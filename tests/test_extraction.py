import copy
from pathlib import Path

import pytest

from forecast_lab.core import Invalid, now
from forecast_lab.extraction import (
    candidates,
    evaluate_extraction,
    extract_rules,
    extract_tfidf,
    gold,
    import_llm,
    import_reviews,
    llm_requests,
    prepare_candidates,
    review_template,
    rules,
)
from forecast_lab.protocol import read_protocol
from forecast_lab.reproduce import default_protocol
from forecast_lab.store import Store, ingest
from test_store import RAW, metadata


def corpus(tmp_path):
    store = Store(tmp_path / "review.db")
    ingest(store, RAW, metadata(RAW))
    protocol, _ = read_protocol(default_protocol())
    manifest = prepare_candidates(store, protocol)
    return store, manifest


def test_rules_do_not_confuse_eps_growth_or_horizon():
    assert rules("Raises full year FY2025 revenue guidance.")["label"] == "RAISED"
    assert (
        rules("Raises EPS guidance while reiterating full year FY2025 revenue guidance.")["label"]
        == "AMBIGUOUS"
    )
    assert rules("Revenue grew 12% over last year.")["label"] == "NO_GUIDANCE"
    assert rules("Raises revenue guidance.")["label"] == "AMBIGUOUS"
    assert (
        rules("Raises FY2025 revenue guidance. Lowers FY2025 revenue guidance.")["label"]
        == "AMBIGUOUS"
    )
    assert rules("Raises FY2025 revenue guidance\nNo terminal punctuation")["label"] == "RAISED"
    assert rules("Raises full year FY2025 subscription revenue guidance.")["label"] == "AMBIGUOUS"


def test_pending_human_reviews_never_become_gold(tmp_path):
    store, manifest = corpus(tmp_path)
    template = review_template(store, manifest)
    with pytest.raises(Invalid):
        import_reviews(store, manifest, template)
    run = extract_rules(store, manifest)
    result = evaluate_extraction(store, run, "train")
    assert result["metrics"] is None
    assert result["status"] == "HUMAN_REVIEW_PENDING"


def test_reviews_preserve_disagreement_and_reject_bad_batch(tmp_path):
    store, manifest = corpus(tmp_path)
    first = review_template(store, manifest)[0]
    first.update(
        reviewer="test-human-1",
        reviewed_at=now(),
        attested_human=True,
        status="REVIEWED",
        label="NO_GUIDANCE",
        support=[],
    )
    bad = copy.deepcopy(first)
    bad["candidate_id"] = "unknown"
    with pytest.raises(Invalid):
        import_reviews(store, manifest, [first, bad])
    assert store.all("review") == []
    imported = import_reviews(store, manifest, [first])
    assert import_reviews(store, manifest, [first]) == imported
    second = copy.deepcopy(first)
    second.update(reviewer="test-human-2", label="AMBIGUOUS")
    import_reviews(store, manifest, [second])
    candidate = next(c for c in candidates(store, manifest) if c["id"] == first["candidate_id"])
    assert gold(store, candidate) == (None, True)
    assert len(store.all("review")) == 2


def test_llm_requires_real_request_identity_and_exact_support(tmp_path):
    store, manifest = corpus(tmp_path)
    request = llm_requests(store, manifest)[0]
    response = dict(
        request_id=request["request_id"],
        model="test-model",
        provider="test-provider",
        generated_at=now(),
        config={"temperature": 0},
        cost_usd=0.01,
        usage={"input_tokens": 20},
        answer=dict(
            label="RAISED",
            horizon="FY2025",
            numbers=None,
            support=[{"start": 0, "end": 4, "quote": "fake"}],
        ),
    )
    with pytest.raises(Invalid):
        import_llm(store, manifest, [response])
    assert not store.all("extraction_run")


@pytest.mark.parametrize(
    "basis",
    [
        "subscription",
        "segment",
        "constant-currency",
        "EPS",
        "margin",
        "bookings",
        "billings",
        "RPO",
        "non-GAAP",
        "organic",
    ],
)
def test_nonconsolidated_revenue_guidance_abstains(basis):
    answer = rules(f"Raises full year FY2025 {basis} revenue guidance.")
    assert answer["label"] == "AMBIGUOUS"
    assert answer["abstained"] is True
    assert answer["support"] == []


@pytest.mark.parametrize(
    "text",
    [
        "Raises Full Year FY25 Operating Cash Flow Growth Guidance.",
        "Raises FY2025 EPS guidance. Revenue grew 12% last year.",
        "Maintains next quarter margin outlook.",
    ],
)
def test_unrelated_guidance_is_a_difficult_negative(text):
    answer = rules(text)
    assert answer["label"] == "NO_GUIDANCE"
    assert answer["abstained"] is False
    assert answer["support"] == []


def test_horizon_and_numeric_guidance_must_be_supported():
    from forecast_lab.extraction import validate_answer

    text = "Raises FY2025 consolidated revenue guidance to USD 100 million."
    answer = dict(
        label="RAISED",
        horizon="FY2025",
        numbers=dict(
            low="100",
            high="100",
            unit="million",
            currency="USD",
            basis="consolidated_gaap_total_revenue",
        ),
        support=[dict(start=0, end=len(text), quote=text)],
    )
    validate_answer(answer, text)
    with pytest.raises(Invalid, match="Horizon"):
        validate_answer({**answer, "horizon": "FY2099"}, text)
    for field, value in (
        ("low", "99"),
        ("high", "999"),
        ("unit", "billion"),
        ("currency", "EUR"),
        ("low", "garbage"),
    ):
        with pytest.raises(Invalid):
            validate_answer({**answer, "numbers": {**answer["numbers"], field: value}}, text)


def test_evaluation_penalizes_wrong_horizon_and_spurious_numbers(tmp_path):
    # Deliberately synthetic annotations: software metrics, never human research labels.
    store = Store(tmp_path / "metrics.db")
    text = "Synthetic company raises FY2025 revenue guidance; FY2024 revenue was USD 100 million."
    ingest(store, text.encode(), metadata(text.encode()))
    protocol, _ = read_protocol(default_protocol())
    manifest = prepare_candidates(store, protocol)
    c = candidates(store, manifest)[0]
    review = review_template(store, manifest)[0]
    review.update(
        reviewer="software-test-1",
        reviewed_at=now(),
        attested_human=True,
        status="REVIEWED",
        label="RAISED",
        horizon="FY2025",
        numbers=None,
        support=[dict(start=0, end=len(text), quote=text)],
    )
    import_reviews(store, manifest, [review])
    prediction = {
        "candidate_id": c["id"],
        "label": "RAISED",
        "horizon": "FY2024",
        "numbers": dict(
            low="100",
            high="100",
            unit="million",
            currency="USD",
            basis="consolidated_gaap_total_revenue",
        ),
        "support": review["support"],
    }
    with store.transaction():
        run = store.put(
            "extraction_run", dict(manifest_id=manifest, status="RUN", predictions=[prediction])
        )
    metrics = evaluate_extraction(store, run, c["split"])["metrics"]
    assert metrics["citation_validity"] == 1
    assert metrics["horizon_accuracy"] == 0
    assert metrics["nullable_numeric_accuracy"] == 0
    assert metrics["failures"] == {"wrong_horizon": 1, "spurious_numeric_range": 1}


def test_missing_predictions_count_against_numeric_accuracy(tmp_path):
    # Artificial reviewed values exercise the metric denominator, not research ground truth.
    store = Store(tmp_path / "missing-numbers.db")
    text = "Raises FY2025 consolidated revenue guidance to USD 100 million. Synthetic example only."
    ingest(store, text.encode(), metadata(text.encode()))
    protocol, _ = read_protocol(default_protocol())
    manifest = prepare_candidates(store, protocol)
    candidate = candidates(store, manifest)[0]
    review = review_template(store, manifest)[0]
    review.update(
        reviewer="software-test-1",
        reviewed_at=now(),
        attested_human=True,
        status="REVIEWED",
        label="RAISED",
        horizon="FY2025",
        numbers=dict(
            low="100",
            high="100",
            unit="million",
            currency="USD",
            basis="consolidated_gaap_total_revenue",
        ),
        support=[dict(start=0, end=len(text), quote=text)],
    )
    import_reviews(store, manifest, [review])
    with store.transaction():
        run = store.put("extraction_run", dict(manifest_id=manifest, status="RUN", predictions=[]))
    metrics = evaluate_extraction(store, run, candidate["split"])["metrics"]
    assert metrics["numeric_count"] == 1
    assert metrics["numeric_accuracy"] == 0
    assert metrics["nullable_numeric_accuracy"] == 0
    assert metrics["failures"] == {"missing_prediction": 1}


def test_single_reviewer_unlocks_training_and_evaluation_without_rewriting_history(tmp_path):
    # Synthetic software fixtures only; these are not genuine human research labels.
    store = Store(tmp_path / "solo.db")
    text = "\n\n".join(
        f"Synthetic passage {i}: revenue discussion with enough context for annotation software checks."
        for i in range(30)
    )
    ingest(store, text.encode(), metadata(text.encode()))
    protocol, _ = read_protocol(default_protocol())
    legacy, _ = read_protocol(Path("research/protocols") / f"{protocol['supersedes']}.json")
    old_manifest = prepare_candidates(store, legacy)
    old_candidates = candidates(store, old_manifest)
    formerly_double = {c["span_id"] for c in old_candidates if c["second_review_required"]}
    assert formerly_double
    manifest = prepare_candidates(store, protocol)
    current = candidates(store, manifest)
    assert manifest != old_manifest
    assert {(c["span_id"], c["split"]) for c in current} == {
        (c["span_id"], c["split"]) for c in old_candidates
    }
    assert all(gold(store, c) == (None, False) for c in current)
    reviews = []
    for index, row in enumerate(review_template(store, manifest)):
        row.update(
            reviewer="Dakari",
            attested_human=True,
            reviewed_at=now(),
            status="REVIEWED",
            label="NO_GUIDANCE" if index % 2 else "AMBIGUOUS",
        )
        reviews.append(row)
    with pytest.raises(Invalid, match="another candidate manifest"):
        import_reviews(store, old_manifest, reviews)
    import_reviews(store, manifest, reviews)
    assert all(gold(store, c)[0] is not None for c in current)
    assert all(gold(store, c) == (None, False) for c in old_candidates)
    trained = store.get(extract_tfidf(store, manifest), "extraction_run")
    assert trained["status"] == "RUN"
    assert set(trained["training_review_ids"]) == {r["id"] for r in store.all("review")}
    result = evaluate_extraction(store, extract_rules(store, manifest), "train")
    assert result["status"] == "EVALUATED"
    assert result["gold_count"] == len(current)
    assert result["metrics"]["per_label"]["NO_GUIDANCE"]["recall"] == 1
    assert result["metrics"]["per_label"]["AMBIGUOUS"]["recall"] == 0
    # The same single-review action still cannot bypass the frozen historical policy.
    old_review = next(
        r for r in review_template(store, old_manifest) if r["second_review_required"]
    )
    old_review.update(
        reviewer="Dakari",
        attested_human=True,
        reviewed_at=now(),
        status="REVIEWED",
        label="NO_GUIDANCE",
    )
    import_reviews(store, old_manifest, [old_review])
    old_candidate = next(c for c in old_candidates if c["id"] == old_review["candidate_id"])
    assert gold(store, old_candidate) == (None, False)
    store.close()
