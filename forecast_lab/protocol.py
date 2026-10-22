"""Frozen protocols are content addressed; existing identities are never rewritten."""

from __future__ import annotations

import re
from pathlib import Path

from .core import Invalid, digest, dump, load, now, require, utc


def validate(protocol: dict) -> str:
    require(
        protocol,
        {
            "version",
            "frozen_at",
            "sector",
            "cohort",
            "target",
            "timing",
            "fiscal",
            "corporate_actions",
            "splits",
            "models",
            "extraction",
            "metrics",
            "minimums",
            "resolution",
            "exclusions",
        },
    )
    utc(protocol["frozen_at"])
    cohort = protocol["cohort"]
    if not 20 <= len(cohort) <= 30:
        raise Invalid("Cohort must contain 20–30 issuers")
    ids = [c["cik"] for c in cohort]
    if len(set(ids)) != len(ids) or any(not re.fullmatch(r"\d{10}", c) for c in ids):
        raise Invalid("CIKs must be unique ten-digit strings")
    if protocol["target"] != {
        "horizon": "next_regular_fiscal_quarter",
        "basis": "original_consolidated_gaap_revenue",
        "growth": "R[q]/R[q-4]-1",
        "slowdown": "g[q+1]<g[q]",
        "ties": 0,
        "unit": "decimal_fraction",
        "arithmetic": "exact_decimal_cross_products",
    }:
        raise Invalid("Unsupported target contract")
    if protocol["timing"]["cutoff_seconds"] != 86400:
        raise Invalid("Unsupported cutoff contract")
    previous = None
    for split in ("train", "calibration", "validation", "holdout"):
        start, end = map(utc, protocol["splits"][split])
        if start >= end or (previous is not None and start < previous):
            raise Invalid("Overlapping or invalid chronological splits")
        previous = end
    if protocol["models"]["numeric_features"] != ["growth_q", "growth_previous"]:
        raise Invalid("Unsupported numeric features")
    if protocol["models"]["text_features"] != [
        "raised",
        "lowered",
        "maintained",
        "initiated",
        "ambiguous",
    ]:
        raise Invalid("Unsupported text features")
    if protocol["models"]["calibration"] != "none":
        raise Invalid("Only preregistered uncalibrated models supported")
    if protocol["extraction"]["task"] != "revenue_guidance_revision":
        raise Invalid("Unsupported extraction task")
    extraction = protocol["extraction"]
    if extraction["version"] == "guidance-v1":
        policy = (0.2, "single_human_unless_second_required_then_consensus")
    elif extraction["version"] == "guidance-v2-single-reviewer":
        policy = (0.0, "single_human_review")
        if extraction.get("reviewer") != "Dakari":
            raise Invalid("Single-reviewer protocol requires designated reviewer Dakari")
    else:
        raise Invalid("Unsupported annotation guide")
    if (extraction["second_review_fraction"], extraction["gold"]) != policy:
        raise Invalid("Annotation guide and review policy differ")
    return digest(protocol)


def freeze(source: str | Path, directory: str | Path) -> str:
    protocol = load(source)
    protocol["frozen_at"] = now()
    identity = validate(protocol)
    target = Path(directory) / f"{identity}.json"
    if target.exists() and load(target) != protocol:
        raise Invalid("Frozen protocol collision")
    if not target.exists():
        dump(target, protocol)
    return identity


def read_protocol(path: str | Path) -> tuple[dict, str]:
    protocol = load(path)
    identity = validate(protocol)
    if Path(path).stem != identity:
        raise Invalid("Protocol filename must match semantic hash; freeze a new identity")
    return protocol, identity


def split_for(protocol: dict, cutoff: str) -> str:
    time = utc(cutoff)
    for name in ("train", "calibration", "validation", "holdout"):
        start, end = map(utc, protocol["splits"][name])
        if start <= time < end:
            return name
    return "excluded_gap_or_outside_window"
