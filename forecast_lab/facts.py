"""Source-backed revenue facts; fiscal relationships are explicit, never month-derived."""

from __future__ import annotations

import re
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, localcontext
from fractions import Fraction

from .core import Invalid, require, utc
from .store import Store, citation

UNIT_SCALES = {
    "units": Decimal("1"),
    "thousand": Decimal("1000"),
    "million": Decimal("1000000"),
    "billion": Decimal("1000000000"),
}


def source_documents(store: Store, fact: dict) -> dict[str, dict]:
    """Include both immutable source operands of a derived quarter."""
    operands = fact.get("derivation")
    sources = [operands["annual"], operands["nine_month"]] if operands else [fact]
    documents = {}
    for source in sources:
        identity = citation(store, source["span_id"])["document_id"]
        documents[identity] = store.get(identity, "document")
    return documents


def ordinal(year: int, quarter: int) -> int:
    if type(year) is not int or type(quarter) is not int or quarter not in (1, 2, 3, 4):
        raise Invalid("Explicit issuer fiscal year/quarter required")
    return year * 4 + quarter - 1


def amount(fact: dict) -> Decimal:
    try:
        if not isinstance(fact["value"], str) or not isinstance(fact["scale"], str):
            raise Invalid("Revenue and scale must be decimal strings")
        value, scale = Decimal(fact["value"]), Decimal(fact["scale"])
        if not value.is_finite() or not scale.is_finite() or value <= 0 or scale <= 0:
            raise Invalid("Revenue and scale must be positive and finite")
        with localcontext() as context:
            context.prec = len(value.as_tuple().digits) + len(scale.as_tuple().digits) + 2
            return value * scale
    except (InvalidOperation, TypeError) as exc:
        raise Invalid("Revenue must use decimal strings") from exc


def validate_source(store: Store, fact: dict) -> dict:
    require(
        fact,
        {
            "cik",
            "fiscal_year",
            "fiscal_quarter",
            "start",
            "end",
            "regime",
            "currency",
            "value",
            "scale",
            "span_id",
            "raw_token",
            "original",
            "authority_attestation",
            "reviewer",
            "known_at",
            "basis",
            "unit_support",
        },
    )
    if fact["original"] is not True or any(
        not isinstance(fact[key], str) or not fact[key].strip()
        for key in ("authority_attestation", "reviewer", "regime")
    ):
        raise Invalid("Original-vintage source review attestation required")
    if fact["basis"] != "consolidated_gaap_total_revenue" or not re.fullmatch(
        r"[A-Z]{3}", fact["currency"]
    ):
        raise Invalid("Unsupported basis or reporting currency")
    amount(fact)
    cited = citation(store, fact["span_id"])
    doc = store.get(cited["document_id"], "document")
    if doc["cik"] != fact["cik"] or doc["period_end"] != fact["end"] or doc["amended"]:
        raise Invalid("Revenue issuer/period/original source mismatch")
    if (doc["fiscal_year"], doc["fiscal_quarter"]) != (fact["fiscal_year"], fact["fiscal_quarter"]):
        raise Invalid("Fiscal mapping conflicts with disclosure metadata")
    raw_token = fact["raw_token"]
    if (
        not isinstance(raw_token, str)
        or not raw_token
        or not re.search(r"(?<![\d.,])" + re.escape(raw_token) + r"(?![\d.,])", cited["quote"])
    ):
        raise Invalid("Revenue token not supported by citation")
    token = raw_token.replace(",", "").replace("$", "").strip()
    try:
        if Decimal(token) != Decimal(fact["value"]):
            raise Invalid("Normalized value differs from cited token")
    except InvalidOperation as exc:
        raise Invalid("Revenue token is not numeric") from exc
    units = fact["unit_support"]
    require(units, {"span_id", "unit_token", "currency_token"})
    unit_cite = citation(store, units["span_id"])
    if unit_cite["document_id"] != cited["document_id"]:
        raise Invalid("Revenue units must cite the same source document")
    for key in ("unit_token", "currency_token"):
        token = units[key]
        if (
            not isinstance(token, str)
            or not token
            or not re.search(r"(?<!\w)" + re.escape(token) + r"(?!\w)", unit_cite["quote"], re.I)
        ):
            raise Invalid("Revenue unit/currency token not supported by citation")
    unit = units["unit_token"].lower().removesuffix("s")
    if unit == "unit":
        unit = "units"
    if UNIT_SCALES.get(unit) != Decimal(fact["scale"]):
        raise Invalid("Revenue scale differs from cited unit")
    currency = units["currency_token"].upper()
    if currency in ("US$", "U.S. DOLLARS", "US DOLLARS"):
        currency = "USD"
    if currency != fact["currency"]:
        raise Invalid("Revenue currency differs from cited currency")
    if utc(fact["known_at"]).date() <= date.fromisoformat(fact["end"]):
        raise Invalid("Revenue availability must follow the completed reporting period")
    if doc["version_available_at"] is None or utc(fact["known_at"]) != utc(
        doc["version_available_at"]
    ):
        raise Invalid("Revenue availability must equal verified original source availability")
    if doc["snapshot_status"] not in ("verified_original", "synthetic"):
        raise Invalid("Historical reconstruction is not original-vintage evidence")
    return doc


def import_fact(store: Store, fact: dict) -> str:
    require(
        fact,
        {
            "cik",
            "fiscal_year",
            "fiscal_quarter",
            "start",
            "end",
            "regime",
            "currency",
            "value",
            "scale",
            "span_id",
            "raw_token",
            "original",
            "authority_attestation",
            "reviewer",
            "known_at",
            "basis",
        },
    )
    ordinal(fact["fiscal_year"], fact["fiscal_quarter"])
    duration = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days + 1
    if (
        not 77 <= duration <= 105
        or not fact["regime"]
        or fact["basis"] != "consolidated_gaap_total_revenue"
    ):
        raise Invalid("Irregular quarter or unsupported revenue basis")
    if fact["original"] is not True or not fact["authority_attestation"] or not fact["reviewer"]:
        raise Invalid(
            "Original-vintage source review required, never inferred from current comparisons"
        )
    amount(fact)
    if fact.get("derivation"):
        operands = fact["derivation"]
        require(operands, {"annual", "nine_month", "explicit_q4_absent_attestation"})
        if operands["explicit_q4_absent_attestation"] is not True:
            raise Invalid(
                "Q4 subtraction is allowed only when explicit quarterly revenue is absent"
            )
        annual, nine_month = operands["annual"], operands["nine_month"]
        validate_source(store, annual)
        validate_source(store, nine_month)
        derived = derive_q4(annual, nine_month)
        for key in ("cik", "currency", "regime", "basis", "fiscal_year", "end", "span_id"):
            if fact[key] != annual[key]:
                raise Invalid("Derived Q4 differs from its original annual source")
        if (
            fact["fiscal_quarter"] != 4
            or fact["start"]
            != (date.fromisoformat(nine_month["end"]) + timedelta(days=1)).isoformat()
            or amount(fact) != amount(derived)
            or utc(fact["known_at"]) != utc(derived["known_at"])
        ):
            raise Invalid("Invalid derived Q4 value, period or availability")
    else:
        validate_source(store, fact)
    existing = [
        f
        for f in store.all("fact")
        if (f["cik"], f["fiscal_year"], f["fiscal_quarter"])
        == (fact["cik"], fact["fiscal_year"], fact["fiscal_quarter"])
    ]
    if any({k: v for k, v in f.items() if k != "id"} != fact for f in existing):
        raise Invalid("Conflicting original fact: adjudicate source outside frozen primary dataset")
    with store.transaction():
        return store.put("fact", fact)


def chain(
    store: Store,
    fact_ids: list[str],
    cik: str,
    year: int,
    quarter: int,
    include_outcome: bool = True,
) -> dict[int, dict]:
    facts = [store.get(identity, "fact") for identity in fact_ids]
    q = ordinal(year, quarter)
    indexed = {}
    for identity, fact in zip(fact_ids, facts):
        if fact["cik"] != cik:
            raise Invalid("Cross-company fiscal chain")
        offset = ordinal(fact["fiscal_year"], fact["fiscal_quarter"]) - q
        if offset in indexed:
            raise Invalid("Duplicate fiscal quarter")
        indexed[offset] = {"id": identity, **fact}
    end = 2 if include_outcome else 1
    if set(indexed) != set(range(-5, end)):
        raise Invalid("Need consecutive original quarters q-5 through q, plus q+1 for resolution")
    if len({f["currency"] for f in facts}) != 1 or len({f["regime"] for f in facts}) != 1:
        raise Invalid("Currency or fiscal regime comparability break")
    for offset in range(-4, end):
        if (
            date.fromisoformat(indexed[offset]["start"])
            - date.fromisoformat(indexed[offset - 1]["end"])
        ).days != 1:
            raise Invalid("Fiscal chain gap or overlap")
    for offset in range(-1, end):
        gap = (
            date.fromisoformat(indexed[offset]["end"])
            - date.fromisoformat(indexed[offset - 4]["end"])
        ).days
        if not 350 <= gap <= 378:
            raise Invalid("YoY quarter mapping is not a regular fiscal year")
    return indexed


def resolve_values(facts: dict[int, dict]) -> dict:
    current, prior = amount(facts[0]), amount(facts[-4])
    following, prior_following = amount(facts[1]), amount(facts[-3])
    return {
        "label": int(
            Fraction(following) * Fraction(prior) < Fraction(current) * Fraction(prior_following)
        ),
        "growth_q": str(current / prior - 1),
        "growth_next": str(following / prior_following - 1),
        "outcome_available_at": facts[1]["known_at"],
    }


def derive_q4(annual: dict, nine_month: dict) -> dict:
    """Explicit original FY minus original YTD operands; caller retains both citations."""
    for key in ("cik", "currency", "regime", "start", "basis", "fiscal_year"):
        if annual[key] != nine_month[key]:
            raise Invalid("Q4 operands have incompatible accounting scope")
    if annual["original"] is not True or nine_month["original"] is not True:
        raise Invalid("Q4 cannot combine restated operands")
    annual_days = (date.fromisoformat(annual["end"]) - date.fromisoformat(annual["start"])).days + 1
    nine_days = (
        date.fromisoformat(nine_month["end"]) - date.fromisoformat(nine_month["start"])
    ).days + 1
    if (
        annual["fiscal_quarter"] != 4
        or nine_month["fiscal_quarter"] != 3
        or not 350 <= annual_days <= 378
        or not 245 <= nine_days <= 294
    ):
        raise Invalid("Q4 operands must be original full-year and nine-month durations")
    annual_value, nine_value = amount(annual), amount(nine_month)
    with localcontext() as context:
        context.prec = (
            max(annual_value.adjusted(), nine_value.adjusted())
            - min(int(annual_value.as_tuple().exponent), int(nine_value.as_tuple().exponent))
            + 2
        )
        value = annual_value - nine_value
    days = (date.fromisoformat(annual["end"]) - date.fromisoformat(nine_month["end"])).days
    if value <= 0 or not 77 <= days <= 105:
        raise Invalid("Invalid Q4 subtraction")
    return {
        "value": str(value),
        "scale": "1",
        "operands": [annual, nine_month],
        "known_at": max(annual["known_at"], nine_month["known_at"], key=utc),
    }
