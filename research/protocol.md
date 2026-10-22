# Frozen experiment — ffl-1.1.0

Canonical identity: `0ab10bdd199817f9706205f697fc6032e5f5f589ffe17e49cec63160b1b2d328`.

The normative machine-readable file is [the content-addressed protocol](protocols/0ab10bdd199817f9706205f697fc6032e5f5f589ffe17e49cec63160b1b2d328.json). Its `frozen_at` is the actual UTC write time, not an invented historical preregistration. This is a retrospective protocol freeze before held-out evaluation, not evidence that models existed in 2020. Changes require a new file/identity; retain the original and its results.

This version supersedes [ffl-1.0.0](protocols/c00be1d921c79ec472bc6dc449692929936f58e6ab43b1190ce39521fd7bf5ba.json) solely to adopt Dakari's single-human annotation policy before any human labels were imported. The original JSON and `research/results/sec-fixture` are preserved. Label meanings, source corpus, sampling, company-quarter splits and forecasting design are unchanged. New candidate identities belong to `research/results/sec-single-reviewer`; do not copy old review identities into that run.

## Population

Fixed purposive enterprise/business application-software cohort, public by end-2019: ADBE, CRM, NOW, WDAY, INTU, ADSK, PTC, MANH, PAYC, PCTY, VEEV, HUBS, ZEN, ZUO, COUP, APPF, FIVN, BL, BLKB, PEGA, RNG, QTWO, BOX, DBX, SMAR. Ten-digit CIKs and primary SEC identity references are in JSON. Tickers are aliases, not identity. Subsequently acquired issuers remain in the roster and retain eligible history.

This is neither an exhaustive historical sector census nor homogeneous SaaS coverage. Design, consumer-facing products, licensing and company size differ. Identifier verification does not establish historical fiscal/GAAP eligibility; each observation requires a source-backed period mapping. Selection was not optimized against held-out revenue outcomes.

## Target and resolution

Let `R[q]` be original-as-first-reported consolidated GAAP total revenue for issuer fiscal quarter q, in reported currency and units. `g[q] = R[q]/R[q−4] − 1`. Slowdown is `g[q+1] < g[q]`, with exact decimal cross-products and equality mapped to 0. Published precision is retained; no invented digits, FX conversions, annualization or organic-growth adjustments.

Each revenue fact must cite its own original period disclosure, not a later comparative column. Source authority is the first complete original GAAP release: verified earlier IR publication or its original 8-K exhibit; first 10-Q/10-K only when it was genuinely the initial disclosure. Conflicting earliest sources require logged source adjudication, not arbitrary precedence. XBRL is a locator aid, not permission to use current revised facts. Required fact fields include actual fiscal dates, CIK, fiscal labels/regime, currency, scale, exact numeric token and source span, known-at time, and explicit original-source review attestation.

Q4 uses explicit quarterly revenue where available; the protocol permits original FY minus original nine-month revenue with both operand citations and the later availability time. Import a complete quarterly fact with `derivation.annual` and `derivation.nine_month` source records plus `explicit_q4_absent_attestation: true`; both cited operands are retained inside the immutable fact. Each source record includes `unit_support` (`span_id`, exact `unit_token`, exact `currency_token`) in addition to the numeric citation. Mismatched periods, units, currencies and non-boolean absence attestations are rejected. Do not use restated annual comparatives or divide annual revenue by four. Missing or unsupported operand provenance remains excluded.

Acquisitions/divestitures remain in reported GAAP revenue without hindsight recasts; do not selectively remove disappointing cases. Restatements/amendments append separate versions and never replace the original resolution basis. Do not stitch successor CIKs. Missing originals, currency changes, incompatible regimes, missing quarters and transition stubs are exclusions. Ordinary 52/53-week years are permitted with no week normalization. Required quarter chain must be contiguous, 77–105 days per quarter and 350–378 days between matching prior-year endpoints.

## Information clock

The anchor is the earliest verified public complete-quarter revenue release. Cutoff = anchor +86,400 elapsed seconds, including weekends and DST. Primary prospective record creation uses actual UTC now in `[cutoff, cutoff+3,600s]`. SEC acceptance is interpreted in America/New_York before UTC conversion. Release date, report period, source publication, source-version availability and retrieval are separate fields.

Unknown/day-only time is not midnight. A current downloaded webpage is not release-time bytes; historical reconstructions are usable only for explicitly qualified pipeline development. Strict research inputs require certified original versions. Prospective source bytes must already be captured by cutoff. A fresh authoritative outcome check and still-open target quarter are additional conservative issuance requirements; a locally empty resolution table is insufficient.

## Evaluation design

Splits use cutoff UTC, start-inclusive/end-exclusive:

| Partition | Window |
|---|---|
| Training | 2020-01-01 through 2022-12-31 |
| Reserved calibration | 2023-04-01 through 2023-12-31 |
| Validation | 2024-04-01 through 2024-12-31 |
| Final holdout | 2025-04-01 through 2026-12-31 |

Fit once at 2023-01-01, with a 120-day origin embargo **and** each label publicly available strictly before fit. No refitting, feature search or post-hoc probability calibration. The reserved calibration interval is descriptive, not secretly used for tuning. Final holdout import/report is sealed until 2027-10-01. Late resolution beyond cutoff+270 days is retained but excluded from primary scores. Unresolved never means no slowdown. Retrospective and genuine prospective results remain separate.

A is Laplace-smoothed training slowdown frequency. B uses current and previous YoY revenue growth. C uses distinct guidance flags `raised, lowered, maintained, initiated, ambiguous`, with target-horizon filtering and no per-snippet vote inflation. D concatenates B and C. B–D use training-only StandardScaler and fixed L2 logistic regression, C=1, lbfgs, max_iter=2000. Rules-v1 is the preregistered forecasting extractor; TF-IDF/LLM are extraction comparisons, not extra forecasting trials to cherry-pick.

Primary metric: Brier D−B on the same eligible company-quarter rows; negative favors text augmentation. Secondary: clipped log loss (epsilon 1e−6), B−A and C−A; five fixed calibration bins. Store model coefficients, scaler, training IDs, config, library, protocol and dataset identities. No phrase-to-probability conversion. Count companies, calendar-quarter blocks, cutoff dates, exclusions, unresolved rows and model coverage. One primary root per company/quarter/model; revisions are supplementary, not independent observations.

Two-way pigeonhole bootstrap independently samples company and cutoff-calendar-quarter cluster multiplicities, multiplies row weights, and computes paired differences using the same observations. 2,000 draws, seed 20260929, percentile 95% intervals; record zero-weight draws. Conditional on fitted models, not all estimation/model-selection uncertainty. Serial dependence across quarter blocks remains a limitation.

Training minimums: 200 rows, 20 companies, 10 calendar-quarter blocks, 40 per class. Evaluation: 140 resolved rows, 18 companies, 7 blocks, 30 per class, 80% resolution coverage. These are operating sufficiency gates, not a power calculation. Otherwise report inconclusive. Only final holdout D−B Brier ≤−0.005 with interval wholly below zero and passing gates supports incremental value. Failure to establish improvement does not prove equivalence. No result supports trading alpha.

## Extraction and human reference labels

One task: explicit revenue-guidance revision. See [versioned guide](annotation-guide.md), `guidance-v2-single-reviewer`. Freeze candidate/source/split identities before genuine human labels. **Dakari is the sole annotator; one completed, attested human review supplies a reference label for every candidate.** No independent second review or consensus is required. Independent inter-annotator agreement is not measured; a later self-recheck would measure only within-reviewer consistency. Corrections append a superseding review rather than overwrite prior judgments. Conflicting active judgments still block reference-label eligibility. LLM predictions never become human reference labels. Historical pretrained models may know outcomes; prospective evidence is stronger. No final extraction metric is emitted without genuine reviewed labels.

## Known implementation/evidence boundaries

The fixture currently contains six reconstructions, not 25-company original-vintage financial history. It establishes deterministic source ingestion, source/span identity, annotation plumbing and an immutable development ledger—not forecast validity. Original-source attestations and supplied model identities are not independently authenticated. Byte hashing is not a historical archive or external timestamp authority. See [research note](research-note.md) for observed results and failure cases.

The SEC fixture uses INTU FY2024 Q3/Q4, MANH 2024 Q1/Q2 and PAYC 2024 Q1/Q2, all already inside the frozen cohort. The earlier fixture/source-channel replacement did not change the cohort or the original protocol. The later single-reviewer change has its own version and identity, documented above. New corpus/candidate identities must not be pooled with the retired ADBE/CRM/NOW fixture or previous annotation policy. See [source rights](source-rights.md) for the reuse basis and historical-publication boundary.
