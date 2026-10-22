"""Frozen A–D baselines with source-derived features and crossed-cluster comparisons."""

from __future__ import annotations

import math
import re
import warnings
from collections import Counter
from datetime import timedelta
from pathlib import Path

import numpy as np

from .core import Invalid, digest, now, require, sha, utc
from .extraction import rules
from .facts import amount, chain, ordinal, resolve_values, source_documents
from .protocol import split_for, validate
from .store import Store, citation


def feature_implementation() -> dict[str, str]:
    return {
        name: sha(Path(__file__).with_name(f"{name}.py").read_bytes())
        for name in ("forecasting", "extraction", "facts")
    }


def quarter_cluster(timestamp: str) -> str:
    time = utc(timestamp)
    return f"{time.year}Q{(time.month - 1) // 3 + 1}"


def features(store: Store, protocol: dict, request: dict) -> dict:
    require(
        request,
        {
            "cik",
            "reported_year",
            "reported_quarter",
            "information_cutoff",
            "feature_fact_ids",
            "document_ids",
            "evidence_class",
        },
    )
    cutoff = utc(request["information_cutoff"])
    facts = chain(
        store,
        request["feature_fact_ids"],
        request["cik"],
        request["reported_year"],
        request["reported_quarter"],
        include_outcome=False,
    )
    target = ordinal(request["reported_year"], request["reported_quarter"]) + 1
    target_year, target_quarter = target // 4, target % 4 + 1
    if cutoff != utc(facts[0]["known_at"]) + timedelta(
        seconds=protocol["timing"]["cutoff_seconds"]
    ):
        raise Invalid("Feature cutoff does not match original revenue release +24h")
    numeric_sources = {}
    for fact in facts.values():
        documents = source_documents(store, fact)
        if utc(fact["known_at"]) > cutoff:
            raise Invalid("Future fundamental in historical features")
        for identity, doc in documents.items():
            if (
                request["evidence_class"] != "pipeline_development"
                and doc["snapshot_status"] != "verified_original"
            ):
                raise Invalid("Research features need original-vintage sources")
            numeric_sources[identity] = doc["raw_hash"]
    numeric = [
        float(amount(facts[0]) / amount(facts[-4]) - 1),
        float(amount(facts[-1]) / amount(facts[-5]) - 1),
    ]
    if not request["document_ids"]:
        raise Invalid("Missing text sources cannot be encoded as no guidance")
    text = [0.0] * 5
    used = []
    for doc_id in request["document_ids"]:
        doc = store.get(doc_id, "document")
        if (
            doc["cik"] != request["cik"]
            or doc["version_available_at"] is None
            or utc(doc["version_available_at"]) > cutoff
        ):
            raise Invalid("Unavailable or wrong-company text source")
        if (doc["fiscal_year"], doc["fiscal_quarter"]) != (
            request["reported_year"],
            request["reported_quarter"],
        ):
            raise Invalid("Text features require the reported-quarter disclosure bundle")
        if (
            request["evidence_class"] != "pipeline_development"
            and doc["snapshot_status"] != "verified_original"
        ):
            raise Invalid("Unverified text cannot enter research features")
        for span in store.all("span"):
            cite = citation(store, span["id"])
            if cite["document_id"] != doc_id:
                continue
            answer = rules(cite["quote"])
            if answer["label"] == "AMBIGUOUS":
                text[4] = 1.0
                used.append(span["id"])
            elif answer["label"] in ("RAISED", "LOWERED", "MAINTAINED", "INITIATED"):
                horizon = answer["horizon"].lower()
                years = re.findall(r"\b(?:fy\s*)?((?:20)?\d{2})\b", horizon)
                year_match = not years or all(
                    (int(y) if len(y) == 4 else 2000 + int(y)) == target_year for y in years
                )
                quarter_words = {"first": 1, "second": 2, "third": 3, "fourth": 4}
                q_match = re.search(r"q([1-4])", horizon)
                explicit_q = (
                    int(q_match.group(1))
                    if q_match
                    else next((v for k, v in quarter_words.items() if k in horizon), None)
                )
                covers_target = year_match and (
                    "next" in horizon
                    or explicit_q == target_quarter
                    or (explicit_q is None and bool(years))
                )
                if covers_target:
                    text[
                        ("RAISED", "LOWERED", "MAINTAINED", "INITIATED").index(answer["label"])
                    ] = 1.0
                    used.append(span["id"])
    return {
        "numeric": numeric,
        "text": text,
        "span_ids": sorted(set(used)),
        "feature_fact_ids": request["feature_fact_ids"],
        "document_ids": request["document_ids"],
        "numeric_sources": numeric_sources,
        "implementation_id": feature_implementation(),
    }


def import_observation(store: Store, protocol: dict, row: dict) -> str:
    require(
        row,
        {
            "cik",
            "reported_year",
            "reported_quarter",
            "information_cutoff",
            "feature_fact_ids",
            "document_ids",
            "evidence_class",
            "outcome_fact_ids",
        },
    )
    if row["evidence_class"] not in ("pipeline_development", "retrospective"):
        raise Invalid("Prospective evidence must originate in the actual-time ledger")
    if row["cik"] not in {c["cik"] for c in protocol["cohort"]}:
        raise Invalid("Issuer outside cohort")
    split = split_for(protocol, row["information_cutoff"])
    if split == "holdout" and utc(now()) < utc(protocol["splits"]["final_holdout_not_before"]):
        raise Invalid("Final holdout remains sealed until preregistered reporting date")
    inputs = features(store, protocol, row)
    values = None
    if row["outcome_fact_ids"]:
        all_facts = chain(
            store,
            row["outcome_fact_ids"],
            row["cik"],
            row["reported_year"],
            row["reported_quarter"],
        )
        if {f["id"] for k, f in all_facts.items() if k <= 0} != set(row["feature_fact_ids"]):
            raise Invalid("Outcome resolution changed original forecast-time revenue vintages")
        values = resolve_values(all_facts)
        if utc(values["outcome_available_at"]) <= utc(row["information_cutoff"]):
            raise Invalid("Outcome was already available at forecast cutoff")
        if utc(values["outcome_available_at"]) > utc(now()):
            raise Invalid("Outcome unavailable at import")
        if row["evidence_class"] != "pipeline_development":
            for f in all_facts.values():
                if any(
                    d["snapshot_status"] != "verified_original"
                    for d in source_documents(store, f).values()
                ):
                    raise Invalid("Outcome source is not an original vintage")
    payload = {
        **row,
        "protocol_id": validate(protocol),
        "features": inputs,
        "outcome": values,
        "split": split,
    }
    existing = [
        r
        for r in store.all("observation")
        if (
            r["cik"],
            r["reported_year"],
            r["reported_quarter"],
            r["protocol_id"],
            r["evidence_class"],
        )
        == (
            row["cik"],
            row["reported_year"],
            row["reported_quarter"],
            validate(protocol),
            row["evidence_class"],
        )
    ]
    if existing and any({k: v for k, v in r.items() if k != "id"} != payload for r in existing):
        raise Invalid(
            "Duplicate or changed company-quarter observation; preserve a new dataset/protocol"
        )
    with store.transaction():
        return store.put("observation", payload)


def vector(features_: dict, model: str) -> list[float]:
    return (
        features_["numeric"]
        if model == "B"
        else features_["text"]
        if model == "C"
        else features_["numeric"] + features_["text"]
    )


def fit_models(store: Store, protocol: dict, evidence_class: str = "retrospective") -> str:
    import sklearn
    from sklearn.exceptions import ConvergenceWarning
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    protocol_id = validate(protocol)
    implementation = feature_implementation()
    fit_at = utc(protocol["splits"]["fit_at"])
    eligible = []
    exclusions = []
    rows = [
        r
        for r in store.all("observation")
        if r["protocol_id"] == protocol_id and r["evidence_class"] == evidence_class
    ]
    for row in rows:
        if row["features"].get("implementation_id") != implementation:
            raise Invalid("Observation feature implementation differs; rebuild an explicit dataset")
        reason = None
        if row["split"] != "train":
            continue
        if row["outcome"] is None:
            reason = "unresolved"
        elif utc(row["outcome"]["outcome_available_at"]) >= fit_at:
            reason = "outcome_not_known_at_fit"
        elif utc(row["information_cutoff"]) >= fit_at - timedelta(
            days=protocol["splits"]["training_gap_days"]
        ):
            reason = "training_embargo"
        if reason:
            exclusions.append({"id": row["id"], "reason": reason})
        else:
            eligible.append(row)
    counts = Counter(r["outcome"]["label"] for r in eligible)
    minimum = protocol["minimums"]
    sufficient = (
        len(eligible) >= minimum["train_rows"]
        and len({r["cik"] for r in eligible}) >= minimum["train_companies"]
        and len({quarter_cluster(r["information_cutoff"]) for r in eligible})
        >= minimum["train_quarters"]
        and min(counts[0], counts[1]) >= minimum["train_each_class"]
    )
    payload = {
        "protocol_id": protocol_id,
        "evidence_class": evidence_class,
        "fit_at": protocol["splits"]["fit_at"],
        "training_ids": [r["id"] for r in eligible],
        "dataset_id": digest(sorted(r["id"] for r in rows)),
        "exclusions": exclusions,
        "training_counts": dict(counts),
        "models": {},
        "status": "FIT" if sufficient else "INSUFFICIENT_ORIGINAL_VINTAGE_TRAINING_DATA",
        "sklearn": sklearn.__version__,
        "feature_implementation_id": implementation,
        "config_id": digest({"models": protocol["models"], "implementation": implementation}),
        "cost_usd": 0,
        "calibration": "none; reserved calibration interval descriptive only",
    }
    if sufficient:
        labels = [r["outcome"]["label"] for r in eligible]
        payload["models"]["A"] = {"probability": (sum(labels) + 1) / (len(labels) + 2)}
        for name in ("B", "C", "D"):
            x = [vector(r["features"], name) for r in eligible]
            scaler = StandardScaler().fit(x)
            estimator = LogisticRegression(
                C=protocol["models"]["C_regularization"],
                solver=protocol["models"]["solver"],
                max_iter=protocol["models"]["max_iter"],
            )
            with warnings.catch_warnings():
                warnings.simplefilter("error", ConvergenceWarning)
                try:
                    estimator.fit(scaler.transform(x), labels)
                except ConvergenceWarning as exc:
                    raise Invalid(
                        "Forecast fit failed to converge; preserve failed run, do not score"
                    ) from exc
            payload["models"][name] = {
                "mean": scaler.mean_.tolist(),
                "scale": scaler.scale_.tolist(),
                "coefficients": estimator.coef_[0].tolist(),
                "intercept": float(estimator.intercept_[0]),
            }
    with store.transaction():
        return store.put("forecast_model", payload)


def predict(model_artifact: dict, name: str, inputs: dict) -> float:
    if model_artifact["status"] != "FIT" or name not in model_artifact["models"]:
        raise Invalid("Forecast model unavailable")
    model = model_artifact["models"][name]
    if name == "A":
        return model["probability"]
    x = vector(inputs, name)
    z = model["intercept"] + sum(
        c * (v - m) / s
        for c, v, m, s in zip(model["coefficients"], x, model["mean"], model["scale"])
    )
    return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))


def validate_prediction(store: Store, protocol: dict, request: dict) -> dict:
    require(request, {"fit_id", "baseline", "feature_fact_ids"})
    model = store.get(request["fit_id"], "forecast_model")
    expected_class = (
        "pipeline_development"
        if request["evidence_class"] == "pipeline_development"
        else "retrospective"
    )
    if model["protocol_id"] != validate(protocol) or model["evidence_class"] != expected_class:
        raise Invalid("Model protocol/evidence class mismatch")
    if utc(model["fit_at"]) >= utc(request["information_cutoff"]):
        raise Invalid("Model was not fit before forecast cutoff")
    if (
        request["config_id"] != model["config_id"]
        or request["model_id"] != f"{request['fit_id']}:{request['baseline']}"
    ):
        raise Invalid("Model/config identity mismatch")
    inputs = features(store, protocol, request)
    if inputs["implementation_id"] != model.get("feature_implementation_id"):
        raise Invalid("Prediction feature implementation differs from fitted model")
    if not math.isclose(
        request["probability"],
        predict(model, request["baseline"], inputs),
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise Invalid("Probability differs from source-derived frozen model prediction")
    return inputs


def losses(
    probabilities: list[float], labels: list[int], epsilon: float
) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(probabilities, dtype=float)
    y = np.asarray(labels, dtype=float)
    bounded = np.clip(p, epsilon, 1 - epsilon)
    return (p - y) ** 2, -(y * np.log(bounded) + (1 - y) * np.log1p(-bounded))


def paired_bootstrap(
    differences: np.ndarray, companies: list[str], quarters: list[str], repeats: int, seed: int
) -> dict:
    unique_c = sorted(set(companies))
    unique_q = sorted(set(quarters))
    ci = np.array([unique_c.index(c) for c in companies])
    qi = np.array([unique_q.index(q) for q in quarters])
    rng = np.random.default_rng(seed)
    draws = []
    empty = 0
    for _ in range(repeats):
        wc = rng.multinomial(len(unique_c), np.full(len(unique_c), 1 / len(unique_c)))
        wq = rng.multinomial(len(unique_q), np.full(len(unique_q), 1 / len(unique_q)))
        weights = wc[ci] * wq[qi]
        if weights.sum() == 0:
            empty += 1
        else:
            draws.append(float(np.average(differences, weights=weights)))
    return {
        "mean": float(np.mean(differences)),
        "interval": np.quantile(draws, [0.025, 0.975]).tolist() if draws else None,
        "draws": len(draws),
        "zero_weight_draws": empty,
        "company_clusters": len(unique_c),
        "quarter_clusters": len(unique_q),
        "method": "crossed_company_calendar_quarter_pigeonhole",
        "conditional_on_fitted_models": True,
    }


def evaluate(store: Store, protocol: dict, fit_id: str, split: str = "validation") -> dict:
    if split not in ("calibration", "validation", "holdout"):
        raise Invalid("Evaluation requires a non-training chronological split")
    if split == "holdout" and utc(now()) < utc(protocol["splits"]["final_holdout_not_before"]):
        raise Invalid("Final holdout reporting date not reached")
    fit = store.get(fit_id, "forecast_model")
    if fit["protocol_id"] != validate(protocol):
        raise Invalid("Fit/protocol mismatch")
    rows = [
        r
        for r in store.all("observation")
        if r["protocol_id"] == fit["protocol_id"]
        and r["evidence_class"] == fit["evidence_class"]
        and r["split"] == split
    ]
    resolved = []
    exclusions = []
    for row in rows:
        if row["features"].get("implementation_id") != fit.get("feature_implementation_id"):
            raise Invalid("Evaluation feature implementation differs from fitted model")
    for row in rows:
        reason = None
        if row["outcome"] is None:
            reason = "unresolved"
        elif utc(row["outcome"]["outcome_available_at"]) > utc(
            row["information_cutoff"]
        ) + timedelta(days=protocol["resolution"]["deadline_days"]):
            reason = "late_resolution"
        if reason:
            exclusions.append({"id": row["id"], "reason": reason})
        else:
            resolved.append(row)
    report = {
        "fit_id": fit_id,
        "protocol_id": validate(protocol),
        "dataset_id": digest(sorted(r["id"] for r in rows)),
        "evidence_class": fit["evidence_class"],
        "split": split,
        "total": len(rows),
        "resolved": len(resolved),
        "unresolved": sum(r["outcome"] is None for r in rows),
        "excluded": exclusions,
        "forecasts": 0,
        "companies": len({r["cik"] for r in resolved}),
        "quarters": len({quarter_cluster(r["information_cutoff"]) for r in resolved}),
        "dates": len({r["information_cutoff"][:10] for r in resolved}),
        "resolution_coverage": len(resolved) / len(rows) if rows else None,
        "metrics": None,
        "comparisons": None,
        "status": "INSUFFICIENT_ORIGINAL_VINTAGE_DATA",
        "cost_usd": 0,
        "implementation_id": feature_implementation(),
        "config_id": digest(protocol["metrics"]),
        "limitations": [
            "Fixed purposive cohort; retrospective exposure caveat",
            "Bootstrap conditional on fitted models; serial dependence beyond quarter blocks not eliminated",
        ],
    }
    if fit["status"] == "FIT" and resolved:
        labels = [r["outcome"]["label"] for r in resolved]
        scores = {}
        metrics = {}
        predictions = {}
        bins = protocol["metrics"]["bins"]
        for name in ("A", "B", "C", "D"):
            predictions[name] = [predict(fit, name, r["features"]) for r in resolved]
            scores[name] = losses(predictions[name], labels, protocol["metrics"]["clip"])
            calibration = []
            for i, (left, right) in enumerate(zip(bins, bins[1:])):
                indices = [
                    j
                    for j, p in enumerate(predictions[name])
                    if left <= p and (p < right or i == len(bins) - 2 and p == right)
                ]
                calibration.append(
                    {
                        "low": left,
                        "high": right,
                        "count": len(indices),
                        "predicted": float(np.mean([predictions[name][j] for j in indices]))
                        if indices
                        else None,
                        "observed": float(np.mean([labels[j] for j in indices]))
                        if indices
                        else None,
                    }
                )
            metrics[name] = {
                "brier": float(scores[name][0].mean()),
                "log_loss": float(scores[name][1].mean()),
                "count": len(resolved),
                "calibration": calibration,
            }
        comparisons = {}
        for first, second in (("D", "B"), ("B", "A"), ("C", "A")):
            comparisons[f"{first}_minus_{second}"] = {
                loss: paired_bootstrap(
                    scores[first][index] - scores[second][index],
                    [r["cik"] for r in resolved],
                    [quarter_cluster(r["information_cutoff"]) for r in resolved],
                    protocol["metrics"]["bootstrap_replicates"],
                    protocol["metrics"]["bootstrap_seed"],
                )
                for index, loss in enumerate(("brier", "log_loss"))
            }
        minimum = protocol["minimums"]
        counts = Counter(labels)
        sufficient = (
            len(resolved) >= minimum["evaluation_rows"]
            and report["companies"] >= minimum["evaluation_companies"]
            and report["quarters"] >= minimum["evaluation_quarters"]
            and min(counts[0], counts[1]) >= minimum["evaluation_each_class"]
            and report["resolution_coverage"] >= minimum["resolution_coverage"]
        )
        primary = comparisons["D_minus_B"]["brier"]
        status = "INCONCLUSIVE_INSUFFICIENT_EVIDENCE"
        if sufficient:
            status = "NO_DEMONSTRATED_INCREMENTAL_VALUE"
            if (
                split == "holdout"
                and primary["mean"] <= -protocol["metrics"]["minimum_practical_improvement"]
                and primary["interval"]
                and primary["interval"][1] < 0
            ):
                status = "SUPPORTED_INCREMENTAL_FORECAST_VALUE"
        if fit["evidence_class"] == "pipeline_development":
            status = "SOFTWARE_DEMONSTRATION_NOT_RESEARCH_EVIDENCE"
        report.update(
            metrics=metrics,
            comparisons=comparisons,
            status=status,
            forecasts=len(resolved),
            row_ids=[r["id"] for r in resolved],
            predictions=predictions,
            labels=labels,
            model_coverage={name: len(resolved) for name in ("A", "B", "C", "D")},
        )
    with store.transaction():
        identity = store.put("forecast_evaluation", report)
    return {"id": identity, **report}
