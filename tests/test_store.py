import sqlite3

import pytest

from forecast_lab.core import Invalid, sha
from forecast_lab.store import Store, citation, ingest


def metadata(raw, **updates):
    row = dict(
        cik="0001108524",
        ticker="CRM",
        source_id="release-1",
        source_url="https://example.com/release",
        form="8-K/EX-99.1",
        period_end="2024-04-30",
        fiscal_year=2025,
        fiscal_quarter=1,
        retrieved_at="2024-05-30T00:00:00Z",
        published_at="2024-05-29T20:00:00Z",
        published_date="2024-05-29",
        availability_evidence="synthetic test receipt",
        version_available_at="2024-05-29T20:00:00Z",
        snapshot_status="synthetic",
        amended=False,
        media_type="text/plain",
        expected_text=["revenue"],
        raw_hash=sha(raw),
    )
    return {**row, **updates}


RAW = b"Company revenue statement with sufficient contextual evidence for deterministic parser tests.\n\nThe company raises full year FY2025 revenue guidance to a new expected range."


def test_idempotency_amendments_and_exact_citations(tmp_path):
    s = Store(tmp_path / "source.db")
    original = ingest(s, RAW, metadata(RAW))
    assert ingest(s, RAW, metadata(RAW)) == original
    assert ingest(s, RAW, metadata(RAW, retrieved_at="2024-06-01T00:00:00Z")) == original
    assert len(s.all("retrieval")) == 2
    assert s.get(original)["retrieved_at"] == "2024-05-30T00:00:00Z"
    span = s.all("span")[0]
    quoted = citation(s, span["id"])
    assert quoted["quote"].encode() in RAW
    amended = RAW.replace(b"raises", b"lowers")
    new = ingest(
        s,
        amended,
        metadata(amended, amended=True, supersedes=original, source_id="release-amendment"),
    )
    assert new != original
    assert s.raw(s.get(original)["raw_hash"]) == RAW
    assert len(s.all("document")) == 2
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        s.db.execute("DELETE FROM artifact")
    s.db.rollback()
    assert s.verify()["span"] == 4


def test_fail_closed_metadata_and_sources(tmp_path):
    s = Store(tmp_path / "source.db")
    for data in [
        metadata(RAW, raw_hash="0" * 64),
        metadata(RAW, retrieved_at="2024-01-01"),
        metadata(RAW, expected_text=["wrong company"]),
        metadata(RAW, snapshot_status="historical_reconstruction"),
    ]:
        with pytest.raises(Invalid):
            ingest(s, RAW, data)
    with pytest.raises(Invalid):
        ingest(s, b"access denied", metadata(b"access denied"))
    assert not s.all("document")


def test_retrieval_conflicts_and_changed_bytes_require_lineage(tmp_path):
    store = Store(tmp_path / "revisions.db")
    original = ingest(store, RAW, metadata(RAW))
    for updates in (
        {"retrieved_at": "2024-05-29T21:00:00Z"},
        {"period_end": "2024-03-31"},
        {"version_available_at": "2024-05-29T19:00:00Z"},
    ):
        with pytest.raises(Invalid):
            ingest(store, RAW, metadata(RAW, **updates))
    changed = RAW.replace(b"raises", b"lowers")
    with pytest.raises(Invalid, match="lineage"):
        ingest(store, changed, metadata(changed))
    revision = ingest(store, changed, metadata(changed, supersedes=original))
    assert store.get(revision)["supersedes"] == original
    assert store.raw(store.get(original)["raw_hash"]) == RAW


@pytest.mark.parametrize("anchors", [[], [""], [" "], "revenue", [42]])
def test_empty_or_malformed_source_anchors_fail_closed(tmp_path, anchors):
    store = Store(tmp_path / "anchors.db")
    with pytest.raises(Invalid, match="anchors"):
        ingest(store, RAW, metadata(RAW, expected_text=anchors))
    assert store.all("document") == []


@pytest.mark.parametrize("field", ["published_at", "version_available_at"])
def test_revised_source_clocks_cannot_regress(tmp_path, field):
    store = Store(tmp_path / "clock.db")
    original = ingest(store, RAW, metadata(RAW))
    changed = RAW.replace(b"raises", b"lowers")
    with pytest.raises(Invalid, match="availability"):
        ingest(
            store,
            changed,
            metadata(changed, supersedes=original, **{field: "2024-05-28T00:00:00Z"}),
        )
    assert len(store.all("document")) == 1
