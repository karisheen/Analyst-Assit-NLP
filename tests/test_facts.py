from copy import deepcopy
from decimal import Decimal

import pytest

from forecast_lab.core import Invalid
from forecast_lab.facts import amount, derive_q4, import_fact, source_documents
from forecast_lab.store import Store, ingest
from test_store import metadata


def source_fact(
    store,
    *,
    quarter=4,
    start="2024-01-01",
    end="2024-12-31",
    value="1000",
    known="2025-01-25T00:00:00Z",
    **updates,
):
    raw = (
        f"Synthetic original consolidated GAAP total revenue was USD {value} million for the period "
        f"{start} through {end}. Software fixture only, not empirical financial evidence."
    ).encode()
    doc_id = ingest(
        store,
        raw,
        metadata(
            raw,
            source_id=f"synthetic-{start}-{end}-{value}",
            fiscal_year=2024,
            fiscal_quarter=quarter,
            period_end=end,
            published_at=known,
            published_date=known[:10],
            retrieved_at=known,
            version_available_at=known,
        ),
    )
    parse = next(p for p in store.all("parse") if p["document_id"] == doc_id)
    span = next(s for s in store.all("span") if s["parse_id"] == parse["id"])
    return dict(
        cik="0001108524",
        fiscal_year=2024,
        fiscal_quarter=quarter,
        start=start,
        end=end,
        value=value,
        scale="1000000",
        currency="USD",
        regime="calendar",
        span_id=span["id"],
        raw_token=value,
        unit_support=dict(span_id=span["id"], unit_token="million", currency_token="USD"),
        original=True,
        authority_attestation="Synthetic original-source attestation",
        reviewer="software-test",
        known_at=known,
        basis="consolidated_gaap_total_revenue",
        **updates,
    )


def test_q4_import_preserves_both_cited_operands(tmp_path):
    store = Store(tmp_path / "q4.db")
    annual = source_fact(store)
    nine = source_fact(
        store, quarter=3, end="2024-09-30", value="700", known="2024-10-25T00:00:00Z"
    )
    derived = derive_q4(annual, nine)
    q4 = {
        **annual,
        "start": "2024-10-01",
        "value": derived["value"],
        "scale": "1",
        "derivation": {
            "annual": annual,
            "nine_month": nine,
            "explicit_q4_absent_attestation": True,
        },
    }
    identity = import_fact(store, q4)
    assert import_fact(store, q4) == identity
    stored = store.get(identity, "fact")
    assert amount(stored) == Decimal("300000000")
    assert stored["known_at"] == annual["known_at"]
    assert len(source_documents(store, stored)) == 2
    assert stored["derivation"]["nine_month"]["span_id"] == nine["span_id"]
    for key, value in (
        ("start", "2024-09-30"),
        ("value", "301000000"),
        ("known_at", nine["known_at"]),
    ):
        with pytest.raises(Invalid):
            import_fact(store, {**q4, key: value})
    mismatched = deepcopy(q4)
    mismatched["derivation"]["nine_month"]["fiscal_year"] = 2023
    with pytest.raises(Invalid):
        import_fact(store, mismatched)
    mismatched = deepcopy(q4)
    mismatched["derivation"]["nine_month"]["span_id"] = annual["span_id"]
    with pytest.raises(Invalid):
        import_fact(store, mismatched)
    for absent in ("", "false", "true", 1, False):
        with pytest.raises(Invalid):
            import_fact(
                store,
                {
                    **q4,
                    "derivation": {**q4["derivation"], "explicit_q4_absent_attestation": absent},
                },
            )


@pytest.mark.parametrize(
    "updates",
    [
        {"scale": "1000000000"},
        {"scale": "0"},
        {"value": "NaN"},
        {"value": "Infinity"},
        {"value": 1000},
        {"currency": "EUR"},
        {"basis": "subscription_revenue"},
        {"cik": "0000796343"},
        {"end": "2024-12-30"},
        {"fiscal_year": 2025},
        {"reviewer": " "},
        {"authority_attestation": ""},
        {"original": False},
        {"known_at": "2024-12-01T00:00:00Z"},
        {"span_id": "missing"},
        {"raw_token": "100"},
    ],
)
def test_invalid_fact_provenance_fails_closed(tmp_path, updates):
    store = Store(tmp_path / "bad.db")
    fact = source_fact(store, start="2024-10-01")
    with pytest.raises(Invalid):
        import_fact(store, {**fact, **updates})
    assert store.all("fact") == []


def test_q4_subtraction_preserves_decimal_precision():
    annual = dict(
        cik="x",
        currency="USD",
        regime="calendar",
        basis="consolidated_gaap_total_revenue",
        fiscal_year=2024,
        fiscal_quarter=4,
        start="2024-01-01",
        end="2024-12-31",
        value="100000000000000000000000000001",
        scale="1",
        original=True,
        known_at="2025-01-25T00:00:00Z",
    )
    nine = {
        **annual,
        "fiscal_quarter": 3,
        "end": "2024-09-30",
        "value": "2",
        "known_at": "2024-10-25T00:00:00Z",
    }
    assert Decimal(derive_q4(annual, nine)["value"]) == Decimal("99999999999999999999999999999")
