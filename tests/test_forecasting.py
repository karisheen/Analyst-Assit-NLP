import calendar
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone

import numpy as np
import pytest

from forecast_lab.core import Invalid, digest
from forecast_lab.facts import chain, import_fact, resolve_values
from forecast_lab.forecasting import (
    evaluate,
    fit_models,
    import_observation,
    losses,
    paired_bootstrap,
    predict,
    features,
)
from forecast_lab.ledger import create, resolve
from forecast_lab.protocol import read_protocol
from forecast_lab.reproduce import default_protocol, fixture_request
from forecast_lab.store import Store, ingest
from test_store import metadata


def synthetic_history(tmp_path, count=28, late_report=False):
    """Explicit software-only source fixtures; never human labels or financial evidence."""
    store = Store(tmp_path / "numeric.db")
    frozen, _ = read_protocol(default_protocol())
    protocol = deepcopy(frozen)
    protocol["version"] = "synthetic-test-only"
    protocol["minimums"].update(
        train_rows=8,
        train_companies=2,
        train_quarters=3,
        train_each_class=2,
        evaluation_rows=4,
        evaluation_companies=2,
        evaluation_quarters=2,
        evaluation_each_class=1,
    )
    protocol["metrics"]["bootstrap_replicates"] = 80
    histories = {}
    for company_index, cik in enumerate(("0001108524", "0000796343")):
        history = []
        for index in range(count):
            year, q = 2018 + index // 4, index % 4 + 1
            month = q * 3
            end = date(year, month, calendar.monthrange(year, month)[1])
            start = date(year, month - 2, 1)
            known = datetime.combine(
                end + timedelta(days=25), datetime.min.time(), timezone.utc
            ).isoformat()
            if late_report and index == 12:
                known = (datetime.fromisoformat(known) + timedelta(days=120)).isoformat()
            value = str(1000 + index * 30 + ((index * 7 + company_index * 3) % 9) * 25)
            direction = "raises" if index % 2 else "lowers"
            raw = (
                f"Original synthetic consolidated GAAP total revenue for {year}Q{q} was USD ${value} million. "
                "This is an artificial deterministic test disclosure, not financial research evidence.\n\n"
                f"Company {direction} next quarter revenue guidance for the coming reporting period."
            ).encode()
            doc = ingest(
                store,
                raw,
                metadata(
                    raw,
                    cik=cik,
                    source_id=f"synthetic-{cik}-{year}-{q}",
                    fiscal_year=year,
                    fiscal_quarter=q,
                    period_end=end.isoformat(),
                    retrieved_at=known,
                    published_at=known,
                    published_date=known[:10],
                    version_available_at=known,
                ),
            )
            parse = next(p for p in store.all("parse") if p["document_id"] == doc)
            span = next(
                s for s in store.all("span") if s["parse_id"] == parse["id"] and s["start"] == 0
            )
            fact = import_fact(
                store,
                dict(
                    cik=cik,
                    fiscal_year=year,
                    fiscal_quarter=q,
                    start=start.isoformat(),
                    end=end.isoformat(),
                    regime="calendar",
                    currency="USD",
                    value=value,
                    scale="1000000",
                    span_id=span["id"],
                    raw_token=f"${value}",
                    unit_support=dict(
                        span_id=span["id"], unit_token="million", currency_token="USD"
                    ),
                    original=True,
                    authority_attestation="synthetic test only",
                    reviewer="test-fixture",
                    known_at=known,
                    basis="consolidated_gaap_total_revenue",
                ),
            )
            history.append(
                dict(
                    fact=fact,
                    doc=doc,
                    year=year,
                    q=q,
                    cutoff=(datetime.fromisoformat(known) + timedelta(days=1)).isoformat(),
                )
            )
        histories[cik] = history
        for index in range(7, count - 1):
            item = history[index]
            import_observation(
                store,
                protocol,
                dict(
                    cik=cik,
                    reported_year=item["year"],
                    reported_quarter=item["q"],
                    information_cutoff=item["cutoff"],
                    feature_fact_ids=[h["fact"] for h in history[index - 5 : index + 1]],
                    document_ids=[item["doc"]],
                    evidence_class="pipeline_development",
                    outcome_fact_ids=[h["fact"] for h in history[index - 5 : index + 2]],
                ),
            )
    return store, protocol, histories


def test_source_to_four_baselines_and_resolution(tmp_path):
    store, protocol, histories = synthetic_history(tmp_path)
    fit_id = fit_models(store, protocol, "pipeline_development")
    fit = store.get(fit_id)
    assert fit["status"] == "FIT"
    assert set(fit["models"]) == {"A", "B", "C", "D"}
    for identity in fit["training_ids"]:
        row = store.get(identity)
        assert row["outcome"]["outcome_available_at"] < fit["fit_at"]
    result = evaluate(store, protocol, fit_id)
    assert result["status"] == "SOFTWARE_DEMONSTRATION_NOT_RESEARCH_EVIDENCE"
    assert result["forecasts"] == 6
    assert result["comparisons"]["D_minus_B"]["brier"]["company_clusters"] == 2
    history = histories["0001108524"]
    index = 25
    request = fixture_request(store, protocol, history[index]["doc"])
    row = next(
        r
        for r in store.all("observation")
        if r["cik"] == request["cik"]
        and r["reported_year"] == request["reported_year"]
        and r["reported_quarter"] == request["reported_quarter"]
    )
    request.update(
        probability=predict(fit, "D", row["features"]),
        abstained=False,
        fit_id=fit_id,
        baseline="D",
        feature_fact_ids=row["feature_fact_ids"],
        model_id=f"{fit_id}:D",
        config_id=fit["config_id"],
    )
    event = create(store, protocol, request)
    frozen_features = store.get(event)["features"]
    assert set(frozen_features["numeric_sources"]) == {
        h["doc"] for h in history[index - 5 : index + 1]
    }
    resolution = resolve(
        store, protocol, event, [h["fact"] for h in history[index - 5 : index + 2]]
    )
    assert store.get(resolution)["label"] == row["outcome"]["label"]


def test_loss_ties_and_cluster_weights():
    brier, log = losses([0, 1, 0.5], [0, 1, 1], 1e-6)
    np.testing.assert_allclose(brier, [0, 0, 0.25])
    assert np.isfinite(log).all()
    result = paired_bootstrap(
        np.array([-0.1, -0.1, 0.1, 0.1]), ["a", "a", "b", "b"], ["q1", "q2", "q1", "q2"], 100, 42
    )
    assert result["mean"] == 0
    assert result["interval"][0] <= 0 <= result["interval"][1]
    assert result == paired_bootstrap(
        np.array([-0.1, -0.1, 0.1, 0.1]), ["a", "a", "b", "b"], ["q1", "q2", "q1", "q2"], 100, 42
    )
    facts = {i: dict(value="100", scale="1", known_at="2020-01-01T00:00:00Z") for i in range(-5, 2)}
    assert resolve_values(facts)["label"] == 0
    facts[1]["value"] = "99.999999999999999999"
    assert resolve_values(facts)["label"] == 1


def test_future_features_and_holdout_are_rejected(tmp_path):
    store, protocol, histories = synthetic_history(tmp_path)
    history = histories["0001108524"]
    with pytest.raises(Invalid, match="consecutive"):
        chain(store, [h["fact"] for h in history[0:5]], "0001108524", 2019, 2, False)
    fit_id = fit_models(store, protocol, "pipeline_development")
    with pytest.raises(Invalid, match="reporting date"):
        evaluate(store, protocol, fit_id, "holdout")
    row = store.all("observation")[0]
    bad = {
        k: row[k]
        for k in (
            "cik",
            "reported_year",
            "reported_quarter",
            "information_cutoff",
            "feature_fact_ids",
            "document_ids",
            "evidence_class",
            "outcome_fact_ids",
        )
    }
    bad["information_cutoff"] = "2010-01-01T00:00:00Z"
    with pytest.raises(Invalid, match="cutoff"):
        import_observation(store, protocol, bad)
    assert digest(protocol) != read_protocol(default_protocol())[1]


def test_features_need_no_future_outcome_and_filter_fiscal_years(tmp_path):
    store, protocol, histories = synthetic_history(tmp_path, count=6)
    history = histories["0001108524"]
    item = history[-1]
    request = dict(
        cik="0001108524",
        reported_year=item["year"],
        reported_quarter=item["q"],
        information_cutoff=item["cutoff"],
        feature_fact_ids=[h["fact"] for h in history],
        document_ids=[item["doc"]],
        evidence_class="pipeline_development",
    )
    assert features(store, protocol, request)["text"] == [1.0, 0.0, 0.0, 0.0, 0.0]
    assert (
        max(f["fiscal_year"] * 4 + f["fiscal_quarter"] for f in store.all("fact")) == 2019 * 4 + 2
    )
    source = store.get(item["doc"], "document")
    for horizon, expected in (
        ("Q3 FY2018", 0.0),
        ("Q3 FY18", 0.0),
        ("Q3 FY2019", 1.0),
        ("Q3 FY19", 1.0),
    ):
        raw = (
            f"Company raises {horizon} revenue guidance. This synthetic source demonstrates fiscal horizon "
            "filtering and is not business-outcome evidence."
        ).encode()
        doc = ingest(
            store,
            raw,
            metadata(
                raw,
                **{
                    k: v
                    for k, v in source.items()
                    if k not in ("raw_hash", "expected_text", "source_id")
                },
                source_id=f"horizon-{horizon}",
            ),
        )
        result = features(store, protocol, {**request, "document_ids": [doc]})
        assert result["text"] == [expected, 0.0, 0.0, 0.0, 0.0]


def test_already_public_outcomes_are_not_forecasts(tmp_path):
    with pytest.raises(Invalid, match="already available"):
        synthetic_history(tmp_path, late_report=True)
