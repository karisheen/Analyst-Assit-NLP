# Revenue-guidance annotation guide — guidance-v2-single-reviewer

## Question and unit

What revision to **consolidated revenue guidance** does management explicitly state in this passage, and for which fiscal horizon? This is not the future slowdown label, sentiment, EPS guidance, or growth versus last year. The unit is one cited paragraph/list/table-context block. Review the complete block and source; do not supply knowledge from later disclosures.

## Labels

- `RAISED`: explicitly higher comparable revenue guidance for the same horizon.
- `LOWERED`: explicitly lower comparable revenue guidance for the same horizon.
- `MAINTAINED`: explicitly reiterated/reaffirmed/unchanged revenue guidance.
- `INITIATED`: first guidance for a horizon; never infer a raise merely because revenue grows.
- `NO_GUIDANCE`: no revenue-guidance revision statement. Realized revenue, EPS/margin guidance, product announcements, risk boilerplate, and historical growth are difficult negatives.
- `AMBIGUOUS`: missing horizon/context, withdrawal, incompatible bases, contradictory directions, incomplete table, unreadable characters, or no defensible direction. Abstention is valid.

Different directions for different horizons in one block are `AMBIGUOUS` under this single-answer task. Do not select the most favorable horizon. A table and prose conflict is `AMBIGUOUS`; cite both and explain. An explicit unchanged full-year forecast and newly initiated next-quarter forecast are distinct claims; do not collapse them into a raise.

## Exact support and numbers

`support` contains zero-based, end-exclusive Unicode offsets **within the candidate quote**, not the raw bytes or full parsed document. Every `quote` must exactly equal that substring. Include the revenue basis, direction, and horizon. Do not correct extraction silently; flag corruption and abstain. Source citation offsets separately locate the candidate in the immutable parser output. Neither flattened HTML tables nor PDF layout text guarantees semantic table alignment.

`horizon` preserves the source's explicit fiscal expression. `numbers` is null unless a single comparable revenue guidance range is supported. Otherwise use decimal-string `low`, `high`, `unit` (`million`, `billion`, `percent`, `units`), `currency`, and `basis`. Point estimates use equal endpoints. Do not compare EPS to revenue, constant currency to reported currency, quarter to year, or infer range direction from midpoint changes. Mixed endpoint changes require abstention. Preserve numeric and table failure comments even when the label is clear.

## Review procedure and policy identity

The active frozen protocol is **ffl-1.1.0**, identity `0ab10bdd199817f9706205f697fc6032e5f5f589ffe17e49cec63160b1b2d328`. Its extraction policy is `guidance-v2-single-reviewer`, with reviewer **Dakari**, `gold: single_human_review`, and `second_review_fraction: 0.0`. One genuine completed review by Dakari supplies gold; no second reviewer or adjudication gate applies to this package.

This is a new protocol identity, not an edit to the frozen predecessor `c00be1d921c79ec472bc6dc449692929936f58e6ab43b1190ce39521fd7bf5ba`. Preserve the historical `research/results/sec-fixture` run, its protocol, artifacts and any genuine reviews unchanged. Its historical subset-review rules still apply to historical replay. The active run is `research/results/sec-single-reviewer`, with new candidate and manifest identities. Never copy IDs, judgments or review records from an old package into the new one, even when passage text matches.

Follow [human-annotation-walkthrough.md](human-annotation-walkthrough.md) for runnable setup, first-ten progress checks, partial-batch export, import, correction and evaluation commands.

1. Prepare the active run before labeling. Preserve the generated `research/results/sec-single-reviewer/annotations.json` template; work only in `research/results/human-review/dakari.json`. Setup refuses to overwrite existing work. Reviewer identity is prefilled as `Dakari`, but labels remain null, status `UNREVIEWED`, and attestation false until genuine judgment.
2. Work blind to model predictions, scores and split membership. Do not open `extraction-rules.json`, model responses or evaluation artifacts while labeling. Leave candidate IDs, hashes, splits, guide identity and source citation unchanged. Do not use the split field to decide labels or select easier work; do not change its value. Every new `second_review_required` field remains false.
3. Only after reading and judging a candidate, keep `reviewer: Dakari`, record the actual UTC `reviewed_at`, and set `reviewer_type: human`, `attested_human: true`, `status: REVIEWED`; supply label, horizon, numbers, support and comment. Leave unread rows unreviewed and unattested.
4. Export only completed rows to a separate JSON array, including for the first ten. Derive `candidate_manifest_id` dynamically from the active `report.json`, then import with `python -m forecast_lab reviews-import`. Do not send the whole unfinished working file to the importer. Preserve each export and receipt.
5. Imported judgments are immutable. To correct your own review, create a separate JSON-array correction file with the same candidate identity and reviewer `Dakari`, set `supersedes` to the current review ID, record a genuinely later review time, and explain the correction. Import it with a new receipt; retain the original judgment and every revision. Do not rewrite working rows already imported, erase database records, or change labels to improve scores.

An attestation records the submitter's claim of human origin; software cannot authenticate that claim. Agents must not fill these fields pretending to be human. Single-human review is **not consensus**: independent inter-annotator agreement is **not measured**. An optional later self-recheck by Dakari is not independent review; a changed judgment follows the same immutable correction lineage.

## Sampling and splits

The 240-candidate target uses six deterministic search strata: directional candidate, numeric guidance, table context, ambiguity candidate, outlook candidate, and difficult-negative candidate. Search strata are not gold labels. Exact normalized duplicate text is removed across documents. Round-robin allocation redistributes scarce strata; the emitted manifest records actual counts. Entire company/fiscal-quarter groups are assigned chronologically to approximately 60/20/20 train/dev/test. Count imbalance is intentional: never split a disclosure group to force desired row counts. All 240 candidates receive one review by Dakari; none require another human. The small fixture's test split is not adequate for broad extraction claims.

The current package comes from SEC-hosted INTU, MANH and PAYC earnings exhibits under the documented [source-rights decision](source-rights.md). Do not import reviews or model responses from either the predecessor SEC package or the retired ADBE/CRM/NOW fixture. Release dates, SEC acceptance and current byte retrieval are distinct clocks. No candidate is certified original-vintage forecasting evidence merely because its source is EDGAR.

No model fitting on dev/test labels. No prompt tuning on final test labels. TF-IDF requires at least two human training classes. LLM requests are exported with exact request/prompt hashes; import real responses and provider/model/cost metadata, never renamed rule output. Historical LLM results may reflect pretraining exposure.

## Evaluation

Report per-label precision/recall/F1, fixed-label macro F1, abstentions, missing predictions, exact citation validity, exact human-supported span agreement, horizon accuracy, and numeric tuple accuracy with denominators. `numeric_accuracy` conditions on gold ranges and counts missing predictions as errors; `nullable_numeric_accuracy` compares every reviewed nullable tuple and penalizes spurious ranges on gold-null passages. Exact horizon/numeric tokens, units and currency must occur in the cited support, but programmatic citation validity is not semantic support. Pending/partial human coverage is explicit; no human gold means null performance metrics. Scores compare models against one human's judgments, not a consensus reference; independent inter-annotator agreement is unavailable. Preserve original reviews, correction lineage, historical disagreements and failed model runs. Finish annotation before opening model outputs or evaluating, so remaining labels are not influenced by scores. The first held-out evaluation is an immutable artifact, not permission to tune and overwrite the result.
