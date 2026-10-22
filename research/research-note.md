# Fundamental Forecast Lab — first engineering slice

## Question and evidence boundary

Does contemporaneously available earnings disclosure add information about next-quarter YoY revenue-growth slowdown beyond simple fundamentals? This run builds and exercises the research path. It **does not answer that empirical question yet**.

The sector/base-rate forecast could make the system unnecessary; the primary incremental comparison is combined numeric+text versus numeric-only. Better extraction, a calibrated probability, or an implementation test does not establish profitable trading.

## Available information and sources

The active corpus contains six SEC-hosted 8-K earnings exhibits, two consecutive reporting periods for each of three existing frozen-cohort issuers:

| Issuer | Fiscal periods | SEC exhibits |
|---|---|---|
| Intuit (INTU) | FY2024 Q3, ended April 30; Q4, ended July 31 | [Q3](https://www.sec.gov/Archives/edgar/data/896878/000089687824000024/fy24q3earningspressrelease.htm), [Q4](https://www.sec.gov/Archives/edgar/data/896878/000089687824000035/fy24q4earningspressrelease.htm) |
| Manhattan Associates (MANH) | 2024 Q1, ended March 31; Q2, ended June 30 | [Q1](https://www.sec.gov/Archives/edgar/data/1056696/000095017024046886/manh-ex99_1.htm), [Q2](https://www.sec.gov/Archives/edgar/data/1056696/000095017024085622/manh-ex99_1.htm) |
| Paycom (PAYC) | 2024 Q1, ended March 31; Q2, ended June 30 | [Q1](https://www.sec.gov/Archives/edgar/data/1590955/000095017024051272/payc-ex99_1.htm), [Q2](https://www.sec.gov/Archives/edgar/data/1590955/000095017024088567/payc-ex99_1.htm) |

Selection was based on the documented SEC reuse channel, existing cohort membership, consecutive quarters and earnings/guidance content—not forecast outcomes or extraction performance. This replaces the restricted ADBE/CRM/NOW working-tree fixture; it does not redefine the cohort. [Source rights](source-rights.md) records primary policy quotations, rejected SEDAR+/Companies House channels, attribution and residual risks. Issuer-authored releases are not represented as government-authored works or universally public domain.

The manifest retains raw hashes, actual retrieval times, fiscal labels, accession/exhibit identifiers, source URLs, explicit HTML body boundaries and separate SEC acceptance evidence. Six retained SEC submission-header files substantiate acceptance and accession metadata. External image assets were not acquired. [Intuit's Q3 release page](https://investors.intuit.com/news-events/press-releases/detail/1188/intuit-reports-strong-third-quarter-results-and-raises-full-year-guidance) displays **May 23, 2024 4:00pm EDT**; only that factual timestamp and URL are recorded, not the issuer-site document. Other release clocks remain null rather than inferred from acceptance or midnight.

**Current retrieval does not prove those bytes existed at historical forecast time.** All six versions remain `historical_reconstruction`, with null verified version availability. Acceptance is not first website publication. No final holdout outcome dataset was used for selection, fitting or evaluation.

## Frozen design

[Protocol](protocol.md) freezes 25 CIKs, original consolidated GAAP revenue slowdown, release+24h cutoff, corporate-action and fiscal rules, 2020–2026 chronological partitions, training embargo and known-label predicate, A–D models, metrics, dependence treatment and evidence minimums. Active protocol `ffl-1.1.0` has identity `0ab10bdd199817f9706205f697fc6032e5f5f589ffe17e49cec63160b1b2d328`, superseding the preserved `ffl-1.0.0` solely to make Dakari the single human annotator before human review began. No label definitions, sampling, splits or forecasting design changed.

Label = 1 only if next-quarter original YoY growth is strictly lower; exact ties are 0. Acquisition effects stay in reported revenue. Amendments do not overwrite originals. Currency/regime breaks, missing quarters and uncertified sources fail closed. Original revenue facts require exact cited tokens and source-review attestation.

## Observed implementation output

The SEC fixture ingested six documents and produced **6,591 parsed spans**. The unchanged sampler prepared **240 unique unreviewed candidates**: 153 train, 17 development and 70 held-out, grouped by issuer/reporting quarter. All 240 now require only Dakari's genuine review; **zero require a second reviewer**. The previous policy's 39-candidate second-review subset remains historical, not an active gate. Search strata: 123 difficult-negative candidates, 44 table-context blocks, 30 ambiguity candidates, 26 numeric-guidance candidates, 13 directional candidates and 4 outlook candidates. These are sampling descriptors, not reviewed labels. Single-reviewer reference labels do not establish consensus or independent inter-annotator agreement.

Unchanged rule output: **233 `NO_GUIDANCE`, 7 `AMBIGUOUS`**. No extraction accuracy is inferred from these counts. Flattened SEC HTML tables and separated headings create many short spans; nearby source context is essential for human interpretation. Rules were not tuned to produce more attractive labels on the replacement corpus. Human review count is zero; held-out precision/recall/F1 and numeric accuracy remain null. TF-IDF is `NOT_FIT`; the external LLM path has no actual responses and is `NOT_RUN`.

The development ledger emitted an abstention and an immutable linked revision for INTU FY2024 Q4, with actual current creation timestamps and simulated cutoff **2024-05-24T20:00:00+00:00**, 24 hours after the publisher's stated release time. Its target period is May 1–July 31, 2024. The audit displays exact supporting-context passages, hashes, offsets, SEC source IDs, separate publication/retrieval timing, missing evidence, model/config identity and revision lineage. No probability was invented.

Earlier synthetic A–D smoke evidence and the retired fixture's results remain historical software evidence only. They are not rerun financial findings, and are not pooled with this new corpus. Old candidate identities and reviews must not be imported into the replacement package.

## Forecasting results and uncertainty

There are **zero eligible original-vintage real forecasting observations**, zero real fitted forecasting models and zero scored real forecasts in the fixture. Brier/log-loss/calibration and comparative intervals are unavailable, not zero. The real experiment is `INSUFFICIENT_ORIGINAL_VINTAGE_DATA`.

When eligible data exists, repeated snippets do not become separate outcomes. Evaluation uses one primary company-quarter observation and paired company/calendar-quarter pigeonhole resampling. Even then, sparse blocks, purposive cohort selection, historical model exposure and dependence across adjacent blocks limit claims. Minimum-count gates cannot be satisfied by generating more bootstrap draws.

## Failures and representative audit cases

1. **Historical byte leakage prevention:** even accession-linked SEC exhibits retrieved now remain reconstructions. Neither administrative acceptance nor an issuer's asserted release clock certifies the current raw bytes at the historical cutoff.
2. **Revenue-basis/context risk:** the INTU audit includes a segment-guidance heading and a separate consolidated-revenue range. Segment versus consolidated revenue, past growth versus revised guidance, and detached horizon headings need independent human review; machine citation validity does not solve those semantic distinctions.
3. **Correct abstention:** the fixture lacks certified original-vintage training data and reviewed extraction labels. The ledger records null probability, missing evidence and a linked continued-abstention revision instead of guessed confidence.
4. **Retrieval/parser limits:** the reader's SEC archive adapter returned company summaries for accession URLs; declared-user-agent HTTPS retrieval acquired actual exhibit bytes instead. No summary was substituted as a source document. The existing HTML parser creates many fragmented table spans; this migration does not establish semantic table fidelity.

A useful belief revision and an overreaction cannot honestly be established from unresolved, unreviewed development examples. Those empirical example categories remain pending; no manufactured financial success/failure examples are claimed.

## Prospective status

**Zero genuine prospective forecasts created.** The corpus is historical, no current eligible original-source issuance bundle is supplied, and the original-vintage training sample does not exist. A current timestamp on an old forecast would not fix this. The ledger path supports prospective creation checks, but calendar-time evidence has not begun. A genuine forecast ultimately resolves from the original reported revenue for its target quarter plus the preserved original comparison quarters.

## Reproduction and next evidence

```bash
uv run --locked python -m forecast_lab reproduce --output research/results/sec-single-reviewer
```

The fixed-corpus command has been exercised; runtime records are truthful, while source/candidate/result identities are deterministic. See generated `execution-manifest.json` for exact source-tree hash, protocol/data/result identities and command. No private credentials or live downloads are used by reproduction. Human review should use `annotations.json` and [the guide](annotation-guide.md), not model predictions as gold.

Next: Dakari completes human review of the fixed candidates, blind to model predictions, using `research/results/human-review/dakari.json` and the walkthrough. Audit original-source availability/fiscal mappings and acquire eligible original-vintage fundamentals before any final forecasting comparison. Begin prospective issuance only at a genuine release+24h opportunity with verified sources and the frozen process.

## Verification and reviewer reconciliation

### Single-reviewer cutover — October 22, 2026

- Froze `ffl-1.1.0` / `guidance-v2-single-reviewer`; preserved the original content-addressed protocol and `research/results/sec-fixture`.
- Ran the real offline CLI default into `research/results/sec-single-reviewer`: six documents, 240 candidates, zero human reviews and zero prospective forecasts. New candidate manifest: `befba072dc6588a735e12de4ee77d4245caa33e91398edf2d3b9bc3836d956ee`.
- Confirmed that source-span membership and company-quarter splits exactly match the preceding SEC package. Every new template has reviewer `Dakari`, `second_review_required: false`, a null label, `UNREVIEWED` status and false human attestation.
- Exercised real CLI ingestion, candidate preparation, export, import, TF-IDF invocation and rule evaluation on a disposable **synthetic** corpus. One review per candidate made all 8 training, 2 development and 2 test labels usable; unattested templates were rejected. These software-only labels were never imported into the SEC run.
- **63 tests passed**, including single-reviewer training/evaluation, rejection of cross-policy reviews and retention of the historical second-review gate. Ruff lint passed; after fixing one CLI formatting issue, format check passed for 19 files and MyPy passed for 12 source files.
- Exercised the walkthrough's protected working-copy setup and progress validation. `dakari.json` contains 240 unreviewed candidates; repeat setup refuses overwrite. No judgments or attestations were supplied.

The final active execution manifest records source-tree identity `d5b98f147113f6170278149bad323fc5f1848d969b40ab312024a2f5d0efd951`, unchanged source-data identity `01b767d24e99dad882e47561ae7a922b9cbb4c3c53bf54bf073ffeddd820c1fa`, and scientific-result identity `39cf7964c7bd7365ed7565b23b2e86c642a1b20deb4d3f036e3a0bf2add1ee57`. The initial smoke artifacts are preserved separately in `research/results/sec-single-reviewer-initial-smoke`. Independent inter-annotator agreement is not measured. Research evidence remains pending; no extraction or forecasting improvement is claimed.

### Prior SEC-corpus verification — October 5, 2026


The SEC-corpus replacement was exercised on October 5, 2026:

```text
uv run --locked pytest -q                                 62 passed
uv run --locked ruff check forecast_lab tests             passed
uv run --locked ruff format --check forecast_lab tests    19 files already formatted
uv run --locked mypy forecast_lab                        12 source files; no issues
uv run --offline --locked python -m forecast_lab reproduce
uv run --offline --locked python -m forecast_lab reproduce --output /tmp/ffl-sec-clean-20261005-2206
```

At that checkpoint the default CLI targeted `research/results/sec-fixture`. Its execution manifest recorded source-tree identity `6c4ce27435feb6edef7a6f74ca89b8afd76969feb8dba82adf6d2fce0b1879d6`, source-data identity `01b767d24e99dad882e47561ae7a922b9cbb4c3c53bf54bf073ffeddd820c1fa`, and scientific-result identity `19ab209a109f044cd8cddc76074bdb94cdafe15a693ce871323856a01a01e8ae`. All six exhibit hashes and all six retained acceptance-header hashes matched their metadata. The original frozen protocol JSON remained byte-for-byte unchanged; it is still preserved beside the newer single-reviewer protocol. No permanent tests were added for filenames or default-path wiring; the actual CLI exercised that surface.

The clean and default runs produced identical scientific reports, annotation packages, rule/TF-IDF artifacts, LLM requests and forecasting artifacts. The store integrity audit verified raw/parsed hashes and all 6,591 exact span citations. A final ledger probe confirmed one development root and one linked revision, both abstaining with null probability, and the correct INTU May 1–July 31 target and release+24h cutoff. The probe initially used the wrong artifact kind (`forecast` rather than `forecast_event`); correcting the temporary probe—not production code—completed that check. All six retired raw files match their privately archived original hashes and are absent from the active fixture. Git ignore rules exclude the archive and generated databases.

### Prior engineering reconciliation — retired IR fixture

The following table and verification record describe the preceding engineering baseline, **not a new measurement on the SEC corpus**. Earlier results remain in ignored `research/results/fixture` and `research/results/verified-fixture`; the retired raw corpus and original manifest are also preserved in `research/results/retired-ir-fixture/original-fixture.tar.gz`. Neither these private archives nor the old Git blobs are approved publication inputs. No frozen protocol, cohort, target, split or holdout boundary changed during either reconciliation or the source-channel replacement.

| Workstream | Status | Boundary |
|---|---|---|
| 2A — Task/data contract | COMPLETE | Content-addressed 25-company protocol; actual-time freeze enforcement |
| 2B — Point-in-time ingestion | COMPLETE | Offline ingestion/provenance path; bundled historical bytes are not certified originals |
| 2C — Extraction evaluation | COMPLETE — HUMAN REVIEW PENDING | Review/evaluation plumbing verified; human labels and actual external LLM responses absent |
| 2D — Forecasting comparison | BLOCKED | A–D software exercised; real comparison needs eligible original-vintage fundamentals |
| 2E — Prospective ledger | BLOCKED | Ledger software exercised; no verified current issuance bundle, no genuine prospective records |
| 2F — Reviewer interface | COMPLETE | Terminal/JSON audit exposes forecast and resolution provenance |

All findings below were software correctness/research-integrity defects unless explicitly identified as documentation or evidence boundaries. Prior reproductions were recovered from reviewer reports; final regression checks exercised the corrected behavior.

| Finding | Disposition and verification |
|---|---|
| Caller-supplied protocol freeze time could be backdated | Freeze assigns actual UTC time; original frozen file preserved. `test_freeze_assigns_actual_time_without_rewriting_existing_protocol`. |
| Repeated identical retrieval created duplicate documents | Logical source reused; retrieval observations retained; backdating/conflicting semantics rejected. `test_idempotency_amendments_and_exact_citations`, `test_retrieval_conflicts_and_changed_bytes_require_lineage`. |
| Changed bytes lacked lineage; source anchors could be empty; child availability regressed | Explicit supersession, nonempty anchors and monotonic comparable clocks required. Source regression suite covers each rejection and retained originals. |
| Q4 derivation was unreachable and units/currency were unverified | Import validates cited annual/nine-month operands, fiscal scope, exact value/unit/currency, later availability, and literal boolean absence attestation. `test_q4_import_preserves_both_cited_operands`, parameterized invalid-fact tests and precision test. |
| Nonconsolidated guidance and unrelated metrics contaminated revenue features | Incompatible revenue bases abstain; pure cash-flow/EPS/margin guidance is `NO_GUIDANCE`. Final smoke reproduced the incorrect `AMBIGUOUS` fallback before correction and confirmed the fixed result; extraction regression tests cover both cases. |
| Horizon/numeric answers could lack cited support | Exact supported horizon, endpoints, unit and currency checked; semantic interpretation still requires human review. `test_horizon_and_numeric_guidance_must_be_supported`. |
| Wrong horizons/spurious ranges escaped scoring | Horizon accuracy and all-row nullable numeric accuracy added. A missing numeric prediction also previously removed its gold range from the denominator (observed count 0/null accuracy); now count 1/accuracy 0. Both metric regression tests pass. |
| FY-prefixed years were ignored; already-public outcomes could be scored | Explicit FY-year filtering and outcome-after-cutoff requirement. `test_features_need_no_future_outcome_and_filter_fiscal_years`, `test_already_public_outcomes_are_not_forecasts`. |
| Prospective outcome checks accepted empty identities/URLs | Nonblank attester, HTTPS URL list, fresh clock and explicitly unresolved status required. Ledger regressions also reject backdating and reconstructed-source relabeling. Supplied authority attestations remain unauthenticated. |
| Run/config provenance omitted implementation identity | Extraction, feature/model/evaluation identities include implementation/config hashes; ledger retains numeric source hashes. Reproduction manifests and the source-to-four-baselines regression exercise the chain. |
| Output reuse could mix corpus/parser versions; generated evidence was stale | Protocol/data/source-tree run contract rejects incompatible reuse. New evidence generated in `verified-fixture`; old run retained. Replay regression rejects changed corpus and verifies fresh/reused scientific results. |
| Review/LLM reports hard-coded pending status; command omitted inputs | Reports reflect imported runs/reviews; manifest includes explicit input paths/hashes and stored artifact IDs. `test_replay_preserves_inputs_and_rejects_changed_corpus` uses clearly synthetic review/provider fixtures only. |
| Installed CLI depended on caller's directory | Source-checkout asset root replaces caller-relative lookup; installed editable CLI reproduced successfully from `/tmp`. Standalone wheel corpus distribution is not claimed; README documents this boundary. |
| Audit mislabeled evidence class and omitted resolution provenance | Class-specific warning and exact feature/resolution fact expansion implemented. Synthetic resolved CLI audit exposed seven cited outcome-chain facts, resolution ID and score; real development audit retained null probability and two revisions. |

Prior baseline commands and observed results (historical record):

```text
uv sync --locked --extra dev                              22 packages resolved; 21 audited
uv run --locked pytest -q                                 62 passed
uv run --locked ruff check forecast_lab tests             passed
uv run --locked ruff format --check forecast_lab tests    19 files already formatted
uv run --locked mypy forecast_lab                        12 source files; no issues
uv run --offline --locked python -m forecast_lab reproduce --output /tmp/ffl-final-verification
uv run --offline --locked python -m forecast_lab reproduce --output research/results/verified-fixture
```

In that prior baseline, both reproduction commands succeeded and produced identical scientific reports. An installed `forecast-lab reproduce` invocation from `/tmp` also succeeded against the same temporary output. Raw hashes, separate source/reporting clocks, all 445 exact parsed citations, implementation hash and report hash were explicitly checked. Synthetic tests/smokes additionally verified q-time features without any q+1 fact, chronological guards, immutable revisions, Q4 provenance, unresolved-attestation rejection and resolved audit output.

The retired baseline's execution manifest recorded Python source-tree identity `c301f99f68ea12e95ff6f2b075485fe7f4d04d202f78b0844aba599b32d72674`, source-data identity `ce47608de8601cab9f79a21ea9019d2a2ff5b43e858b627a2e13cd35bd62ea5e`, and scientific-result identity `676ca076f2c60e8fd689c68d24c7d761a58394e0e250b28aa2c5bf0b73faf91e`. These are not the current SEC-fixture identities. Generated SQLite/results remain ignored local artifacts.


## Unsupported claims and rights

No measured extraction quality, incremental real forecasting value, genuine prospective performance, sector-wide generalization or trading alpha is established. The SEC-channel fixture has a documented, qualified reuse basis; it is not a blanket issuer licence, general-purpose model-training grant or clearance of old restricted files. See [source rights](source-rights.md). Local SQLite immutability is not third-party timestamp attestation. The engineering slice is actionable; broader Phase 2 research remains open.

## Publication check

**Publication decision: use a clean branch based on the verified existing public commit `f4219257ee032f4e260aa93c347ea7c4e901f597`, not a descendant of the private implementation commit.** The public repository is `karisheen/Analyst-Assit-NLP`. Only the current implementation, qualified SEC fixture and research documentation belong in the new publication commit. Retired raw files, generated research outputs, private backups and human annotation files are excluded. No published history is rewritten.

Commit `f1ad186` and its descendants remain private: deleting old files in a descendant does not remove their blobs from reachable history. The original commits, working snapshot, research artifacts and annotation file were privately backed up before constructing the clean branch. Do not merge that private-history branch into the clean branch or push all local refs/tags. Human evaluation and prospective outcomes remain pending regardless of publication status.

The clean-tree audit found 48 proposed files, no retired raw blob identities, and no generated results or backups. The 20 objects reachable from the verified public base contain neither `f1ad186` nor the six retired raw blob identities. All twelve SEC exhibit/header SHA-256 values match their provenance records. Independent current-content reviews found no new source-content or concrete credential blocker. The SEC reuse decision remains qualified, not an issuer warranty or unrestricted AI-training licence.

Fresh publication-checkout verification passed **63 tests**, Ruff lint, Ruff formatting for 19 files and MyPy for 12 source files. The actual offline CLI reproduced six SEC documents and 240 candidates with zero human reviews and zero prospective forecasts. A fresh environment initially lacked the optional test tools; the README now explicitly uses `uv run --locked --extra dev` for quality checks. Installing those declared, locked extras resolved that setup prerequisite; no application code changed.

`detect-secrets` 1.5.0 scanned the exact staged source blobs and the inherited public history entirely offline with `--all-files --no-verify`. The source scan yielded 26 candidates: fourteen verified provenance/history identifiers and twelve opaque `script src` references already present in the SEC response bytes; no project credential was identified. History exports included all fourteen reachable blob/commit payloads, three notebook versions and decoded notebook strings. Its only two findings were the same embedded PNG confusion-matrix output, decoded and visually inspected. These are bounded scans, not a guarantee that every possible secret is absent. Private annotations, archives, SQLite databases and generated outputs remain excluded. The exact final committed ancestry and retired-blob exclusion must also pass before an explicit clean-branch-only push.

The following is the historical October 1, 2026 publication check for the **retired IR baseline**. Its permission failures remain relevant to the retained private archives, not a claim that the SEC replacement lacks a reuse basis. The existing `karisheen/Analyst-Assit-NLP` remote was reported public at that check.

- [Salesforce website terms, section G](https://www.salesforce.com/company/legal/sfdc-website-terms-of-service/) require permission or another lawful basis to use site content. Its [Trademark & Copyright Usage Guidelines](https://www.salesforce.com/company/legal/tmcusageguidelines/) prohibit content use/display without explicit written authorization and separately restrict use/scraping for creation or training of AI models/tools. No applicable permission was found in this repository.
- [Adobe's permissions page](https://www.adobe.com/legal/permissions.html) directs requests to use press releases and press materials to `adobepr@adobe.com`; no applicable redistribution grant was established.
- ServiceNow's primary terms endpoints timed out during retrieval. No redistribution grant was established for its two source PDFs; an inaccessible policy is not permission.

That conservative check was not a legal determination about statutory exceptions. The new SEC acquisition does not retroactively authorize the retired materials; do not upload their extracted passages to an external LLM or include their bytes/history in a public release without separate clearance.

Historical pre-commit content check (retired baseline, not a scan of the new SEC fixture):

- The staged baseline contains 38 files; generated results, SQLite databases, virtual environments and Python caches are excluded. The legacy notebook and generated analyst exports are intentionally deleted.
- `detect-secrets` 1.5.0 scanned an isolated staged-file snapshot with `scan --all-files --no-verify`; no candidate credentials were sent to external validation endpoints. Its 18 findings were six documented source SHA-256 hashes and twelve matches in the downloaded Salesforce HTML (browser monitoring/CDN tokens and asset paths). These are third-party page contents, not project API credentials; no live credential validation was attempted. The [Akamai loader documentation](https://techdocs.akamai.com/mpulse-boomerang/docs/implementation) confirms the browser-embedded mPulse key pattern.
- Extracted text/metadata from all four PDFs produced zero scanner findings; none contained file attachments. No project credential was identified in the checked snapshot. This is a bounded scan, not proof that every possible secret is absent.
- All six fixture hashes match the preserved manifest. The staged Python source-tree identity matches the previously reproduced `c301f99f68ea12e95ff6f2b075485fe7f4d04d202f78b0844aba599b32d72674`; the only new repository edits in this publication pass are documentation.
- The full staged whitespace check reports trailing whitespace in the two original Salesforce HTML downloads. It is intentionally retained: editing those raw bytes would invalidate source hashes and provenance. No formatter is applied to original source files.
