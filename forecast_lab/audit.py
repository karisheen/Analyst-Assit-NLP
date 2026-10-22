"""Read-only reviewer surface over verified ledger/source records."""

from __future__ import annotations

import math

from .core import Invalid
from .facts import source_documents
from .ledger import verify_ledger
from .store import Store, citation


def fact_view(store: Store, identity: str) -> dict:
    fact = store.get(identity, "fact")
    operands = fact.get("derivation")
    sources = [operands["annual"], operands["nine_month"]] if operands else [fact]
    spans = sorted(
        {s["span_id"] for s in sources} | {s["unit_support"]["span_id"] for s in sources}
    )
    return {
        "fact_id": identity,
        "fact": fact,
        "citations": [citation(store, span) for span in spans],
        "sources": [{"id": key, **doc} for key, doc in source_documents(store, fact).items()],
    }


def inspect_forecast(store: Store, forecast_id: str) -> dict:
    verify_ledger(store)
    event = store.get(forecast_id, "forecast_event")
    indexed = store.db.execute("SELECT root FROM forecast WHERE id=?", (forecast_id,)).fetchone()
    if indexed is None:
        raise Invalid("Forecast event has no ledger index")
    root = indexed[0]
    lineage = []
    cursor = forecast_id
    while cursor:
        row = store.get(cursor, "forecast_event")
        lineage.append({"id": cursor, **row})
        cursor = row["parent_id"]
    resolution_row = store.db.execute("SELECT id FROM resolution WHERE root=?", (root,)).fetchone()
    resolution = (
        {"id": resolution_row[0], **store.get(resolution_row[0], "resolution_event")}
        if resolution_row
        else None
    )
    scores = None
    if resolution is not None and event["probability"] is not None:
        p = event["probability"]
        y = resolution["label"]
        bounded = min(1 - 1e-6, max(1e-6, p))
        scores = {
            "brier": (p - y) ** 2,
            "log_loss": -(y * math.log(bounded) + (1 - y) * math.log1p(-bounded)),
            "primary": event["primary"],
            "late_resolution": resolution["late"],
        }
    evidence = {
        key: [citation(store, s) for s in event[key]]
        for key in ("evidence_for", "evidence_against", "ambiguous_evidence")
    }
    return {
        "forecast_id": forecast_id,
        "root_id": root,
        "forecast": event,
        "evidence": evidence,
        "sources": [{"id": d, **store.get(d, "document")} for d in event["document_ids"]],
        "feature_facts": [fact_view(store, f) for f in event.get("feature_fact_ids", [])],
        "resolution_facts": [fact_view(store, f) for f in resolution["fact_ids"]]
        if resolution
        else [],
        "revision_history": list(reversed(lineage)),
        "resolution": resolution,
        "score": scores,
        "status": "UNRESOLVED" if resolution is None else "RESOLVED",
        "warning": {
            "pipeline_development": "Development example, not prospective evidence.",
            "retrospective": "Retrospective reconstruction, not prospective evidence.",
            "prospective": "Prospective record; unresolved outcomes are not measured performance.",
        }[event["evidence_class"]]
        + " Local integrity is not external attestation.",
    }


def render_text(view: dict) -> str:
    f = view["forecast"]
    lines = [
        f"Forecast {view['forecast_id']}",
        f"Class: {f['evidence_class']} | {view['status']}",
        f"Issuer {f['cik']} | target {f['target_year']}Q{f['target_quarter']}",
        f"Created: {f['created_at']} | cutoff: {f['information_cutoff']}",
        f"Prior: {f['prior_probability']} | current: {f['probability']} | abstained: {f['abstained']}",
        f"Model: {f['model_id']} | config: {f['config_id']} | prompt: {f['prompt_id']}",
        f"Protocol: {f['protocol_id']} | inference cost USD: {f['cost_usd']}",
        f"Claim: {f['claim']}",
        f"Drivers: {f['drivers']}",
        f"Invalidation: {f['invalidation']}",
        f"Missing evidence: {f['missing_evidence']}",
    ]
    for category, items in view["evidence"].items():
        lines.append(category + ":")
        for c in items:
            lines.extend(
                [
                    f"  {c['quote']}",
                    f"  source={c['source_url']} | source_id={c['source_id']}",
                    f"  sha256={c['raw_hash']} | span={c['span_id']} | offsets={c['start']}:{c['end']}",
                    f"  published={c['published_at']} | verified_available={c['available_at']} | retrieved={c['retrieved_at']}",
                ]
            )
    for category in ("feature_facts", "resolution_facts"):
        lines.append(category + ":")
        for item in view[category]:
            lines.append(f"  fact={item['fact_id']} | known_at={item['fact']['known_at']}")
            for c in item["citations"]:
                lines.extend(
                    [
                        f"  {c['quote']}",
                        f"  source={c['source_id']} | sha256={c['raw_hash']} | span={c['span_id']}",
                        f"  available={c['available_at']} | offsets={c['start']}:{c['end']}",
                    ]
                )
    lines.append("Revisions:")
    lines.extend(
        f"  {r['id']} | {r['created_at']} | {r['revision_reason']}"
        for r in view["revision_history"]
    )
    lines.extend([f"Resolution: {view['resolution']}", f"Score: {view['score']}", view["warning"]])
    # Do not let external document controls become terminal escape sequences.
    return "\n".join(
        "".join(
            c if c in "\n\t" or ord(c) >= 32 and ord(c) != 127 else f"\\x{ord(c):02x}" for c in line
        )
        for line in lines
    )
