# Fundamental Forecast Lab

A point-in-time financial-disclosure research workflow, evolved from the historical Analyst Assist prototype.

> After a company reports earnings, does its contemporaneously available disclosure help forecast whether next-quarter year-over-year revenue growth will be lower than the just-reported quarter's growth?

**Engineering complete; human evaluation pending.** No forecasting improvement has been demonstrated. The offline engineering path works on six SEC-hosted earnings exhibits from **Intuit, Manhattan Associates, and Paycom**. These are **current historical reconstructions**, not certified release-time bytes. It prepares 240 unique, unreviewed annotation candidates and records an immutable development abstention plus revision. It does not manufacture human labels, LLM responses, historical fundamentals, or prospective forecasts.

**Source rights and publication boundary:** the active fixture relies on the SEC's explicit public-filing reuse policy, with attribution and documented exceptions—not merely public accessibility. See [source-rights.md](research/source-rights.md) for primary terms, rejected alternatives, AI-use limits and residual risks. This clean publication branch starts from the existing public history at `f421925`, without the restricted private commit `f1ad186` or its descendants. The retired Adobe/Salesforce/ServiceNow downloads and their history remain private and must never be pushed, bundled into a public release, or merged into this branch.

No stock-return prediction, trading profitability claim, document chat, broker integration, or autonomous execution.

## Reproduce from a fresh checkout

Python 3.12 and [uv](https://docs.astral.sh/uv/) are required for the locked entry command:

```bash
uv run --locked python -m forecast_lab reproduce --output research/results/sec-single-reviewer
```

The command initializes/reuses SQLite, ingests the bundled corpus, checks source hashes and citations, prepares annotations, runs rules, conditionally trains/evaluates extraction on genuine reviewed labels, evaluates data eligibility for A–D, appends development forecast/revision records, and emits JSON, a text audit, Markdown report, and calibration SVG. **The experiment itself makes no network calls.** First-time dependency installation may need internet; after `uv sync --locked`, use `uv run --offline --locked ...`.

Equivalent pip installation:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m forecast_lab reproduce --output research/results/sec-single-reviewer
```

The uv lock is the fully pinned dependency route. Pip honors direct pins but may resolve different transitive versions.

Run from a source checkout: the fixed corpus and default protocol remain in `research/`, not inside a standalone wheel. Editable installs resolve these assets relative to the checkout, including when the CLI is invoked from another working directory.

Generated artifacts:

| Artifact | Meaning |
|---|---|
| `fixture.sqlite` | Immutable documents, parses, spans, review/model artifacts, forecast/revision ledger |
| `report.json`, `report.md` | Counts, measured software output, explicit missing-evidence statuses |
| `annotations.json` | Single-reviewer package for Dakari; initially null labels and unattested, not ground truth |
| `llm-requests.json` | Hashed external LLM requests; no provider call is silently made |
| `extraction-*.json` | Rule results and text-model readiness/training identity |
| `forecasting.json` | A–D evaluation or an explicit insufficient-original-vintage-data result |
| `audit.json`, `audit.txt` | Exact quotes, hashes, timestamps, model/config, abstention and revision history |
| `calibration.svg` | Calibration when available; otherwise an explicit unavailable-evidence panel |
| `execution-manifest.json` | Protocol/data/source-tree/result identities, actual run timestamp, command |
| `ledger-integrity.json` | Local content-addressed integrity and ledger head manifest |

Re-running the same directory preserves records. `run-contract.json` binds it to the protocol, fixture manifest and Python source-tree identities; changed inputs/code require a **fresh output directory**, not deletion or rewriting of earlier evidence. `research/results/sec-single-reviewer` is the active run and CLI default under `ffl-1.1.0` / `guidance-v2-single-reviewer`. The previous `sec-fixture` run and frozen `ffl-1.0.0` protocol remain unchanged historical evidence; their candidate/review IDs must not be imported into the new package. Earlier `fixture` and `verified-fixture` runs remain private, ignored historical artifacts. The retired raw fixture and manifest remain in the ignored `research/results/retired-ir-fixture/original-fixture.tar.gz` and private Git history, not approved publication inputs. Fresh directories produce identical source/candidate/rule/scientific result identities, but truthful ledger creation times and event IDs differ. Never point fixture reproduction at a live prospective ledger.

## Frozen research contract

See [protocol](research/protocol.md), [machine-readable manifest](research/manifest.json), and [research note](research/research-note.md).

- Fixed, purposive **25-issuer enterprise/business application-software cohort**; CIK identities, including acquired issuers. Not a homogeneous SaaS universe or survivorship-free census.
- Target: `1[R(q+1)/R(q-3) < R(q)/R(q-4)]`, original consolidated GAAP revenue, exact decimal arithmetic, equality = no slowdown.
- Primary cutoff: first verified complete revenue release +24 elapsed hours. Prospective creation must occur within the following hour, using an actual system clock; date-only publication and uncertified source versions fail closed.
- Training 2020–2022; reserved calibration April–December 2023; validation April–December 2024; sealed holdout April 2025–December 2026. A 120-day training embargo and actual outcome-availability check both apply. No post-hoc calibration or refitting in this protocol. Final holdout reporting not before October 1, 2027.
- A: Laplace-smoothed sector rate. B: L2 logistic on reported and previous YoY growth. C: L2 logistic on frozen guidance flags. D: B+C. Training-only scaling; no verbal confidence mapping.
- Brier primary, bounded log loss, calibration counts, paired D−B comparison, independently resampled company/calendar-quarter clusters. Minimum sample/coverage gates prohibit a claim from the fixture.

Protocol files are named by canonical SHA-256. Never edit a frozen protocol in place. `protocol-freeze --input new-contract.json --output research/protocols` creates a new identity; old identities remain.

## Human review and external LLM workflow

For the complete manual procedure and copy-paste commands, follow [Human annotation: step-by-step walkthrough](research/human-annotation-walkthrough.md).

Read [annotation-guide.md](research/annotation-guide.md). **Dakari is the sole human annotator for all 240 candidates; no second reviewer is required.** The SEC fixture has 153 train, 17 dev and 70 test candidates, grouped by company/reporting quarter; 240 candidates is not 240 independent observations. Templates prefill `reviewer: "Dakari"` but leave labels null, status `UNREVIEWED` and human attestation false. One genuine completed review supplies each reference label. This is not consensus, and independent inter-annotator agreement is not measured. Flattened HTML tables, separated headings and segment-versus-consolidated revenue require particular care. Rule output is not a human label.

```bash
# Replace IDs with values from report.json / preceding command output.
forecast-lab reviews-import --db research/results/sec-single-reviewer/fixture.sqlite \
  --manifest-id MANIFEST_ID --input completed-human-reviews.json
forecast-lab extract-tfidf --db research/results/sec-single-reviewer/fixture.sqlite --manifest-id MANIFEST_ID
forecast-lab extraction-evaluate --db research/results/sec-single-reviewer/fixture.sqlite --id RUN_ID --split test
forecast-lab llm-import --db research/results/sec-single-reviewer/fixture.sqlite \
  --manifest-id MANIFEST_ID --input actual-provider-responses.json
```

Responses supply `request_id`, provider, exact model/version, actual `generated_at`, finite `cost_usd`, usage, nonempty inference `config` and structured `answer`; requests/schema are in `llm-requests.json`. No API credentials are required for export/import. External identities and human attestations are recorded as supplied, not independently authenticated. Historical LLM performance must acknowledge pretraining exposure.

Reproduction accepts `--reviews completed-human-reviews.json --llm-responses actual-provider-responses.json`, records their paths/content identities, and reports every matching imported LLM run rather than selecting a winner. Prior explicit imports in the same database also appear by artifact ID; retain the original input files for replay in a fresh directory.

## Live ingestion and forecasting inputs

`forecast-lab --help` lists the unified commands. `fetch --url URL --user-agent 'Project contact@example.org' --output raw-file` explicitly acquires at most 10 MB and writes a retrieval receipt; it never overwrites an existing file. Follow SEC fair-access rules and issuer terms. Ingestion takes the same manifest structure as [the fixture](research/fixtures/manifest.json). Supported parser inputs are PDF, explicitly bounded HTML, UTF-8 text, and JSON metadata. Preserve original SEC accession/form/exhibit identifiers in source metadata; do not substitute today's Company Facts value for an original vintage. Live broad SEC harvesting is intentionally not a background service.

`facts-import` accepts a JSON array of cited original revenue records; `observations-import` derives numeric/text features and resolved labels from their immutable IDs rather than accepting arbitrary feature vectors or labels. See typed implementation in `forecast_lab/facts.py` and `forecast_lab/forecasting.py` for field contracts. Missing fiscal mappings, original sources or outcome timestamps are rejected. Corporate-action effects stay in reported GAAP revenue; currency/regime changes and irregular/missing quarters are excluded. The bundled reconstruction corpus cannot be upgraded to original-vintage evidence merely by changing a timestamp.

## Ledger and reviewer interface

```bash
forecast-lab ledger-create --db research/live.sqlite --input forecast-request.json
forecast-lab ledger-revise --db research/live.sqlite --id FORECAST_ID --input revision.json
forecast-lab ledger-list-unresolved --db research/live.sqlite
forecast-lab ledger-resolve --db research/live.sqlite --id FORECAST_ID --input seven-original-fact-ids.json
forecast-lab ledger-verify --db research/live.sqlite
forecast-lab audit --db research/results/sec-single-reviewer/fixture.sqlite --id FORECAST_ID
```

`audit.json` contains a complete development request example under `forecast`; remove ledger-generated fields before submitting a new request. Non-abstaining forecasts must match a source-derived fitted model prediction. Resolution derives the label from seven consecutive original quarters; it does not accept an arbitrary binary outcome. Revisions cannot mutate prior forecasts or branch from an old tip. Historical, development and prospective classes are separate fields. Only still-open target quarters with verified source capture and a fresh authoritative unresolved-outcome attestation qualify for prospective creation. Unknown public-outcome status is not evidence of being unresolved.

SQLite triggers, hashes and an exported head manifest protect against accidental mutation. They are **not** trusted third-party timestamping or protection from a database owner replacing the entire file.

## Quality checks

```bash
uv run --locked --extra dev pytest -q
uv run --locked --extra dev ruff check forecast_lab tests
uv run --locked --extra dev ruff format --check forecast_lab tests
uv run --locked --extra dev mypy forecast_lab
```

Tests and synthetic A–D smoke runs establish implementation behavior, not predictive validity. The historical Newsgroups notebook and risk-scoring exports were removed from the primary tree after the new path ran; they remain in Git history at `f421925`. The repository has not been renamed.

Single-reviewer verification: **63 tests passed**, Ruff lint and formatting passed, MyPy passed for 12 source files. The actual offline CLI default generated all 240 candidates with reviewer `Dakari`, no second-review requirement and no human labels. A disposable synthetic CLI smoke exercised single-human imports and train/dev/test evaluation; the protected working-copy setup and progress checks also ran. The [research note](research/research-note.md) records the new protocol, evidence identities and prior verification history.

## Evidence gates

- **Human labels:** none supplied. Review the candidate package; agents are not human annotators.
- **LLM evidence:** no actual responses supplied. Import a real, versioned run to evaluate it.
- **Forecasting evidence:** no complete certified original-vintage training/validation revenue history bundled. No real A–D performance claim.
- **Prospective evidence:** zero genuine forecasts created by the fixture. A verified current issuance opportunity and eligible fitted model/source history are still needed; future outcomes cannot be backfilled.
- **Rights:** the SEC public-filing reuse and dissemination policies support this limited fixture under the [documented interpretation](research/source-rights.md); they are not issuer warranties or a blanket general-purpose AI-training licence. External provider retention/training terms need separate review. Reproduction never commits or publishes anything. The clean publication branch excludes the retired material; publication of the old private history remains prohibited.
