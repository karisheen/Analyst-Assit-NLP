"""One CLI for acquisition, offline replay, review, evaluation and ledger operations."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from . import extraction, forecasting, ledger
from .audit import inspect_forecast, render_text
from .core import Invalid, dump, load
from .facts import import_fact
from .protocol import freeze, read_protocol
from .reproduce import default_protocol, reproduce
from .store import Store, fetch, ingest_manifest

COMMANDS = (
    "reproduce",
    "protocol-freeze",
    "fetch",
    "ingest",
    "candidates",
    "reviews-export",
    "reviews-import",
    "extract-rules",
    "extract-tfidf",
    "llm-requests",
    "llm-import",
    "extraction-evaluate",
    "facts-import",
    "observations-import",
    "fit",
    "evaluate",
    "ledger-create",
    "ledger-inspect",
    "ledger-revise",
    "ledger-list-unresolved",
    "ledger-resolve",
    "ledger-verify",
    "audit",
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Fundamental Forecast Lab — research, not trading")
    result.add_argument("command", choices=COMMANDS)
    result.add_argument("--db", default="research/ledger.sqlite")
    result.add_argument("--protocol")
    result.add_argument("--input", help="JSON input file or fixture manifest")
    result.add_argument("--output", help="Output file (directory for reproduce/protocol-freeze)")
    result.add_argument("--manifest-id")
    result.add_argument("--id", help="Forecast, extraction-run, or fitted-model identity")
    result.add_argument("--split", default="test")
    result.add_argument("--reviews", help="Genuine human review JSON array for reproduction")
    result.add_argument(
        "--llm-responses", help="Actual provider response JSON array for reproduction"
    )
    result.add_argument("--url")
    result.add_argument(
        "--user-agent", help="Identifying live-source User-Agent; never needed offline"
    )
    result.add_argument(
        "--json", action="store_true", help="Machine-readable audit instead of terminal view"
    )
    result.add_argument(
        "--require-evidence",
        action="store_true",
        help="Fail if reproduction lacks final human/financial evidence",
    )
    return result


def needed(value, flag: str):
    if value is None:
        raise Invalid(f"{flag} is required for this command")
    return value


def execute(args: argparse.Namespace):
    command = args.command
    if command == "reproduce":
        report = reproduce(
            args.output or "research/results/sec-single-reviewer",
            args.protocol,
            args.reviews,
            args.llm_responses,
        )
        if args.require_evidence and (
            report["forecasting"]["metrics"] is None
            or report["extraction"]["rules"]["status"] != "EVALUATED"
        ):
            raise Invalid(
                "Evidence gate remains open; artifacts were written with explicit pending statuses"
            )
        return {
            k: report[k]
            for k in (
                "status",
                "protocol_id",
                "documents",
                "companies",
                "candidate_count",
                "human_review_count",
                "prospective_forecasts",
            )
        }
    if command == "protocol-freeze":
        return {
            "protocol_id": freeze(
                needed(args.input, "--input"), args.output or "research/protocols"
            )
        }
    if command == "fetch":
        raw, receipt = fetch(needed(args.url, "--url"), needed(args.user_agent, "--user-agent"))
        target = Path(needed(args.output, "--output"))
        if target.exists():
            raise Invalid("Acquisition never overwrites existing source bytes")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        dump(str(target) + ".receipt.json", receipt)
        return receipt
    protocol, _ = read_protocol(args.protocol or default_protocol())
    store = Store(args.db)
    try:
        if command == "ingest":
            return {
                "document_ids": ingest_manifest(store, needed(args.input, "--input")),
                "integrity": store.verify(),
            }
        if command == "candidates":
            return {"manifest_id": extraction.prepare_candidates(store, protocol)}
        if command in (
            "reviews-export",
            "reviews-import",
            "extract-rules",
            "extract-tfidf",
            "llm-requests",
            "llm-import",
        ):
            manifest = needed(args.manifest_id, "--manifest-id")
            if command == "reviews-export":
                return extraction.review_template(store, manifest)
            if command == "reviews-import":
                return {
                    "review_ids": extraction.import_reviews(
                        store, manifest, load(needed(args.input, "--input"))
                    )
                }
            if command == "extract-rules":
                return {"run_id": extraction.extract_rules(store, manifest)}
            if command == "extract-tfidf":
                return {"run_id": extraction.extract_tfidf(store, manifest)}
            if command == "llm-requests":
                return extraction.llm_requests(store, manifest)
            return {
                "run_id": extraction.import_llm(
                    store, manifest, load(needed(args.input, "--input"))
                )
            }
        if command == "extraction-evaluate":
            return extraction.evaluate_extraction(store, needed(args.id, "--id"), args.split)
        if command == "facts-import":
            return {
                "fact_ids": [import_fact(store, row) for row in load(needed(args.input, "--input"))]
            }
        if command == "observations-import":
            return {
                "observation_ids": [
                    forecasting.import_observation(store, protocol, row)
                    for row in load(needed(args.input, "--input"))
                ]
            }
        if command == "fit":
            return {"fit_id": forecasting.fit_models(store, protocol)}
        if command == "evaluate":
            return forecasting.evaluate(
                store,
                protocol,
                needed(args.id, "--id"),
                args.split if args.split != "test" else "validation",
            )
        if command == "ledger-create":
            return {
                "forecast_id": ledger.create(store, protocol, load(needed(args.input, "--input")))
            }
        if command == "ledger-revise":
            return {
                "forecast_id": ledger.revise(
                    store, protocol, needed(args.id, "--id"), load(needed(args.input, "--input"))
                )
            }
        if command == "ledger-list-unresolved":
            return {"forecast_ids": ledger.unresolved(store)}
        if command == "ledger-resolve":
            return {
                "resolution_id": ledger.resolve(
                    store, protocol, needed(args.id, "--id"), load(needed(args.input, "--input"))
                )
            }
        if command == "ledger-verify":
            return ledger.verify_ledger(store)
        if command in ("ledger-inspect", "audit"):
            view = inspect_forecast(store, needed(args.id, "--id"))
            return view if args.json or command == "ledger-inspect" else render_text(view)
        raise Invalid("Unsupported command")
    finally:
        store.close()


def main() -> int:
    args = parser().parse_args()
    try:
        result = execute(args)
        if args.output and args.command not in ("reproduce", "protocol-freeze", "fetch"):
            if isinstance(result, str):
                Path(args.output).write_text(result + "\n")
            else:
                dump(args.output, result)
        else:
            print(
                result
                if isinstance(result, str)
                else json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
            )
        return 0
    except (Invalid, OSError, KeyError, TypeError, ValueError, sqlite3.Error) as exc:
        print(f"forecast-lab: {exc}", file=sys.stderr)
        return 2
