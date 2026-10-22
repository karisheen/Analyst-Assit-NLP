import pytest

from forecast_lab.audit import inspect_forecast
from forecast_lab.core import Invalid
from forecast_lab.ledger import create, revise, unresolved, verify_ledger
from forecast_lab.protocol import read_protocol
from forecast_lab.reproduce import default_protocol, fixture_request
from forecast_lab.store import Store, ingest
from test_store import RAW, metadata


def setup(tmp_path):
    store = Store(tmp_path / "ledger.db")
    doc = ingest(store, RAW, metadata(RAW))
    protocol, _ = read_protocol(default_protocol())
    return store, protocol, fixture_request(store, protocol, doc)


def test_immutable_revision_lineage_and_audit(tmp_path):
    store, protocol, request = setup(tmp_path)
    root = create(store, protocol, request)
    child = revise(store, protocol, root, {"revision_reason": "Keep abstention after source audit"})
    assert unresolved(store) == [child]
    audit = inspect_forecast(store, child)
    assert [r["id"] for r in audit["revision_history"]] == [root, child]
    assert audit["forecast"]["created_at"] > audit["revision_history"][0]["created_at"]
    assert audit["forecast"]["probability"] is None
    assert audit["score"] is None
    with pytest.raises(Invalid, match="current tip"):
        revise(store, protocol, root, {"revision_reason": "Illegal branch"})
    assert verify_ledger(store)["counts"]["forecast_event"] == 2


def test_no_backdating_fake_probability_or_prospective_relabel(tmp_path):
    store, protocol, request = setup(tmp_path)
    for updates in (
        {"created_at": "2024-05-30T20:00:00Z"},
        {"probability": 0.7, "abstained": False},
        {"evidence_class": "prospective"},
        {"information_cutoff": "2099-01-01T00:00:00Z"},
    ):
        with pytest.raises(Invalid):
            create(store, protocol, {**request, **updates})
    assert not store.all("forecast_event")


def test_citations_cannot_cross_company_or_cutoff(tmp_path):
    store, protocol, request = setup(tmp_path)
    later = ingest(
        store,
        RAW,
        metadata(
            RAW,
            source_id="future",
            published_at="2024-06-01T20:00:00Z",
            retrieved_at="2024-06-02T00:00:00Z",
            published_date="2024-06-01",
            version_available_at="2024-06-01T20:00:00Z",
        ),
    )
    with pytest.raises(Invalid, match="after cutoff"):
        create(store, protocol, {**request, "document_ids": [later]})


def test_prospective_requires_fresh_identified_outcome_attestation(tmp_path, monkeypatch):
    store = Store(tmp_path / "prospective-test.db")
    doc = ingest(store, RAW, metadata(RAW, snapshot_status="verified_original"))
    protocol, _ = read_protocol(default_protocol())
    # Controlled software clock/source only; never a research/prospective issuance.
    protocol["frozen_at"] = "2024-01-01T00:00:00Z"
    monkeypatch.setattr("forecast_lab.ledger.now", lambda: "2024-05-30T20:30:00Z")
    request = fixture_request(store, protocol, doc)
    check = dict(
        attested_by="software-test",
        source_urls=["https://example.com/release"],
        checked_at="2024-05-30T20:00:00Z",
        outcome_public=False,
    )
    request.update(evidence_class="prospective", unresolved_check=check)
    for updates in (
        {"attested_by": ""},
        {"attested_by": " "},
        {"source_urls": [""]},
        {"source_urls": "https://example.com"},
        {"source_urls": ["http://example.com"]},
        {"checked_at": "2024-05-30T18:00:00Z"},
        {"outcome_public": True},
    ):
        with pytest.raises(Invalid):
            create(store, protocol, {**request, "unresolved_check": {**check, **updates}})
    assert not store.all("forecast_event")
    event = create(store, protocol, request)
    recorded = store.get(event)
    assert recorded["created_at"] == "2024-05-30T20:30:00Z"
    assert recorded["information_cutoff"] == request["information_cutoff"]
    assert recorded["evidence_class"] == "prospective"


def test_reconstructed_historical_bytes_cannot_be_prospective(tmp_path):
    store = Store(tmp_path / "reconstructed.db")
    doc = ingest(
        store,
        RAW,
        metadata(RAW, snapshot_status="historical_reconstruction", version_available_at=None),
    )
    protocol, _ = read_protocol(default_protocol())
    request = fixture_request(store, protocol, doc)
    with pytest.raises(Invalid, match="verified original"):
        create(store, protocol, {**request, "evidence_class": "prospective"})
