from copy import deepcopy

import pytest

from forecast_lab.core import Invalid, digest, utc
from forecast_lab.protocol import read_protocol, split_for, validate
from forecast_lab.reproduce import default_protocol

PROTOCOL_PATH = default_protocol()


def test_frozen_identity_order_and_semantic_change():
    protocol, identity = read_protocol(PROTOCOL_PATH)
    assert digest(dict(reversed(list(protocol.items())))) == identity
    changed = deepcopy(protocol)
    changed["metrics"]["minimum_practical_improvement"] = 0.01
    assert validate(changed) != identity


def test_schema_and_split_boundaries():
    protocol, _ = read_protocol(PROTOCOL_PATH)
    assert split_for(protocol, "2023-01-01T00:00:00Z") == "excluded_gap_or_outside_window"
    assert split_for(protocol, "2025-04-01T00:00:00Z") == "holdout"
    with pytest.raises(Invalid):
        utc("2024-01-01T00:00:00")
    changed = deepcopy(protocol)
    changed["cohort"][1]["cik"] = changed["cohort"][0]["cik"]
    with pytest.raises(Invalid):
        validate(changed)
    changed = deepcopy(protocol)
    changed["splits"]["validation"][0] = "2022-01-01T00:00:00Z"
    with pytest.raises(Invalid):
        validate(changed)


def test_freeze_assigns_actual_time_without_rewriting_existing_protocol(tmp_path):
    from forecast_lab.core import dump, now
    from forecast_lab.protocol import freeze

    original_bytes = PROTOCOL_PATH.read_bytes()
    protocol, original_id = read_protocol(PROTOCOL_PATH)
    protocol["frozen_at"] = "2000-01-01T00:00:00Z"
    source = tmp_path / "input.json"
    dump(source, protocol)
    before = utc(now())
    identity = freeze(source, tmp_path / "frozen")
    after = utc(now())
    frozen, loaded_id = read_protocol(tmp_path / "frozen" / f"{identity}.json")
    assert before <= utc(frozen["frozen_at"]) <= after
    assert loaded_id == identity != original_id
    assert PROTOCOL_PATH.read_bytes() == original_bytes
