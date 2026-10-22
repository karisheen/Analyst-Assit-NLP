"""One offline entry path; missing research evidence is reported, never synthesized."""

from __future__ import annotations

import calendar
import shlex
import subprocess
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from .audit import inspect_forecast, render_text
from .core import Invalid, digest, dump, load, now, utc
from .extraction import (
    candidates,
    evaluate_extraction,
    extract_rules,
    extract_tfidf,
    import_llm,
    import_reviews,
    llm_requests,
    prepare_candidates,
    review_template,
)
from .forecasting import evaluate, fit_models
from .ledger import create, revise, verify_ledger
from .protocol import read_protocol
from .store import Store, citation, ingest_manifest


def research_root() -> Path:
    root = Path(__file__).resolve().parent.parent / "research"
    if not (root / "manifest.json").is_file():
        raise Invalid("Fixed-corpus commands require the research assets from a source checkout")
    return root


def default_protocol() -> Path:
    root = research_root()
    manifest = load(root / "manifest.json")
    return root / manifest["protocol_path"]


def fixture_request(store: Store, protocol: dict, doc_id: str) -> dict:
    doc = store.get(doc_id, "document")
    year, q = doc["fiscal_year"], doc["fiscal_quarter"]
    target_year, target_q = (year + 1, 1) if q == 4 else (year, q + 1)
    end = date.fromisoformat(doc["period_end"])
    month = end.month + 3
    target_calendar_year = end.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    target_end = date(
        target_calendar_year, month, calendar.monthrange(target_calendar_year, month)[1]
    )
    release = doc["published_at"]
    if release is None:
        raise Invalid(
            "Fixture forecast requires an asserted release timestamp; "
            "date-only publication and SEC acceptance do not establish the release time"
        )
    cutoff = (utc(release) + timedelta(days=1)).isoformat()
    spans = [
        s["id"]
        for s in store.all("span")
        if citation(store, s["id"])["document_id"] == doc_id
        and "revenue" in citation(store, s["id"])["quote"].lower()
        and "guidance" in citation(store, s["id"])["quote"].lower()
    ]
    return {
        "cik": doc["cik"],
        "reported_year": year,
        "reported_quarter": q,
        "target_year": target_year,
        "target_quarter": target_q,
        "target_start": (end + timedelta(days=1)).isoformat(),
        "target_end": target_end.isoformat(),
        "release_at": release,
        "information_cutoff": cutoff,
        "evidence_class": "pipeline_development",
        "document_ids": [doc_id],
        "evidence_for": [],
        "evidence_against": [],
        "ambiguous_evidence": spans[:2],
        "missing_evidence": [
            "Certified historical original byte availability",
            "Original-vintage revenue training history",
            "Independent human extraction labels",
        ],
        "prior_probability": None,
        "probability": None,
        "abstained": True,
        "model_id": "abstention-v1",
        "config_id": digest(protocol["models"]),
        "prompt_id": None,
        "cost_usd": 0,
        "revision_reason": "Initial development-only abstention; no unsupported numeric probability",
        "claim": "Next-quarter YoY revenue growth is lower than the reported quarter's growth",
        "drivers": ["Stated revenue guidance revision"],
        "invalidation": [
            "Original authoritative revenues do not support slowdown",
            "Unsupported source vintage",
        ],
        "resolution_rule": protocol["target"]["slowdown"],
    }


def calibration_svg(report: dict) -> str:
    header = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="700" height="450" viewBox="0 0 700 450">'
    )
    if report["metrics"] is None:
        return (
            header
            + '<rect width="700" height="450" fill="white"/><text x="30" y="100" font-size="20">Calibration unavailable: no eligible resolved forecasts</text><text x="30" y="145" font-size="16">Fixture correctness is not forecasting evidence.</text></svg>'
        )
    body = [
        '<rect width="700" height="450" fill="white"/>',
        '<path d="M60 380 L410 30 M60 30 V380 H410" stroke="gray" fill="none"/>',
    ]
    colors = {"A": "black", "B": "blue", "C": "orange", "D": "green"}
    for name, metrics in report["metrics"].items():
        body.append(
            f'<text x="470" y="{50 + 25 * list(colors).index(name)}" fill="{colors[name]}">{name}</text>'
        )
        for b in metrics["calibration"]:
            if b["count"]:
                x, y = 60 + 350 * b["predicted"], 380 - 350 * b["observed"]
                body.append(
                    f'<circle cx="{x}" cy="{y}" r="5" fill="{colors[name]}"><title>n={b["count"]}</title></circle>'
                )
    body.append(
        '<text x="60" y="420">Predicted probability; vertical axis observed frequency (0–1)</text>'
    )
    return header + "".join(body) + "</svg>"


def reproduce(
    output: str | Path,
    protocol_path: str | Path | None = None,
    reviews: str | Path | None = None,
    llm_responses: str | Path | None = None,
) -> dict:
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    protocol_path = Path(protocol_path) if protocol_path else default_protocol()
    protocol, protocol_id = read_protocol(protocol_path)
    fixture_path = research_root() / "fixtures/manifest.json"
    manifest = load(fixture_path)
    source_files = sorted(Path(__file__).parent.glob("*.py"))
    source_tree_hash = digest(
        {f"forecast_lab/{p.name}": digest(p.read_text()) for p in source_files}
    )
    marker = output / "run-contract.json"
    contract = {
        "purpose": "offline_fixture_only",
        "protocol_id": protocol_id,
        "source_data_id": digest(manifest),
        "source_tree_hash": source_tree_hash,
    }
    if marker.exists() and load(marker) != contract:
        raise Invalid("Output contract differs; preserve this run and use a fresh output directory")
    if not marker.exists() and (output / "fixture.sqlite").exists():
        raise Invalid("Refusing to use an unrecognized existing database")
    dump(marker, contract)
    store = Store(output / "fixture.sqlite")
    try:
        doc_ids = ingest_manifest(store, fixture_path)
        if {d["id"] for d in store.all("document")} != set(doc_ids):
            raise Invalid("Fixture database contains sources outside its frozen corpus")
        verified = store.verify()
        provenance = {
            kind: verified.get(kind, 0) for kind in ("document", "retrieval", "parse", "span")
        }
        candidate_manifest = prepare_candidates(store, protocol)
        if reviews:
            import_reviews(store, candidate_manifest, load(reviews))
        rule_run = extract_rules(store, candidate_manifest)
        text_run = extract_tfidf(store, candidate_manifest)
        rule_metrics = evaluate_extraction(store, rule_run)
        text_metrics = evaluate_extraction(store, text_run)
        if llm_responses:
            import_llm(store, candidate_manifest, load(llm_responses))
        llm_runs = [
            r
            for r in store.all("extraction_run")
            if r["manifest_id"] == candidate_manifest and r["method"] == "llm-external-v1"
        ]
        llm_metrics = {
            "status": "RUNS_AVAILABLE" if llm_runs else "NOT_RUN",
            "evaluations": [evaluate_extraction(store, r["id"]) for r in llm_runs],
            "reason": None if llm_runs else "No actual provider responses supplied",
        }
        fit_id = fit_models(store, protocol)
        forecast_report = evaluate(store, protocol, fit_id)
        eligible_docs = [d for d in doc_ids if store.get(d, "document")["published_at"]]
        if not eligible_docs:
            raise Invalid("Fixture has no asserted release timestamp for development replay")
        request = fixture_request(store, protocol, eligible_docs[0])
        root_row = store.db.execute(
            "SELECT id FROM forecast WHERE parent IS NULL AND company=? AND quarter=? AND model=? AND protocol=? AND evidence_class=?",
            (
                request["cik"],
                f"{request['target_year']}Q{request['target_quarter']}",
                "abstention-v1",
                protocol_id,
                "pipeline_development",
            ),
        ).fetchone()
        root = root_row[0] if root_row else create(store, protocol, request)
        child = store.db.execute("SELECT id FROM forecast WHERE parent=?", (root,)).fetchone()
        revision = (
            child[0]
            if child
            else revise(
                store,
                protocol,
                root,
                {
                    "revision_reason": "Provenance audit confirms reconstructed bytes; maintain abstention",
                    "missing_evidence": request["missing_evidence"]
                    + ["Next-period original revenue resolution"],
                },
            )
        )
        ledger = verify_ledger(store)
        view = inspect_forecast(store, revision)
        candidate_rows = candidates(store, candidate_manifest)
        report = {
            "protocol_id": protocol_id,
            "source_data_id": digest(manifest),
            "evidence_class": "retrospective_pipeline_development",
            "documents": len(doc_ids),
            "companies": len({store.get(d, "document")["cik"] for d in doc_ids}),
            "provenance": provenance,
            "candidate_manifest_id": candidate_manifest,
            "candidate_count": len(candidate_rows),
            "candidate_splits": dict(Counter(c["split"] for c in candidate_rows)),
            "candidate_strata": dict(Counter(c["stratum"] for c in candidate_rows)),
            "second_review_count": sum(c["second_review_required"] for c in candidate_rows),
            "annotation_policy": {
                key: protocol["extraction"].get(key)
                for key in ("version", "gold", "reviewer", "second_review_fraction")
            },
            "human_review_count": len(store.all("review")),
            "extraction": {
                "rules": rule_metrics,
                "tfidf": text_metrics,
                "llm": llm_metrics,
            },
            "forecasting": forecast_report,
            "prospective_forecasts": 0,
            "prospective_blocker": "No verified original current issuance bundle or original-vintage training sample in fixture",
            "status": "ENGINEERING_SLICE_WITH_HUMAN_AND_SOURCE_EVIDENCE_GATES",
        }
        for name, value in (
            ("report.json", report),
            ("annotations.json", review_template(store, candidate_manifest)),
            ("llm-requests.json", llm_requests(store, candidate_manifest)),
            ("extraction-rules.json", store.get(rule_run)),
            ("extraction-tfidf.json", store.get(text_run)),
            ("forecasting.json", forecast_report),
            ("ledger-integrity.json", ledger),
            ("audit.json", view),
        ):
            dump(output / name, value)
        (output / "audit.txt").write_text(render_text(view) + "\n")
        (output / "calibration.svg").write_text(calibration_svg(forecast_report) + "\n")
        (output / "report.md").write_text(
            f"# Fixed-corpus development report\n\nProtocol `{protocol_id}`.\n\n"
            f"{len(doc_ids)} documents, {report['companies']} companies, {len(candidate_rows)} unique annotation candidates; "
            f"{report['human_review_count']} review records.\n\n"
            f"Annotation policy: **{protocol['extraction']['gold']}**; "
            f"designated reviewer: {protocol['extraction'].get('reviewer') or 'not designated'}. "
            "Single-reviewer labels do not measure independent inter-annotator agreement.\n\n"
            "Bundled disclosures are historical reconstructions, not certified release-time bytes. "
            "Publication assertions and SEC acceptance timestamps do not certify historical bytes. "
            f"Rule evaluation: **{rule_metrics['status']}**, {rule_metrics['gold_count']} reviewed test candidates. "
            f"LLM: **{llm_metrics['status']}**. Exact citation identity does not establish semantic support. "
            "TF-IDF and detailed extraction metrics/statuses are in report.json.\n\n"
            f"Forecast comparison: **{forecast_report['status']}**. No business-outcome performance claim. "
            "No synthetic returns, verbal confidence probabilities, or backdated prospective records.\n\n"
            "The immutable development ledger contains an abstention and a linked revision. "
            "No useful-revision/overreaction empirical example can be identified without legitimate resolved evidence.\n\n"
            "See annotations.json for human work, audit.txt for exact passages/provenance, forecasting.json for counts, "
            "and calibration.svg for the explicit unavailable-evidence panel.\n"
        )
        revision_result = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parent.parent), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        command = [
            "python",
            "-m",
            "forecast_lab",
            "reproduce",
            "--output",
            str(output),
            "--protocol",
            str(protocol_path),
        ]
        inputs = {"protocol": {"path": str(protocol_path), "identity": protocol_id}}
        for flag, path in (("reviews", reviews), ("llm-responses", llm_responses)):
            if path is not None:
                command.extend([f"--{flag}", str(path)])
                inputs[flag] = {"path": str(path), "identity": digest(load(path))}
        execution = {
            "recorded_at": now(),
            "source_revision": revision_result.stdout.strip() or None,
            "source_tree_hash": source_tree_hash,
            "command": shlex.join(command),
            "inputs": inputs,
            "review_ids": sorted(r["id"] for r in store.all("review")),
            "llm_run_ids": [r["id"] for r in llm_runs],
            "protocol_id": protocol_id,
            "source_data_id": report["source_data_id"],
            "scientific_result_id": digest(report),
            "ledger_head_manifest_hash": ledger["head_manifest_hash"],
            "artifacts": sorted(p.name for p in output.iterdir() if p.is_file()),
            "limitations": [
                "uncommitted source hash supplements Git revision",
                "runtime creation timestamps intentionally not deterministic",
                "review and LLM artifact IDs include any preceding explicit CLI imports into this database",
                f"human review records: {report['human_review_count']}; LLM runs: {len(llm_runs)}",
                "no historical original-byte certification, no prospective outcomes",
            ],
        }
        dump(output / "execution-manifest.json", execution)
        return report
    finally:
        store.close()
