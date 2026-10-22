"""Small immutable SQLite artifact store with exact byte and citation provenance."""

from __future__ import annotations

import io
import json
import re
import sqlite3
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .core import Invalid, canonical, digest, load, now, require, sha, utc

SCHEMA = """
CREATE TABLE IF NOT EXISTS artifact (
 kind TEXT NOT NULL, id TEXT PRIMARY KEY, payload TEXT NOT NULL,
 UNIQUE(kind,id)
);
CREATE TABLE IF NOT EXISTS raw (hash TEXT PRIMARY KEY, content BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS forecast (
 id TEXT PRIMARY KEY REFERENCES artifact(id), parent TEXT UNIQUE REFERENCES forecast(id),
 root TEXT NOT NULL, company TEXT NOT NULL, quarter TEXT NOT NULL, model TEXT NOT NULL,
 protocol TEXT NOT NULL, evidence_class TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS unique_root ON forecast(company,quarter,model,protocol,evidence_class)
 WHERE parent IS NULL;
CREATE TABLE IF NOT EXISTS resolution (
 root TEXT PRIMARY KEY REFERENCES forecast(id), id TEXT UNIQUE NOT NULL REFERENCES artifact(id)
);
"""


class Store:
    def __init__(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(SCHEMA)
        for table in ("artifact", "raw", "forecast", "resolution"):
            for action in ("UPDATE", "DELETE"):
                self.db.execute(
                    f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} "
                    f"BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'immutable'); END"
                )
        self.db.commit()

    def close(self) -> None:
        self.db.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        if self.db.in_transaction:
            raise Invalid("Nested transaction not permitted")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def put(self, kind: str, payload: dict) -> str:
        identity = digest({"kind": kind, "payload": payload})
        self.db.execute(
            "INSERT OR IGNORE INTO artifact VALUES (?,?,?)", (kind, identity, canonical(payload))
        )
        return identity

    def get(self, identity: str, kind: str | None = None) -> dict:
        row = self.db.execute(
            "SELECT kind,payload FROM artifact WHERE id=?", (identity,)
        ).fetchone()
        if row is None or (kind is not None and row[0] != kind):
            raise Invalid(f"Unknown {kind or 'artifact'}: {identity}")
        payload = json.loads(row[1])
        if digest({"kind": row[0], "payload": payload}) != identity:
            raise Invalid("Artifact integrity failure")
        return payload

    def all(self, kind: str) -> list[dict]:
        return [
            {"id": row[0], **self.get(row[0], kind)}
            for row in self.db.execute(
                "SELECT id FROM artifact WHERE kind=? ORDER BY id", (kind,)
            ).fetchall()
        ]

    def raw(self, hash_: str) -> bytes:
        row = self.db.execute("SELECT content FROM raw WHERE hash=?", (hash_,)).fetchone()
        if row is None or sha(row[0]) != hash_:
            raise Invalid("Raw content missing or hash mismatch")
        return row[0]

    def verify(self) -> dict:
        counts: dict[str, int] = {}
        for kind, identity in self.db.execute("SELECT kind,id FROM artifact").fetchall():
            self.get(identity, kind)
            counts[kind] = counts.get(kind, 0) + 1
        for (hash_,) in self.db.execute("SELECT hash FROM raw").fetchall():
            self.raw(hash_)
        for doc in self.all("document"):
            self.raw(doc["raw_hash"])
        for parsed in self.all("parse"):
            self.get(parsed["document_id"], "document")
            if sha(parsed["text"].encode()) != parsed["text_hash"]:
                raise Invalid("Parsed text corruption")
        for span in self.all("span"):
            citation(self, span["id"])
        return counts


class Blocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in ("script", "style", "nav", "footer", "header"):
            self.skip += 1
        if not self.skip and tag in ("p", "div", "tr", "li", "h1", "h2", "h3", "br"):
            self.parts.append("\n")
        if not self.skip and tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "nav", "footer", "header"):
            self.skip = max(0, self.skip - 1)
        if not self.skip and tag in ("p", "div", "tr", "li"):
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def parse_document(raw: bytes, metadata: dict) -> tuple[str, str]:
    anchors = metadata["expected_text"]
    if (
        not isinstance(anchors, list)
        or not anchors
        or any(not isinstance(anchor, str) or not anchor.strip() for anchor in anchors)
    ):
        raise Invalid("Nonempty source identity anchors required")
    kind = metadata["media_type"]
    if kind == "application/pdf":
        from pypdf import PdfReader

        if not raw.startswith(b"%PDF-"):
            raise Invalid("Not PDF bytes")
        try:
            pages = PdfReader(io.BytesIO(raw)).pages
            text = "\n\n".join(page.extract_text(extraction_mode="layout") for page in pages)
        except Exception as exc:
            raise Invalid("Unreadable PDF") from exc
        parser = "pypdf-6.1.1-layout-v1"
    elif kind == "text/html":
        html = raw.decode("utf-8", errors="strict")
        selector = metadata.get("article_bounds")
        if not selector or len(selector) != 2:
            raise Invalid("HTML requires explicit article start/end delimiters")
        start, end = selector
        if html.count(start) != 1 or end not in html.split(start, 1)[1]:
            raise Invalid("Article boundaries not found uniquely")
        body = html.split(start, 1)[1].split(end, 1)[0]
        parser_obj = Blocks()
        parser_obj.feed(body)
        text = "".join(parser_obj.parts)
        parser = "html-blocks-v1"
    elif kind == "text/plain":
        text = raw.decode("utf-8", errors="strict")
        parser = "utf8-blocks-v1"
    elif kind == "application/json":
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise Invalid("SEC metadata must be a JSON object")
        text = canonical(parsed)
        parser = "canonical-json-v1"
    else:
        raise Invalid("Unsupported media type")
    text = "\n".join(re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines())
    if len(text.strip()) < 80 or "access denied" in text[:200].lower():
        raise Invalid("Empty, blocked or metadata-only disclosure")
    for anchor in metadata["expected_text"]:
        if anchor.casefold() not in text.casefold():
            raise Invalid(f"Source identity mismatch: missing {anchor!r}")
    return text, parser


def ingest(store: Store, raw: bytes, metadata: dict) -> str:
    require(
        metadata,
        {
            "cik",
            "ticker",
            "source_id",
            "source_url",
            "form",
            "period_end",
            "fiscal_year",
            "fiscal_quarter",
            "retrieved_at",
            "published_at",
            "published_date",
            "availability_evidence",
            "version_available_at",
            "snapshot_status",
            "amended",
            "media_type",
            "expected_text",
            "raw_hash",
        },
    )
    if not re.fullmatch(r"\d{10}", metadata["cik"]) or metadata["fiscal_quarter"] not in (
        1,
        2,
        3,
        4,
    ):
        raise Invalid("Invalid issuer or fiscal quarter")
    if urlparse(metadata["source_url"]).scheme != "https":
        raise Invalid("Source must retain an HTTPS authoritative URL")
    retrieved = utc(metadata["retrieved_at"])
    if metadata["published_at"] is not None:
        if utc(metadata["published_at"]) > retrieved:
            raise Invalid("Publication after retrieval")
    if metadata["snapshot_status"] not in (
        "historical_reconstruction",
        "verified_original",
        "synthetic",
    ):
        raise Invalid("Unknown snapshot status")
    available = metadata["version_available_at"]
    if available is not None and utc(available) > retrieved:
        raise Invalid("Version availability after retrieval")
    if metadata["snapshot_status"] == "historical_reconstruction" and available is not None:
        raise Invalid("Reconstructed current bytes cannot be backdated")
    if metadata["snapshot_status"] == "verified_original" and (
        available is None or not metadata["availability_evidence"]
    ):
        raise Invalid("Verified originals require availability evidence")
    if sha(raw) != metadata["raw_hash"]:
        raise Invalid("Manifest raw hash mismatch")
    parent = metadata.get("supersedes")
    if parent:
        previous = store.get(parent, "document")
        if previous["cik"] != metadata["cik"] or previous["period_end"] != metadata["period_end"]:
            raise Invalid("Amendment lineage must preserve issuer and period")
        if retrieved < utc(previous["retrieved_at"]):
            raise Invalid("Revision retrieval cannot precede original")
        for field in ("published_at", "version_available_at"):
            if (
                previous[field] is not None
                and metadata[field] is not None
                and utc(metadata[field]) < utc(previous[field])
            ):
                raise Invalid("Superseding source availability cannot precede its parent")
    existing = [
        doc
        for doc in store.all("document")
        if doc["cik"] == metadata["cik"]
        and doc["source_id"] == metadata["source_id"]
        and doc["raw_hash"] == metadata["raw_hash"]
    ]
    if existing:
        previous = existing[0]
        observation_fields = {"id", "retrieved_at", "final_url"}
        old_semantics = {k: v for k, v in previous.items() if k not in observation_fields}
        new_semantics = {k: v for k, v in metadata.items() if k not in observation_fields}
        if old_semantics != new_semantics:
            raise Invalid(
                "Conflicting metadata for identical source bytes; preserve a separately identified adjudication"
            )
        if retrieved < utc(previous["retrieved_at"]):
            raise Invalid("A later import cannot backdate the first retrieval")
        with store.transaction():
            store.put(
                "retrieval",
                {
                    "document_id": previous["id"],
                    "retrieved_at": metadata["retrieved_at"],
                    "source_url": metadata["source_url"],
                },
            )
        return previous["id"]
    versions = [
        doc
        for doc in store.all("document")
        if doc["cik"] == metadata["cik"] and doc["source_id"] == metadata["source_id"]
    ]
    if versions and parent not in {doc["id"] for doc in versions}:
        raise Invalid("Changed source bytes require explicit supersedes lineage")
    text, parser = parse_document(raw, metadata)
    with store.transaction():
        store.db.execute("INSERT OR IGNORE INTO raw VALUES (?,?)", (sha(raw), raw))
        doc_id = store.put("document", metadata)
        store.put(
            "retrieval",
            {
                "document_id": doc_id,
                "retrieved_at": metadata["retrieved_at"],
                "source_url": metadata["source_url"],
            },
        )
        parse_id = store.put(
            "parse",
            {
                "document_id": doc_id,
                "parser": parser,
                "text": text,
                "text_hash": sha(text.encode()),
            },
        )
        # Blank-line paragraphs preserve table blocks rather than pretending cells are prose.
        for match in re.finditer(r"\S(?:.*?\S)?(?=\n\s*\n|\Z)", text, flags=re.S):
            store.put(
                "span",
                {
                    "parse_id": parse_id,
                    "start": match.start(),
                    "end": match.end(),
                    "quote_hash": sha(match.group().encode()),
                },
            )
    return doc_id


def ingest_manifest(store: Store, path: str | Path) -> list[str]:
    manifest = load(path)
    documents = manifest["documents"]
    result = []
    for entry in documents:
        metadata = {k: v for k, v in entry.items() if k != "path"}
        file = (Path(path).parent / entry["path"]).resolve()
        if not file.is_relative_to(Path(path).parent.resolve()):
            raise Invalid("Fixture path escapes manifest directory")
        result.append(ingest(store, file.read_bytes(), metadata))
    return result


def citation(store: Store, span_id: str) -> dict:
    span = store.get(span_id, "span")
    parsed = store.get(span["parse_id"], "parse")
    doc = store.get(parsed["document_id"], "document")
    if not 0 <= span["start"] < span["end"] <= len(parsed["text"]):
        raise Invalid("Span outside parsed text")
    quote = parsed["text"][span["start"] : span["end"]]
    if sha(quote.encode()) != span["quote_hash"]:
        raise Invalid("Citation quote hash mismatch")
    return {
        "span_id": span_id,
        "document_id": parsed["document_id"],
        "raw_hash": doc["raw_hash"],
        "parse_id": span["parse_id"],
        "text_hash": parsed["text_hash"],
        "start": span["start"],
        "end": span["end"],
        "quote": quote,
        "source_url": doc["source_url"],
        "source_id": doc["source_id"],
        "available_at": doc["version_available_at"],
        "published_at": doc["published_at"],
        "retrieved_at": doc["retrieved_at"],
        "snapshot_status": doc["snapshot_status"],
    }


def fetch(url: str, user_agent: str) -> tuple[bytes, dict]:
    """Explicit acquisition only; fixture reproduction never calls this function."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or not user_agent.strip():
        raise Invalid("HTTPS URL and identifying user agent required")
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=30) as response:
        raw = response.read(10_000_001)
        if len(raw) > 10_000_000:
            raise Invalid("Document exceeds 10 MB acquisition limit")
        return raw, {
            "requested_url": url,
            "final_url": response.url,
            "retrieved_at": now(),
            "raw_hash": sha(raw),
            "http_status": response.status,
            "content_type": response.headers.get_content_type(),
        }
