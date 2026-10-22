# Human annotation: step-by-step walkthrough

This is the practical walkthrough for **Dakari, the sole human annotator**, reviewing **240 SEC candidates**. No candidate in the active package requires another reviewer. The authoritative labeling rules remain in [annotation-guide.md](annotation-guide.md). Source-use boundaries are documented in [source-rights.md](source-rights.md).

You are labeling what management says about consolidated revenue guidance—not predicting future revenue slowdown. There is currently no annotation UI; this workflow uses JSON files and terminal commands.

## 1. Open the project and read the guide

In Terminal:

```bash
cd ~/Developer/personal/analyst-assist-nlp
```

Read `research/annotation-guide.md` before labeling anything.

**Do not open `extraction-rules.json`, model responses or score reports, or use an AI assistant to choose labels.** Your judgments must be independent of model predictions. Remain blind to split membership: do not inspect or use `split` to select candidates or decide judgments, and never alter it. Prepare the package before starting; do not run reproduction or extraction evaluation while labeling is underway.

## 2. Prepare the active package and one protected working copy

The active protocol is **ffl-1.1.0**, hash `0ab10bdd199817f9706205f697fc6032e5f5f589ffe17e49cec63160b1b2d328`, with guide `guidance-v2-single-reviewer`, reviewer `Dakari`, `gold: single_human_review`, and `second_review_fraction: 0.0`. It supersedes frozen protocol `c00be1d921c79ec472bc6dc449692929936f58e6ab43b1190ce39521fd7bf5ba`; it does not rewrite that protocol.

Preserve `research/results/sec-fixture`, all historical artifacts and any genuine old reviews unchanged. The new run is `research/results/sec-single-reviewer`. Candidate IDs and manifest identity are new: never copy IDs or judgments from an old package, even for matching passages. Historical subset-review rules remain historical only.

Run the following **once, before labeling**. If the active run is absent, it prepares it offline. If it already exists, it uses the existing template without rerunning reproduction. It refuses to overwrite `dakari.json`, and fails rather than resetting a damaged or incompatible package.

```bash
uv run --offline --locked python - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

root = Path("research/results/sec-single-reviewer")
working = Path("research/results/human-review/dakari.json")
if working.exists():
    raise SystemExit(f"Resume existing work; refusing to overwrite: {working}")
if not root.exists():
    subprocess.run(
        [sys.executable, "-m", "forecast_lab", "reproduce", "--output", str(root)],
        check=True,
    )
report = json.loads((root / "report.json").read_text())
if report["protocol_id"] != "0ab10bdd199817f9706205f697fc6032e5f5f589ffe17e49cec63160b1b2d328":
    raise SystemExit("Wrong protocol; preserve this run rather than relabeling it.")
rows = json.loads((root / "annotations.json").read_text())
if len(rows) != 240 or len({r["candidate_id"] for r in rows}) != 240:
    raise SystemExit("Expected 240 distinct candidates; do not repair IDs by hand.")
for row in rows:
    if (
        row["guide"] != "guidance-v2-single-reviewer"
        or row["second_review_required"] is not False
        or row["reviewer"] != "Dakari"
        or row["status"] != "UNREVIEWED"
        or row["attested_human"] is not False
        or row["label"] is not None
        or row["reviewed_at"] is not None
        or row["supersedes"] is not None
    ):
        raise SystemExit("Unexpected template; preserve it and investigate.")
working.parent.mkdir(parents=True, exist_ok=True)
with working.open("x") as handle:
    handle.write(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
print(f"{working}: {len(rows)} candidates; no judgments or attestations supplied")
PY
```

Work only in **`research/results/human-review/dakari.json`**, using a plain-text/code editor such as VS Code, not Word. Leave the generated `research/results/sec-single-reviewer/annotations.json` unchanged: reproduction regenerates it. If working files exist, resume them rather than recreating or deleting them. Reviewer identity is prefilled; that is not a completed human review.

These files live under ignored `research/results/`: Git does not back them up. Keep a separate private backup of the working file, immutable batch exports, corrections and import receipts. Do not publish source text or send it to an external model outside the source-rights and provider-use boundaries.

## 3. Understand one candidate

Each object in the JSON array is one candidate. The passage is `citation.quote`; its source is `citation.source_url`.

Leave these fields unchanged:

- `candidate_id`
- `candidate_hash`
- `citation` and everything inside it
- `guide`
- `split`
- `second_review_required`

For an initial review, leave `"supersedes": null`.

You will fill in the judgment and reviewer fields elsewhere in that object. Keep the surrounding JSON array and commas valid. JSON uses `null`, `true`, and `false`, not Python's `None`, `True`, and `False`.

## 4. Read the passage and its source when necessary

For each candidate:

1. Read `citation.quote`.
2. Open `citation.source_url` if you need surrounding context or table headings.
3. Locate the passage in that release.
4. Ask: **Does this passage explicitly state a revision to consolidated total revenue guidance, and for what fiscal period?**

Boundaries:

- Actual revenue growth is not a guidance revision.
- EPS, profit, margin and cash-flow guidance are not revenue guidance.
- Segment revenue is not automatically consolidated revenue.
- Do not consult later quarters to decide what the passage meant.
- Do not repair or expand `citation.quote`.

Source context can help you understand a passage, but support offsets must point inside the candidate quote. If the necessary horizon or meaning only exists outside the candidate and cannot be supported inside it, do not manufacture it. Flag the limitation and use `AMBIGUOUS` where appropriate.

## 5. Choose one label

| Label | Use when |
|---|---|
| `RAISED` | Management explicitly increases comparable consolidated revenue guidance for the same horizon. |
| `LOWERED` | Management explicitly decreases it. |
| `MAINTAINED` | Management explicitly reiterates or leaves it unchanged. |
| `INITIATED` | Management introduces guidance for a horizon. |
| `NO_GUIDANCE` | No revenue-guidance revision statement: historical results, unrelated metrics, boilerplate, etc. |
| `AMBIGUOUS` | Relevant guidance cannot be classified defensibly because of missing context, conflicting directions, incompatible bases, withdrawal or damaged/incomplete extraction. |

Do not use `AMBIGUOUS` merely because a passage is boring or contains unfamiliar accounting terms. Conversely, do not force a directional label when essential evidence is missing.

If one passage contains incompatible directions or different-horizon claims that cannot be represented by one answer, use `AMBIGUOUS` and explain.

## 6. Fill in horizon, numbers and comment

### Horizon

Copy the exact fiscal expression supported by the quote, for example:

```json
"horizon": "fiscal 2027"
```

Do not normalize it into wording absent from the passage. A supported horizon is mandatory for `RAISED`, `LOWERED`, `MAINTAINED`, and `INITIATED`. If there is no supported horizon, use `"horizon": null` and do not force a directional label.

### Numbers

Use `null` unless the passage supports a single comparable consolidated-revenue guidance range.

Illustrative structure only—not an answer to an actual candidate:

```json
"numbers": {
  "low": "100",
  "high": "110",
  "unit": "million",
  "currency": "USD",
  "basis": "consolidated_gaap_total_revenue"
}
```

- `low` and `high` are strings, not JSON numbers.
- Preserve the stated unit; do not silently convert millions into billions.
- A point estimate has equal endpoints.
- Endpoints, unit and currency must be supported by the cited text.
- For percentage guidance, use `"unit": "percent"` and `"currency": null`.
- Do not choose arbitrarily between incompatible ranges or infer a raise from a midpoint change.

### Comment

Write a brief reason, especially for ambiguity or source problems. Example—not a label for any actual candidate:

```json
"comment": "The passage reports historical revenue, not forward guidance."
```

## 7. Add exact supporting text

`support` is an array of objects with `start`, `end`, and `quote`. Offsets count Unicode characters in the decoded `citation.quote`, starting at zero; `end` is exclusive. They are not byte offsets or the full-document offsets in `citation`.

Use this helper rather than counting manually:

```bash
uv run --offline --locked python -c '
import json
from pathlib import Path

rows = json.loads(
    Path("research/results/human-review/dakari.json").read_text()
)
candidate_id = input("Paste candidate_id: ").strip()
row = next(r for r in rows if r["candidate_id"] == candidate_id)
text = row["citation"]["quote"]

print("\nCANDIDATE TEXT:\n" + text + "\n")
excerpt = input(
    "Paste one exact supporting excerpt, or press Enter for the whole candidate: "
)
if not excerpt:
    excerpt = text
if text.count(excerpt) != 1:
    raise SystemExit("Excerpt is absent or repeated; choose a unique exact excerpt.")

start = text.index(excerpt)
print(json.dumps(
    [{"start": start, "end": start + len(excerpt), "quote": excerpt}],
    indent=2,
    ensure_ascii=False
))
'
```

Copy the printed array into that candidate's `support` field.

- Prefer a sufficient, relevant excerpt containing the revenue basis, direction and horizon.
- The pasted excerpt prompt takes one line. For a required multiline passage, pressing Enter selects the whole candidate without losing line breaks.
- Whole-candidate support is valid when the whole passage is needed.
- For multiple excerpts, include multiple support objects.
- `NO_GUIDANCE` and `AMBIGUOUS` may have `"support": []`; explain the reasoning in `comment`.
- Any non-null horizon or numbers must occur in supported text, even for an ambiguous answer.

Do not change source text to make the helper accept an excerpt; whitespace, nonbreaking spaces and punctuation must match exactly.

## 8. Record reviewer identity and completion time

Only after finishing the candidate, set:

```json
"reviewer": "Dakari",
"reviewer_type": "human",
"attested_human": true,
"status": "REVIEWED"
```

Keep the exact identity `Dakari` throughout; do not use aliases or impersonate another reviewer. This is single-human review, not consensus. Independent inter-annotator agreement is not measured. An optional later self-recheck is not independent review.

Get the actual current UTC timestamp:

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

Paste that output as the string value of `reviewed_at`. Do not use the earnings-release date, invent a past review time or mark unread candidates reviewed.

Work in sessions of around 10–20 candidates. Save the file and leave unfinished rows `UNREVIEWED` with `attested_human: false`. After import, preserve that row exactly; later corrections go in separate revision files, not over the original answer.

## 9. Check the first ten and subsequent progress without scoring

```bash
uv run --offline --locked python - <<'PY'
import json
from pathlib import Path
from forecast_lab.core import now, utc
from forecast_lab.extraction import validate_answer

rows = json.loads(Path("research/results/human-review/dakari.json").read_text())
template = json.loads(
    Path("research/results/sec-single-reviewer/annotations.json").read_text()
)
expected = {r["candidate_id"]: r for r in template}
ids = [r["candidate_id"] for r in rows]
if len(ids) != len(set(ids)) or set(ids) != set(expected):
    raise SystemExit("Candidate set changed; preserve all original rows.")
completed = []
errors = []
for row in rows:
    try:
        original = expected[row["candidate_id"]]
        for field in (
            "candidate_hash", "citation", "guide", "split", "second_review_required"
        ):
            if row[field] != original[field]:
                raise ValueError(f"Immutable field changed: {field}")
        if row["reviewer"] != "Dakari" or row["reviewer_type"] != "human":
            raise ValueError("Reviewer must be Dakari, type human.")
        if row["status"] == "UNREVIEWED":
            if row["attested_human"] is not False:
                raise ValueError("Unfinished row must remain unattested.")
            continue
        if row["status"] != "REVIEWED" or row["attested_human"] is not True:
            raise ValueError("Completed row needs REVIEWED and genuine attestation.")
        if not row["reviewed_at"] or utc(row["reviewed_at"]) > utc(now()):
            raise ValueError("Use the actual non-future UTC review timestamp.")
        if row["supersedes"] is not None:
            raise ValueError("Keep corrections in separate revision files.")
        validate_answer(row, row["citation"]["quote"])
        completed.append(row)
    except Exception as exc:
        errors.append((row["candidate_id"], str(exc)))

print(f"Dakari: {len(completed)}/{len(rows)} structurally valid completed rows")
for candidate_id, error in errors:
    print(f"ERROR {candidate_id}: {error}")
if errors:
    raise SystemExit("Fix these errors before exporting.")
print("Structural checks passed; no model predictions or scores were inspected.")
PY
```

First-session target: **10/240**. Full target: **240/240**. These checks validate structure and exact textual support, not whether your interpretation is correct. Import adds identity and lineage checks. Do not fabricate a label, horizon or supporting text to make validation pass.

## 10. Export and import only genuinely completed rows

You may import the first ten, then further partial batches, without waiting for all 240. Never import the unfinished `dakari.json` directly.

Set these variables in the same Terminal session. The manifest is always read from the **current active report**, never copied from an old example:

```bash
export FFL_DB="research/results/sec-single-reviewer/fixture.sqlite"
export FFL_MANIFEST="$(uv run --offline --locked python -c '
import json
from pathlib import Path
print(json.loads(Path("research/results/sec-single-reviewer/report.json").read_text())["candidate_manifest_id"])
')"
export FFL_BATCH="research/results/human-review/batch-001"
```

For each later export choose a new directory, such as `batch-002`; do not reuse or delete an earlier batch. Run Step 9 first, then:

```bash
uv run --offline --locked python - <<'PY'
import json
import os
from pathlib import Path
from forecast_lab.core import now, utc
from forecast_lab.extraction import validate_answer

rows = json.loads(Path("research/results/human-review/dakari.json").read_text())
completed = [row for row in rows if row["status"] == "REVIEWED"]
if not completed:
    raise SystemExit("Nothing genuinely reviewed to export.")
for row in completed:
    if (
        row["reviewer"] != "Dakari"
        or row["reviewer_type"] != "human"
        or row["attested_human"] is not True
        or not row["reviewed_at"]
        or utc(row["reviewed_at"]) > utc(now())
        or row["supersedes"] is not None
    ):
        raise SystemExit("Incomplete initial review; rerun Step 9.")
    validate_answer(row, row["citation"]["quote"])
batch = Path(os.environ["FFL_BATCH"])
batch.mkdir()  # Refuses an existing directory; never overwrites a prior export.
with (batch / "dakari-completed.json").open("x") as handle:
    handle.write(json.dumps(completed, indent=2, ensure_ascii=False) + "\n")
print(f"Exported {len(completed)} completed rows to {batch}")
PY
```

Only if export succeeded, import the saved batch:

```bash
if [ -f "$FFL_BATCH/dakari-completed.json" ] && [ ! -e "$FFL_BATCH/import-receipt.json" ]; then
  uv run --offline --locked python -m forecast_lab reviews-import \
    --db "$FFL_DB" \
    --manifest-id "$FFL_MANIFEST" \
    --input "$FFL_BATCH/dakari-completed.json" \
    --output "$FFL_BATCH/import-receipt.json"
else
  printf '%s\n' "Missing export or existing receipt; refusing to overwrite."
fi
```

The receipt contains immutable `review_ids` in input order. Preserve it together with its exact export. Later cumulative exports may repeat unchanged initial reviews: identical reimports are idempotent. Do not edit a previously imported answer in `dakari.json`; use Step 12 for any changed judgment. If import fails, resolve the error without editing the database manually; preserve unsuccessful exports too. A corrected export uses a new batch directory.

**Do not evaluate yet.** Continue labeling without model outputs; imports and the next check do not require a second person.

## 11. Check usable single-human gold without model scores

```bash
uv run --offline --locked python - <<'PY'
import json
from pathlib import Path
from forecast_lab.store import Store
from forecast_lab.extraction import candidates, gold

root = Path("research/results/sec-single-reviewer")
manifest_id = json.loads((root / "report.json").read_text())["candidate_manifest_id"]
store = Store(root / "fixture.sqlite")
try:
    rows = candidates(store, manifest_id)
    usable = 0
    for candidate in rows:
        answer, conflict = gold(store, candidate)
        if answer is not None:
            usable += 1
        else:
            print("PENDING:", candidate["id"], "conflict=" + str(conflict))
    print(f"Usable human gold: {usable}/{len(rows)}")
    print("Policy: one genuine review by Dakari; independent agreement not measured.")
finally:
    store.close()
PY
```

After the first ten successful imports, expect **10/240** usable gold; unreviewed candidates are simply pending. After all reviews and any corrections, the target is **240/240**, with no second-review gate. A conflict is not an instruction to recruit or invent another reviewer: check the package identity and preserved records, and do not overwrite history.

## 12. Correct your own judgment with immutable lineage, if necessary

Skip this step if no judgment needs correction. A self-recheck is optional and is not independent agreement.

1. Re-read the original passage and guide, without using model predictions as the answer.
2. Preserve `dakari.json`, original batch exports and receipts unchanged.
3. Create a new directory, for example `research/results/human-review/correction-001`, and a JSON-array file `dakari-correction.json` inside it. Copy only the candidate row needing correction, retaining its identity fields; make your genuine correction.
4. Keep `reviewer: Dakari`, `reviewer_type: human`, `status: REVIEWED`, and a truthful human attestation. Set `supersedes` to the current review ID for that candidate: the matching position in the initial batch receipt, or the latest correction receipt if already revised.
5. Set a new actual UTC `reviewed_at`, strictly later than its parent, and explain why the answer changed in `comment`. Do not backdate.
6. Import the correction below, then repeat Step 11. Use a new numbered directory and receipt for every later correction. Never submit two revisions of the same candidate in one import; import parent before child.

```bash
export FFL_CORRECTION="research/results/human-review/correction-001"
if [ -f "$FFL_CORRECTION/dakari-correction.json" ] && [ ! -e "$FFL_CORRECTION/import-receipt.json" ]; then
  uv run --offline --locked python -m forecast_lab reviews-import \
    --db "$FFL_DB" \
    --manifest-id "$FFL_MANIFEST" \
    --input "$FFL_CORRECTION/dakari-correction.json" \
    --output "$FFL_CORRECTION/import-receipt.json"
else
  printf '%s\n' "Missing correction or existing receipt; refusing to overwrite."
fi
```

Only your own current review can be superseded. Never erase original judgments, rename yourself to create another vote, or manufacture consensus. If a needed correction becomes apparent after score inspection, preserve the original evaluation and explicitly record that exposure with the correction; do not present the revised result as untouched holdout evidence.

## 13. Finish annotation, then evaluate and reproduce

Before opening predictions or scores:

- [ ] All 240 candidates have Dakari's genuine review.
- [ ] Step 9 passes and all completed rows have been imported successfully.
- [ ] Step 11 reports **240/240** usable single-human gold.
- [ ] Initial reviews, batch exports, receipts and any correction lineage are preserved and privately backed up.
- [ ] No model predictions were used to manufacture human labels.

If you stop short of 240, keep pending coverage explicit. Do not call partial scores final held-out performance or inspect scores while intending to continue blind annotation.

After reaching the checkpoint, preserve the current generated artifacts before reproduction updates its report and templates. This snapshots the closed SQLite database too; do not run concurrent imports while copying:

```bash
uv run --offline --locked python - <<'PY'
import shutil
from pathlib import Path

source = Path("research/results/sec-single-reviewer")
destination = Path("research/results/human-review/before-evaluation-001")
shutil.copytree(source, destination)  # Refuses an existing snapshot.
print(f"Preserved pre-evaluation run: {destination}")
PY
```

Only after the snapshot succeeds, reproduce the active run:

```bash
uv run --offline --locked python -m forecast_lab reproduce \
  --output research/results/sec-single-reviewer
```

This retains imported reviews in the existing database, including correction history, regenerates the untouched annotation template, and evaluates rules and TF-IDF against available single-human gold. It does not read or overwrite `research/results/human-review/dakari.json`. No `--reviews` flag is needed because completed reviews were already imported. Do not pass the unfinished working file to reproduction.

Now inspect `research/results/sec-single-reviewer/report.json`: extraction statuses, per-label scores, support/horizon/numeric accuracy and coverage denominators are under `extraction`. Full review coverage does not guarantee a runnable TF-IDF baseline: at least two genuine training classes are required. Do not invent labels to satisfy that requirement. LLM metrics remain unavailable without actual provider responses; do not substitute rule outputs.

The default extraction evaluation is on the held-out test split. Preserve this first evaluated run with another non-overwriting snapshot (use `after-evaluation-001` as the destination in the copy command) before any subsequent rerun or correction. Never tune models or prompts on final test labels, or change labels to improve scores. Independent inter-annotator agreement is **not measured**; this is one human's reference, not consensus.

For a **clean replay**, keep the original run and backups. Reproduce into a fresh directory such as `research/results/sec-single-reviewer-replay-001`; point `FFL_DB` to that directory's `fixture.sqlite` and derive `FFL_MANIFEST` from its `report.json`, exactly as in Step 10. Replay preserved initial batch exports in order, then correction files in parent-before-child order, using fresh receipt locations rather than overwriting originals. Run reproduction again in that replay directory after all imports. Do not combine parent and child revisions into one `--reviews` array or change their timestamps. If a run-contract mismatch occurs, preserve that run and use a fresh directory; never delete the contract or bypass its identity check.

Good extraction scores do not establish forecasting value. Reproduction may still report forecasting/source-evidence gates or unavailable metrics unrelated to human annotation; `--require-evidence` is not a single-reviewer annotation completion check.

**First session: complete ten candidates in `dakari.json`, run Step 9, export/import those ten with Step 10, and check Step 11. Then continue the same workflow to all 240 without opening model outputs.**
