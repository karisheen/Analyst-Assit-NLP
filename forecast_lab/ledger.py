"""Append-only forecasts: actual creation clocks, separate evidence classes and resolutions."""

from __future__ import annotations

from datetime import date, timedelta
from urllib.parse import urlparse

from .core import Invalid, digest, now, probability, require, utc
from .facts import chain, ordinal, resolve_values, source_documents
from .protocol import validate
from .store import Store, citation

CLASSES = {"pipeline_development", "retrospective", "prospective"}


def create(store: Store, protocol: dict, request: dict, parent_id: str | None = None) -> str:
    require(
        request,
        {
            "cik",
            "reported_year",
            "reported_quarter",
            "target_year",
            "target_quarter",
            "target_start",
            "target_end",
            "release_at",
            "information_cutoff",
            "evidence_class",
            "document_ids",
            "evidence_for",
            "evidence_against",
            "ambiguous_evidence",
            "missing_evidence",
            "prior_probability",
            "probability",
            "abstained",
            "model_id",
            "config_id",
            "prompt_id",
            "cost_usd",
            "revision_reason",
            "claim",
            "drivers",
            "invalidation",
            "resolution_rule",
        },
    )
    protocol_id = validate(protocol)
    recorded = now()  # Never accepted from input, including retrospective fixture input.
    if "created_at" in request or "recorded_at" in request:
        raise Invalid("Creation timestamp is assigned by the ledger")
    if request["cik"] not in {c["cik"] for c in protocol["cohort"]}:
        raise Invalid("Issuer outside frozen cohort")
    reported = ordinal(request["reported_year"], request["reported_quarter"])
    target = ordinal(request["target_year"], request["target_quarter"])
    if target != reported + 1:
        raise Invalid("Target must be the next issuer fiscal quarter")
    duration = (
        date.fromisoformat(request["target_end"]) - date.fromisoformat(request["target_start"])
    ).days + 1
    if not 77 <= duration <= 105:
        raise Invalid("Irregular target quarter")
    if request["evidence_class"] not in CLASSES:
        raise Invalid("Unknown evidence class")
    cutoff = utc(request["information_cutoff"])
    release = utc(request["release_at"])
    if cutoff > utc(recorded):
        raise Invalid("Cannot create with a future information cutoff")
    if parent_id is None and cutoff != release + timedelta(
        seconds=protocol["timing"]["cutoff_seconds"]
    ):
        raise Invalid("Root cutoff must equal verified release +24 elapsed hours")
    probability(request["prior_probability"], nullable=True)
    probability(request["probability"], nullable=True)
    if type(request["abstained"]) is not bool or request["abstained"] != (
        request["probability"] is None
    ):
        raise Invalid("Abstention must have null probability and vice versa")
    if request["abstained"] and not request["missing_evidence"]:
        raise Invalid("Abstention requires missing evidence/reason")
    from math import isfinite

    if (
        type(request["cost_usd"]) not in (int, float)
        or not isfinite(request["cost_usd"])
        or request["cost_usd"] < 0
    ):
        raise Invalid("Finite nonnegative cost required")
    if not request["document_ids"] or len(set(request["document_ids"])) != len(
        request["document_ids"]
    ):
        raise Invalid("Distinct source documents required")
    docs = [store.get(identity, "document") for identity in request["document_ids"]]
    for doc in docs:
        if doc["cik"] != request["cik"]:
            raise Invalid("Forecast source belongs to another issuer")
        if doc["published_at"] and utc(doc["published_at"]) > cutoff:
            raise Invalid("Source published after cutoff")
        if doc["published_date"] > cutoff.date().isoformat():
            raise Invalid("Source date after cutoff")
        if request["evidence_class"] != "pipeline_development":
            if doc["snapshot_status"] != "verified_original" or doc["version_available_at"] is None:
                raise Invalid("Strict forecasts require verified original byte availability")
            if utc(doc["version_available_at"]) > cutoff:
                raise Invalid("Source version was unavailable at cutoff")
    if request["evidence_class"] != "pipeline_development":
        anchors = [
            doc
            for doc in docs
            if doc["fiscal_year"] == request["reported_year"]
            and doc["fiscal_quarter"] == request["reported_quarter"]
            and not doc["amended"]
            and doc["published_at"] is not None
            and utc(doc["published_at"]) == release
        ]
        if not anchors:
            raise Invalid("Verified earnings release anchor required")
        if any(
            (date.fromisoformat(request["target_start"]) - date.fromisoformat(d["period_end"])).days
            != 1
            for d in anchors
        ):
            raise Invalid("Target fiscal start does not follow reported quarter")
    for key in ("evidence_for", "evidence_against", "ambiguous_evidence"):
        for span_id in request[key]:
            if citation(store, span_id)["document_id"] not in request["document_ids"]:
                raise Invalid("Evidence citation missing from frozen source set")
    if request["resolution_rule"] != protocol["target"]["slowdown"]:
        raise Invalid("Resolution rule differs from protocol")
    feature_provenance = None
    if request["probability"] is not None:
        from .forecasting import validate_prediction

        feature_provenance = validate_prediction(store, protocol, request)
    elif request["model_id"] != "abstention-v1":
        raise Invalid("Unfitted forecast must use explicit abstention identity")
    parent = None
    if parent_id:
        parent = store.get(parent_id, "forecast_event")
        for key in (
            "cik",
            "target_year",
            "target_quarter",
            "reported_year",
            "reported_quarter",
            "target_start",
            "target_end",
            "evidence_class",
            "model_id",
            "release_at",
        ):
            if request[key] != parent[key]:
                raise Invalid(f"Revision changes frozen target/model identity: {key}")
        if parent["protocol_id"] != protocol_id or cutoff < utc(parent["information_cutoff"]):
            raise Invalid("Revision changes protocol or moves cutoff backward")
        if (
            request["prior_probability"] != parent["probability"]
            or not request["revision_reason"].strip()
        ):
            raise Invalid("Revision must link prior belief and give a reason")
        if utc(recorded) <= utc(parent["created_at"]):
            raise Invalid("Revision creation must advance")
    if request["evidence_class"] == "prospective":
        if utc(protocol["frozen_at"]) > cutoff:
            raise Invalid("Protocol was not frozen at cutoff")
        if parent is None and not cutoff <= utc(recorded) <= cutoff + timedelta(
            seconds=protocol["timing"]["creation_tolerance_seconds"]
        ):
            raise Invalid("Missed primary prospective issuance window")
        if parent is not None and cutoff > utc(recorded):
            raise Invalid("Prospective revision cutoff is in the future")
        if date.fromisoformat(request["target_end"]) <= utc(recorded).date():
            raise Invalid("Only still-open target quarters qualify; no unverifiable backfill")
        if any(utc(doc["retrieved_at"]) > cutoff for doc in docs):
            raise Invalid("Prospective sources must have been captured by cutoff")
        if feature_provenance and any(
            utc(store.get(identity, "document")["retrieved_at"]) > cutoff
            for identity in feature_provenance["numeric_sources"]
        ):
            raise Invalid("Prospective numeric sources must have been captured by cutoff")
        check = request.get("unresolved_check")
        if (
            not isinstance(check, dict)
            or not isinstance(check.get("attested_by"), str)
            or not check["attested_by"].strip()
        ):
            raise Invalid("Authoritative unresolved-outcome check required")
        urls = check.get("source_urls")
        if (
            not isinstance(urls, list)
            or not urls
            or any(
                not isinstance(url, str)
                or urlparse(url).scheme != "https"
                or not urlparse(url).hostname
                for url in urls
            )
        ):
            raise Invalid("Authoritative unresolved-outcome check required")
        age = (utc(recorded) - utc(check["checked_at"])).total_seconds()
        if not 0 <= age <= 3600 or check.get("outcome_public") is not False:
            raise Invalid("Outcome check stale or already public")
    root = (parent["root_id"] or parent_id) if parent else None
    payload = {
        **request,
        "protocol_id": protocol_id,
        "created_at": recorded,
        "parent_id": parent_id,
        "root_id": root,
        "primary": parent is None,
        "source_hashes": [d["raw_hash"] for d in docs],
        "features": feature_provenance,
    }
    # Root identity excludes itself; database index supplies the root event ID.
    with store.transaction():
        if parent:
            if store.db.execute("SELECT 1 FROM resolution WHERE root=?", (root,)).fetchone():
                raise Invalid("Cannot revise a resolved forecast")
            if store.db.execute("SELECT 1 FROM forecast WHERE parent=?", (parent_id,)).fetchone():
                raise Invalid("Revision must extend the current tip")
        event_id = store.put("forecast_event", payload)
        actual_root = root or event_id
        store.db.execute(
            "INSERT INTO forecast VALUES (?,?,?,?,?,?,?,?)",
            (
                event_id,
                parent_id,
                actual_root,
                request["cik"],
                f"{request['target_year']}Q{request['target_quarter']}",
                request["model_id"],
                protocol_id,
                request["evidence_class"],
            ),
        )
    return event_id


def revise(store: Store, protocol: dict, parent_id: str, updates: dict) -> str:
    parent = store.get(parent_id, "forecast_event")
    indexed = store.db.execute("SELECT root FROM forecast WHERE id=?", (parent_id,)).fetchone()
    # root_id is null on a root payload to avoid a circular content hash.
    request = {
        k: v
        for k, v in parent.items()
        if k
        not in {"protocol_id", "created_at", "parent_id", "root_id", "primary", "source_hashes"}
        and k != "features"
    }
    request.update(updates)
    request["prior_probability"] = parent["probability"]
    # create resolves actual root through its immutable index.
    if indexed is None:
        raise Invalid("Missing ledger index")
    return create(store, protocol, request, parent_id)


def resolve(store: Store, protocol: dict, forecast_id: str, fact_ids: list[str]) -> str:
    event = store.get(forecast_id, "forecast_event")
    if event["protocol_id"] != validate(protocol):
        raise Invalid("Resolution protocol mismatch")
    root = store.db.execute("SELECT root FROM forecast WHERE id=?", (forecast_id,)).fetchone()[0]
    facts = chain(store, fact_ids, event["cik"], event["reported_year"], event["reported_quarter"])
    cutoff = utc(event["information_cutoff"])
    for offset, fact in facts.items():
        if offset <= 0 and utc(fact["known_at"]) > cutoff:
            raise Invalid("Baseline revenue was unavailable at forecast cutoff")
    values = resolve_values(facts)
    recorded = now()
    if utc(values["outcome_available_at"]) > utc(recorded):
        raise Invalid("Outcome not yet publicly available")
    if utc(values["outcome_available_at"]) <= cutoff:
        raise Invalid("Outcome was already available at forecast cutoff")
    if event["evidence_class"] == "prospective" and utc(values["outcome_available_at"]) <= utc(
        event["created_at"]
    ):
        raise Invalid("Outcome predates prospective creation; integrity violation")
    for fact in facts.values():
        if event["evidence_class"] != "pipeline_development" and any(
            doc["snapshot_status"] != "verified_original"
            for doc in source_documents(store, fact).values()
        ):
            raise Invalid("Non-original outcome cannot resolve a research forecast")
    payload = {
        "root_id": root,
        "protocol_id": validate(protocol),
        "fact_ids": fact_ids,
        **values,
        "recorded_at": recorded,
        "late": utc(values["outcome_available_at"])
        > cutoff + timedelta(days=protocol["resolution"]["deadline_days"]),
    }
    with store.transaction():
        identity = store.put("resolution_event", payload)
        store.db.execute("INSERT INTO resolution VALUES (?,?)", (root, identity))
    return identity


def unresolved(store: Store) -> list[str]:
    return [
        r[0]
        for r in store.db.execute(
            "SELECT f.id FROM forecast f LEFT JOIN resolution r "
            "ON f.root=r.root WHERE r.root IS NULL AND NOT EXISTS "
            "(SELECT 1 FROM forecast child WHERE child.parent=f.id) ORDER BY f.id"
        )
    ]


def verify_ledger(store: Store) -> dict:
    counts = store.verify()
    for (
        identity,
        parent,
        root,
        company,
        quarter,
        model,
        protocol,
        evidence_class,
    ) in store.db.execute("SELECT * FROM forecast").fetchall():
        event = store.get(identity, "forecast_event")
        if (
            event["parent_id"] != parent
            or event["cik"] != company
            or event["model_id"] != model
            or event["protocol_id"] != protocol
            or event["evidence_class"] != evidence_class
        ):
            raise Invalid("Ledger index/payload mismatch")
        if quarter != f"{event['target_year']}Q{event['target_quarter']}":
            raise Invalid("Ledger target index mismatch")
        if parent:
            ancestor = store.get(parent, "forecast_event")
            if (
                utc(event["created_at"]) <= utc(ancestor["created_at"])
                or event["prior_probability"] != ancestor["probability"]
            ):
                raise Invalid("Broken revision lineage")
            expected_root = store.db.execute(
                "SELECT root FROM forecast WHERE id=?", (parent,)
            ).fetchone()[0]
            if root != expected_root:
                raise Invalid("Broken revision root")
        elif root != identity:
            raise Invalid("Broken root index")
        if event["source_hashes"] != [
            store.get(d, "document")["raw_hash"] for d in event["document_ids"]
        ]:
            raise Invalid("Forecast source hash mismatch")
        if event.get("features"):
            for doc_id, raw_hash in event["features"]["numeric_sources"].items():
                if store.get(doc_id, "document")["raw_hash"] != raw_hash:
                    raise Invalid("Forecast numeric source hash mismatch")
    for root, identity in store.db.execute("SELECT root,id FROM resolution").fetchall():
        if store.get(identity, "resolution_event")["root_id"] != root:
            raise Invalid("Resolution index mismatch")
    heads = [
        row[0]
        for row in store.db.execute(
            "SELECT id FROM forecast WHERE id NOT IN "
            "(SELECT parent FROM forecast WHERE parent IS NOT NULL) ORDER BY id"
        )
    ]
    return {
        "counts": counts,
        "heads": heads,
        "head_manifest_hash": digest(heads),
        "unresolved": len(unresolved(store)),
        "limitation": "Local append-only integrity, not external timestamp attestation",
    }
