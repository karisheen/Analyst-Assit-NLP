import calendar
import importlib
from datetime import date, timedelta

import pytest

from forecast_lab.core import Invalid, dump, load, now
from forecast_lab.extraction import llm_requests
from forecast_lab.store import Store
from test_store import metadata

replay = importlib.import_module("forecast_lab.reproduce")


def test_replay_preserves_inputs_and_rejects_changed_corpus(tmp_path, monkeypatch):
    """Synthetic review/provider records exercise plumbing, never research ground truth."""
    protocol_path = replay.default_protocol()
    root = tmp_path / "synthetic-research"
    fixtures = root / "fixtures"
    fixtures.mkdir(parents=True)
    documents = []
    for index in range(6):
        year, quarter = 2023 + index // 4, index % 4 + 1
        month = quarter * 3
        end = date(year, month, calendar.monthrange(year, month)[1])
        known = (end + timedelta(days=25)).isoformat() + "T20:00:00Z"
        raw = (
            f"Synthetic source {index} for fiscal {year}Q{quarter}. Original revenue statement for software testing only; "
            "no prediction or measured financial evidence is supplied by this artificial corpus."
        ).encode()
        name = f"source-{index}.txt"
        (fixtures / name).write_bytes(raw)
        documents.append(
            {
                "path": name,
                **metadata(
                    raw,
                    source_id=f"synthetic-{index}",
                    fiscal_year=year,
                    fiscal_quarter=quarter,
                    period_end=end.isoformat(),
                    published_at=known,
                    published_date=known[:10],
                    retrieved_at=known,
                    version_available_at=known,
                ),
            }
        )
    manifest = fixtures / "manifest.json"
    dump(manifest, {"documents": documents})
    monkeypatch.setattr(replay, "research_root", lambda: root)
    output = tmp_path / "output"
    first = replay.reproduce(output, protocol_path)
    templates = load(output / "annotations.json")
    reviews = []
    for row in templates:
        if row["split"] == "test":
            reviews.append(
                {
                    **row,
                    "reviewer": "Dakari",
                    "attested_human": True,
                    "reviewed_at": now(),
                    "status": "REVIEWED",
                    "label": "NO_GUIDANCE",
                }
            )
    review_path = tmp_path / "synthetic-reviews.json"
    dump(review_path, reviews)
    store = Store(output / "fixture.sqlite")
    requests = llm_requests(store, first["candidate_manifest_id"])
    responses = [
        dict(
            request_id=r["request_id"],
            model="synthetic-test-not-provider",
            provider="software-test",
            generated_at=now(),
            cost_usd=0,
            usage={},
            config={"temperature": 0},
            answer=dict(label="NO_GUIDANCE", horizon=None, numbers=None, support=[]),
        )
        for r in requests
    ]
    store.close()
    response_path = tmp_path / "synthetic-responses.json"
    dump(response_path, responses)
    reviewed = replay.reproduce(output, protocol_path, review_path, response_path)
    assert reviewed["extraction"]["rules"]["status"] == "EVALUATED"
    assert reviewed["extraction"]["llm"]["evaluations"][0]["status"] == "EVALUATED"
    assert reviewed["human_review_count"] == len(reviews) > 0
    execution = load(output / "execution-manifest.json")
    assert execution["inputs"]["reviews"]["path"] == str(review_path)
    assert execution["inputs"]["llm-responses"]["path"] == str(response_path)
    fresh = replay.reproduce(tmp_path / "fresh", protocol_path, review_path, response_path)
    assert reviewed == fresh
    assert (
        replay.reproduce(output, protocol_path)["extraction"]["llm"]
        == reviewed["extraction"]["llm"]
    )
    documents[0]["expected_text"].append("Synthetic source 0")
    dump(manifest, {"documents": documents})
    with pytest.raises(Invalid, match="fresh output"):
        replay.reproduce(output, protocol_path)
    assert load(output / "report.json")["source_data_id"] == first["source_data_id"]
