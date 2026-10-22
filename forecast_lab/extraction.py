"""One task: stated revenue-guidance revision, not sentiment or future revenue outcomes."""

from __future__ import annotations

import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .core import Invalid, digest, now, require, sha, utc
from .store import Store, citation

LABELS = ("RAISED", "LOWERED", "MAINTAINED", "INITIATED", "NO_GUIDANCE", "AMBIGUOUS")
DIRECTIONS = {
    "RAISED": r"\b(?:raises?|raised|raising|increases?|increased)\b",
    "LOWERED": r"\b(?:lowers?|lowered|lowering|reduces?|reduced)\b",
    "MAINTAINED": r"\b(?:reiterates?|reiterated|maintains?|maintained|reaffirms?|reaffirmed)\b",
    "INITIATED": r"\b(?:initiates?|initiated|initiating)\b",
}
HORIZON = r"(?:Q[1-4]\s*(?:FY)?\s*\d{2,4}|(?:first|second|third|fourth|next)\s+quarter(?:\s+(?:FY|fiscal)?\s*\d{2,4})?|(?:full[ -]year|fiscal\s+year|FY)\s*\d{2,4})"


def prepare_candidates(store: Store, protocol: dict) -> str:
    protocol_id = digest(protocol)
    extraction = protocol["extraction"]
    target = extraction["candidate_target"]
    options = []
    seen = set()
    for span in store.all("span"):
        cite = citation(store, span["id"])
        doc = store.get(cite["document_id"], "document")
        text = cite["quote"]
        normalized = re.sub(r"\s+", " ", text).casefold()
        if len(text) < 60 or normalized in seen or doc["media_type"] == "application/json":
            continue
        seen.add(normalized)
        low = text.lower()
        if "revenue" in low and any(re.search(p, low) for p in DIRECTIONS.values()):
            stratum = "directional_candidate"
        elif "guidance" in low and re.search(r"\d", low):
            stratum = "numeric_guidance"
        elif "\n" in text and len(re.findall(r"\d", text)) > 8:
            stratum = "table_context"
        elif any(w in low for w in ("uncertain", "may ", "could ", "expect")):
            stratum = "ambiguity_candidate"
        elif "guidance" in low or "outlook" in low:
            stratum = "outlook_candidate"
        else:
            stratum = "difficult_negative_candidate"
        group = f"{doc['cik']}:{doc['fiscal_year']}Q{doc['fiscal_quarter']}"
        options.append(
            {
                "span_id": span["id"],
                "group": group,
                "cik": doc["cik"],
                "date": doc["published_date"],
                "stratum": stratum,
                "text_hash": digest(normalized),
            }
        )
    # Balanced deterministic search strata, never label-based sampling.
    buckets: dict[str, list[dict]] = {}
    for row in options:
        buckets.setdefault(row["stratum"], []).append(row)
    for rows in buckets.values():
        rows.sort(key=digest)
    selected: list[dict] = []
    while buckets and len(selected) < target:
        for key in sorted(list(buckets)):
            if len(selected) == target:
                break
            selected.append(buckets[key].pop(0))
            if not buckets[key]:
                del buckets[key]
    groups = sorted({(r["date"], r["group"]) for r in selected})
    group_index = {group: i for i, (_, group) in enumerate(groups)}
    ids = []
    with store.transaction():
        for row in selected:
            fraction = group_index[row["group"]] / max(1, len(groups))
            split = "train" if fraction < 0.6 else "dev" if fraction < 0.8 else "test"
            item = {
                **row,
                "protocol_id": protocol_id,
                "guide": extraction["version"],
                "split": split,
                "second_review_required": extraction["second_review_fraction"] > 0
                and int(row["text_hash"][:8], 16) % 5 == 0,
                **({"reviewer": extraction["reviewer"]} if "reviewer" in extraction else {}),
            }
            ids.append(store.put("candidate", item))
        return store.put(
            "candidate_manifest",
            {
                "protocol_id": protocol_id,
                "candidate_ids": sorted(ids),
                "target": target,
                "selection": "balanced_search_strata_round_robin_v1",
                "status": "READY_FOR_REVIEW" if len(ids) >= 150 else "CORPUS_INSUFFICIENT",
            },
        )


def candidates(store: Store, manifest_id: str) -> list[dict]:
    manifest = store.get(manifest_id, "candidate_manifest")
    return [
        {"id": identity, **store.get(identity, "candidate")}
        for identity in manifest["candidate_ids"]
    ]


def review_template(store: Store, manifest_id: str) -> list[dict]:
    return [
        {
            "candidate_id": c["id"],
            "candidate_hash": digest({k: v for k, v in c.items() if k != "id"}),
            "split": c["split"],
            "guide": c["guide"],
            "citation": citation(store, c["span_id"]),
            "second_review_required": c["second_review_required"],
            "reviewer": c.get("reviewer"),
            "reviewer_type": "human",
            "attested_human": False,
            "reviewed_at": None,
            "label": None,
            "horizon": None,
            "numbers": None,
            "support": [],
            "comment": "",
            "supersedes": None,
            "status": "UNREVIEWED",
        }
        for c in candidates(store, manifest_id)
    ]


def validate_answer(answer: dict, text: str) -> None:
    require(answer, {"label", "horizon", "numbers", "support"})
    if answer["label"] not in LABELS:
        raise Invalid("Unknown guidance label")
    if answer["label"] not in ("NO_GUIDANCE", "AMBIGUOUS") and not answer["horizon"]:
        raise Invalid("Directional guidance requires a horizon")
    for span in answer["support"]:
        require(span, {"start", "end", "quote"})
        if (
            type(span["start"]) is not int
            or type(span["end"]) is not int
            or not 0 <= span["start"] < span["end"] <= len(text)
            or text[span["start"] : span["end"]] != span["quote"]
        ):
            raise Invalid("Unsupported answer citation")
    if answer["label"] not in ("NO_GUIDANCE", "AMBIGUOUS") and not answer["support"]:
        raise Invalid("Guidance answer requires exact support")
    supported_text = "\n".join(span["quote"] for span in answer["support"])
    if answer["horizon"] is not None and (
        not isinstance(answer["horizon"], str)
        or not answer["horizon"]
        or answer["horizon"] not in supported_text
    ):
        raise Invalid("Horizon must preserve an exact supported fiscal expression")
    if answer["numbers"] is not None:
        require(answer["numbers"], {"low", "high", "unit", "currency", "basis"})
        try:
            if any(not isinstance(answer["numbers"][key], str) for key in ("low", "high")):
                raise Invalid("Numeric guidance must use decimal strings")
            values = [Decimal(answer["numbers"][key]) for key in ("low", "high")]
        except InvalidOperation as exc:
            raise Invalid("Invalid numeric guidance decimal") from exc
        if any(not v.is_finite() or v < 0 for v in values) or values[0] > values[1]:
            raise Invalid("Invalid numeric guidance range")
        if answer["numbers"]["unit"] not in ("million", "billion", "percent", "units"):
            raise Invalid("Unrecognized numeric unit")
        numbers = answer["numbers"]
        tokens = {
            Decimal(token.replace(",", ""))
            for token in re.findall(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?![\w.])", supported_text)
        }
        if any(value not in tokens for value in values):
            raise Invalid("Numeric guidance endpoints lack exact support")
        unit_pattern = "%" if numbers["unit"] == "percent" else r"\b" + numbers["unit"] + r"s?\b"
        if not re.search(unit_pattern, supported_text, re.I):
            raise Invalid("Numeric guidance unit lacks support")
        currency = numbers["currency"]
        currency_pattern = (
            r"\bUSD\b|\$|U\.S\. dollars"
            if currency == "USD"
            else (
                r"\b" + re.escape(currency) + r"\b"
                if isinstance(currency, str) and currency
                else None
            )
        )
        if numbers["unit"] not in ("percent", "units") and (
            currency_pattern is None or not re.search(currency_pattern, supported_text, re.I)
        ):
            raise Invalid("Numeric guidance currency lacks support")
        if numbers["basis"] != "consolidated_gaap_total_revenue" or not re.search(
            r"\brevenue\b", supported_text, re.I
        ):
            raise Invalid("Numeric guidance requires consolidated GAAP total revenue basis")


def import_reviews(store: Store, manifest_id: str, rows: list[dict]) -> list[str]:
    known = {c["id"]: c for c in candidates(store, manifest_id)}
    checked = []
    keys = set()
    for row in rows:
        require(
            row,
            {
                "candidate_id",
                "candidate_hash",
                "split",
                "guide",
                "reviewer",
                "reviewer_type",
                "attested_human",
                "reviewed_at",
                "label",
                "horizon",
                "numbers",
                "support",
                "supersedes",
                "status",
                "comment",
            },
        )
        candidate = known.get(row["candidate_id"])
        if candidate is None:
            raise Invalid("Review belongs to another candidate manifest")
        expected = digest({k: v for k, v in candidate.items() if k != "id"})
        if (
            row["candidate_hash"] != expected
            or row["split"] != candidate["split"]
            or row["guide"] != candidate["guide"]
        ):
            raise Invalid("Review candidate identity, guide or split changed")
        if (
            row["reviewer_type"] != "human"
            or row["attested_human"] is not True
            or not row["reviewer"]
            or row["status"] != "REVIEWED"
        ):
            raise Invalid("Actual human review attestation required")
        if utc(row["reviewed_at"]) > utc(now()):
            raise Invalid("Review cannot be future dated")
        key = (row["candidate_id"], row["reviewer"])
        if key in keys:
            raise Invalid("Duplicate reviewer/candidate in batch")
        keys.add(key)
        text = citation(store, candidate["span_id"])["quote"]
        validate_answer(row, text)
        existing = [r for r in store.all("review") if (r["candidate_id"], r["reviewer"]) == key]
        if row["supersedes"]:
            parent = store.get(row["supersedes"], "review")
            if (parent["candidate_id"], parent["reviewer"]) != key or utc(
                parent["reviewed_at"]
            ) >= utc(row["reviewed_at"]):
                raise Invalid("Invalid review revision lineage")
            if any(r["supersedes"] == row["supersedes"] for r in existing):
                raise Invalid("Review revision branching forbidden")
        elif existing and not any(
            {k: v for k, v in r.items() if k != "id"} == row for r in existing
        ):
            raise Invalid("Changed review must explicitly supersede previous review")
        checked.append(row)
    with store.transaction():
        return [store.put("review", row) for row in checked]


def gold(store: Store, candidate: dict) -> tuple[dict | None, bool]:
    rows = [r for r in store.all("review") if r["candidate_id"] == candidate["id"]]
    superseded = {r["supersedes"] for r in rows}
    tips = [r for r in rows if r["id"] not in superseded]
    fields = ("label", "horizon", "numbers", "support")
    disagreement = len({digest({k: r[k] for k in fields}) for r in tips}) > 1
    if not tips or disagreement or (candidate["second_review_required"] and len(tips) < 2):
        return None, disagreement
    return tips[0], False


def rules(text: str) -> dict:
    support = []
    found = []
    horizons = []
    revenue_guidance = False
    # Sentences/lines constrain direction to the revenue clause, not nearby EPS claims.
    for match in re.finditer(r"[^\n.!?]+(?:[.!?]|(?=\n)|$)", text):
        sentence = match.group()
        low = sentence.lower()
        if "revenue" not in low or not re.search(r"guidance|outlook", low):
            continue
        revenue_guidance = True
        horizon = re.search(HORIZON, sentence, re.I)
        labels = [label for label, pattern in DIRECTIONS.items() if re.search(pattern, low)]
        if (
            not horizon
            or len(labels) != 1
            or re.search(
                r"\b(?:eps|margin|earnings per share|subscription|segment|constant.currency|"
                r"bookings|billings|rpo|remaining performance obligations|non.gaap|organic)\b",
                low,
            )
        ):
            continue
        found.extend(labels)
        horizons.append(horizon.group())
        support.append({"start": match.start(), "end": match.end(), "quote": sentence})
    label = found[0] if len(set(found)) == 1 and len(set(horizons)) == 1 else "AMBIGUOUS"
    if not revenue_guidance:
        label = "NO_GUIDANCE"
    # Numeric tables require human context; no unlabeled table-to-range guessing.
    return {
        "label": label,
        "horizon": horizons[0] if label not in ("AMBIGUOUS", "NO_GUIDANCE") else None,
        "numbers": None,
        "support": support if label not in ("AMBIGUOUS", "NO_GUIDANCE") else [],
        "abstained": label == "AMBIGUOUS",
        "reason": "missing_or_conflicting_explicit_revenue_horizon"
        if label == "AMBIGUOUS"
        else None,
    }


def extract_rules(store: Store, manifest_id: str) -> str:
    predictions = []
    for candidate in candidates(store, manifest_id):
        text = citation(store, candidate["span_id"])["quote"]
        predictions.append({"candidate_id": candidate["id"], **rules(text)})
    with store.transaction():
        return store.put(
            "extraction_run",
            {
                "manifest_id": manifest_id,
                "method": "rules-v1",
                "model": "explicit-revenue-horizon-regex-v1",
                "implementation_id": sha(Path(__file__).read_bytes()),
                "prompt_id": None,
                "cost_usd": 0,
                "status": "RUN",
                "predictions": predictions,
            },
        )


def extract_tfidf(store: Store, manifest_id: str) -> str:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline

    rows = candidates(store, manifest_id)
    training: list[tuple[dict, dict]] = []
    for candidate in rows:
        if candidate["split"] == "train":
            reviewed, _ = gold(store, candidate)
            if reviewed is not None:
                training.append((candidate, reviewed))
    run = {
        "manifest_id": manifest_id,
        "method": "tfidf-v1",
        "model": f"sklearn-{sklearn.__version__}-tfidf-L2-C1",
        "implementation_id": sha(Path(__file__).read_bytes()),
        "prompt_id": None,
        "cost_usd": 0,
        "predictions": [],
        "training_review_ids": [g["id"] for _, g in training],
    }
    if len({g["label"] for _, g in training}) < 2:
        run.update(status="NOT_FIT", reason="need_human_training_labels_from_at_least_two_classes")
    else:
        model = make_pipeline(
            TfidfVectorizer(ngram_range=(1, 2), min_df=1), LogisticRegression(C=1, max_iter=2000)
        )
        model.fit(
            [citation(store, c["span_id"])["quote"] for c, _ in training],
            [g["label"] for _, g in training],
        )
        predictions = []
        for c in rows:
            text = citation(store, c["span_id"])["quote"]
            label = str(model.predict([text])[0])
            horizon = re.search(HORIZON, text, re.I)
            if label not in ("NO_GUIDANCE", "AMBIGUOUS") and not horizon:
                label = "AMBIGUOUS"
            predictions.append(
                {
                    "candidate_id": c["id"],
                    "label": label,
                    "horizon": horizon.group() if horizon else None,
                    "numbers": None,
                    "support": [{"start": 0, "end": len(text), "quote": text}],
                    "abstained": label == "AMBIGUOUS",
                }
            )
        run.update(
            status="RUN",
            predictions=predictions,
            vocabulary=model[0].vocabulary_,
            classes=model[1].classes_.tolist(),
            coefficients=model[1].coef_.tolist(),
            intercept=model[1].intercept_.tolist(),
        )
    with store.transaction():
        return store.put("extraction_run", run)


def llm_requests(store: Store, manifest_id: str) -> list[dict]:
    prompt = (
        "Extract only stated revenue-guidance revision. Labels: "
        + ", ".join(LABELS)
        + ". Do not use external knowledge or predict outcomes. Require revenue, explicit direction "
        "and fiscal horizon; only consolidated GAAP total revenue, not subscription/segment, "
        "constant-currency, EPS/margin, bookings/billings/RPO or organic guidance. "
        "Ambiguous or conflicting context: AMBIGUOUS. "
        "Return label,horizon,numbers (null or low/high/unit/currency/basis),support "
        "(zero-based start,end,exact quote). Preserve the exact supported horizon. "
        "Numbers require explicit supported endpoints/units/currency and basis consolidated_gaap_total_revenue."
    )
    result = []
    for c in candidates(store, manifest_id):
        request = {
            "candidate_id": c["id"],
            "manifest_id": manifest_id,
            "prompt": prompt,
            "prompt_id": digest(prompt),
            "text": citation(store, c["span_id"])["quote"],
        }
        result.append({"request_id": digest(request), **request})
    return result


def import_llm(store: Store, manifest_id: str, responses: list[dict]) -> str:
    requests = {r["request_id"]: r for r in llm_requests(store, manifest_id)}
    predictions = []
    used = set()
    total = 0.0
    for row in responses:
        require(
            row,
            {
                "request_id",
                "model",
                "provider",
                "generated_at",
                "cost_usd",
                "usage",
                "answer",
                "config",
            },
        )
        request = requests.get(row["request_id"])
        if request is None or row["request_id"] in used:
            raise Invalid("Unknown or duplicate LLM request")
        used.add(row["request_id"])
        if not row["model"] or not row["provider"] or utc(row["generated_at"]) > utc(now()):
            raise Invalid("Actual LLM identity/time required")
        if not isinstance(row["config"], dict) or not row["config"]:
            raise Invalid("Actual provider inference configuration required")
        from math import isfinite

        if (
            type(row["cost_usd"]) not in (float, int)
            or not isfinite(row["cost_usd"])
            or row["cost_usd"] < 0
        ):
            raise Invalid("Finite nonnegative inference cost required")
        validate_answer(row["answer"], request["text"])
        predictions.append(
            {
                "candidate_id": request["candidate_id"],
                **row["answer"],
                "abstained": row["answer"]["label"] == "AMBIGUOUS",
            }
        )
        total += row["cost_usd"]
    if not responses:
        raise Invalid("No actual LLM responses supplied")
    with store.transaction():
        return store.put(
            "extraction_run",
            {
                "manifest_id": manifest_id,
                "method": "llm-external-v1",
                "model": sorted({r["model"] for r in responses}),
                "prompt_id": next(iter(requests.values()))["prompt_id"],
                "implementation_id": sha(Path(__file__).read_bytes()),
                "config_ids": sorted({digest(r["config"]) for r in responses}),
                "responses": responses,
                "cost_usd": total,
                "status": "RUN",
                "provenance": "supplied_not_independently_authenticated",
                "predictions": predictions,
            },
        )


def evaluate_extraction(store: Store, run_id: str, split: str = "test") -> dict:
    run = store.get(run_id, "extraction_run")
    rows = [c for c in candidates(store, run["manifest_id"]) if c["split"] == split]
    predictions = {p["candidate_id"]: p for p in run["predictions"]}
    pairs = []
    disagreements = 0
    review_ids = []
    for c in rows:
        reviewed, disagreement = gold(store, c)
        disagreements += disagreement
        if reviewed is not None:
            pairs.append((c, reviewed, predictions.get(c["id"])))
            review_ids.append(reviewed["id"])
    result = {
        "run_id": run_id,
        "implementation_id": sha(Path(__file__).read_bytes()),
        "split": split,
        "candidates": len(rows),
        "gold_count": len(pairs),
        "disagreements": disagreements,
        "review_ids": review_ids,
        "status": "HUMAN_REVIEW_PENDING",
        "metrics": None,
        "limitations": (
            "Citation identity is not human support; partial coverage is not final held-out performance. "
            "Single-reviewer labels do not establish independent inter-annotator agreement."
        ),
    }
    if pairs and run["status"] == "RUN":
        failures: Counter[str] = Counter()
        per_label = {}
        for label in LABELS:
            tp = sum(
                g["label"] == label and p is not None and p["label"] == label for _, g, p in pairs
            )
            fp = sum(
                g["label"] != label and p is not None and p["label"] == label for _, g, p in pairs
            )
            fn = sum(
                g["label"] == label and (p is None or p["label"] != label) for _, g, p in pairs
            )
            precision = tp / (tp + fp) if tp + fp else 0
            recall = tp / (tp + fn) if tp + fn else 0
            per_label[label] = {
                "precision": precision,
                "recall": recall,
                "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0,
                "gold_count": tp + fn,
            }
        valid = supported = numeric_correct = numeric_n = abstained = 0
        for c, g, p in pairs:
            if g["numbers"] is not None:
                numeric_n += 1
                numeric_correct += p is not None and g["numbers"] == p["numbers"]
            if p is None:
                failures["missing_prediction"] += 1
                abstained += 1
                continue
            try:
                validate_answer(p, citation(store, c["span_id"])["quote"])
                valid += 1
            except Invalid:
                failures["invalid_citation"] += 1
            abstained += p["label"] == "AMBIGUOUS"
            if p["horizon"] != g["horizon"]:
                failures["wrong_horizon"] += 1
            if p["numbers"] is not None and g["numbers"] is None:
                failures["spurious_numeric_range"] += 1
            elif p["numbers"] != g["numbers"]:
                failures["wrong_or_missing_numeric_range"] += 1
            if p["label"] != g["label"]:
                failures["wrong_label"] += 1
            gold_spans = {(s["start"], s["end"]) for s in g["support"]}
            pred_spans = {(s["start"], s["end"]) for s in p["support"]}
            supported += gold_spans == pred_spans
        result.update(
            status="EVALUATED" if len(pairs) == len(rows) else "PARTIAL_HUMAN_REVIEW",
            metrics={
                "per_label": per_label,
                "macro_f1": sum(v["f1"] for v in per_label.values()) / len(LABELS),
                "abstentions": abstained,
                "citation_validity": valid / len(pairs),
                "exact_supported_span_accuracy": supported / len(pairs),
                "numeric_count": numeric_n,
                "numeric_accuracy": numeric_correct / numeric_n if numeric_n else None,
                "horizon_count": len(pairs),
                "horizon_accuracy": sum(
                    p is not None and p["horizon"] == g["horizon"] for _, g, p in pairs
                )
                / len(pairs),
                "numeric_tuple_count": len(pairs),
                "nullable_numeric_accuracy": sum(
                    p is not None and p["numbers"] == g["numbers"] for _, g, p in pairs
                )
                / len(pairs),
                "failures": dict(failures),
            },
        )
    with store.transaction():
        result_id = store.put("extraction_evaluation", result)
    return {"id": result_id, **result}
