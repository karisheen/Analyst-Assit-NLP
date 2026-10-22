# AGENTS.md

## Purpose

This file defines the operating rules for AI coding agents working in this repository.

Read this file **before making changes**.

These instructions apply to the primary agent, spawned subagents, reviewers, and any other automated coding or research workflow operating in this repository.

If an instruction in a user prompt conflicts with this file, follow the user's explicit instruction for that task while preserving the research-integrity constraints unless the user explicitly changes the underlying research protocol.

---

# Project Mission

This repository is being transformed from the original **Analyst Assist** NLP prototype into a **Fundamental Forecast Lab**.

The primary research question is:

> After a company reports earnings, does its contemporaneously available disclosure help forecast whether next-quarter year-over-year revenue growth will be lower than the just-reported quarter's year-over-year growth?

This is a **business-outcome forecasting research project**.

It is not primarily:

- a document-chat application;
- a generic RAG demo;
- a stock-price prediction system;
- an automated trading strategy;
- a portfolio-management application;
- a sentiment classifier;
- an LLM showcase;
- a financial dashboard;
- a model-zoo benchmark;
- or an autonomous investment agent.

The purpose of the project is to produce **defensible empirical evidence** about:

1. point-in-time financial-document ingestion;
2. structured evidence extraction;
3. extraction accuracy against human-reviewed labels;
4. incremental forecasting value relative to simple baselines;
5. calibration and uncertainty;
6. prospective forecasting;
7. provenance and reproducibility.

A negative empirical result is acceptable.

A polished system without a defensible experiment is not.

---

# Authoritative Roadmap

The broader project roadmap is located at:

`~/Developer/plans/projects/quant-project-strengthening-roadmap.md`

Phase 2 of that roadmap is the authoritative high-level specification for this repository.

When working on Phase 2:

1. read this `AGENTS.md`;
2. read the relevant Phase 2 section of the roadmap;
3. inspect the repository;
4. determine what already exists;
5. implement the smallest coherent vertical slice needed for the requested work.

Do not blindly translate roadmap prose into new infrastructure if equivalent functionality already exists.

---

# Repository Transition

The repository began as an Analyst Assist / NLP prototype using **20 Newsgroups** data as a proxy classification problem.

That historical work may remain available through Git history and may remain in clearly historical/archive locations where appropriate, but it must **not remain the primary project story**.

The target main-branch narrative is the Fundamental Forecast Lab.

Do not:

- erase Git history merely to hide the prior prototype;
- build a second overlapping project beside the existing repository;
- create another generic document-chat application;
- rename the repository as a prerequisite for substantive work.

Repository renaming is presentation work.

Do not rename the repository until the first reproducible financial-document vertical slice works unless the user explicitly requests otherwise.

---

# Core Research Principles

These rules are non-negotiable unless the user explicitly changes the research design.

## 1. Freeze before outcomes

Define the following before examining final held-out outcomes:

- eligible population;
- sector/cohort;
- timestamps;
- information cutoff;
- labels;
- exclusions;
- metrics;
- baselines;
- evaluation splits;
- dependence treatment;
- stopping/inconclusive criteria.

A protocol change after freezing must create a **new version/identity**.

Never silently rewrite the frozen protocol.

---

## 2. Point-in-time means availability time

Do not confuse:

- reporting period;
- document date;
- earnings date;
- filing date;
- publication date;
- retrieval date;
- information availability time.

The relevant research question is what information was **actually available at the forecast creation time**.

A fact that existed economically but had not yet been publicly released is not available information.

Preserve availability timestamps wherever possible.

---

## 3. Prevent temporal leakage

Historical pipeline development is allowed.

Outcome leakage is not.

Agents must actively check for:

- future filings entering historical feature sets;
- amended documents replacing originals without provenance;
- future-quarter fundamentals entering training;
- resolved outcomes entering features;
- post-release revisions being treated as contemporaneous;
- train/test overlap;
- company-quarter leakage;
- unresolved labels entering training;
- prompt examples containing target outcomes;
- model-generated features that accidentally include future information.

When uncertain, fail closed and document the ambiguity.

---

## 4. Preserve dependence structure

Do not treat every snippet, document, forecast revision, company quarter, or repeated observation as statistically independent.

Evaluation should explicitly consider dependence across:

- companies;
- quarters;
- dates;
- sectors;
- repeated document snippets;
- forecast revisions;
- related disclosures.

Use company/date clustering or another defensible treatment when estimating uncertainty.

Do not inflate evidence by counting correlated observations as independent samples.

---

## 5. No alpha by implication

Better:

- extraction;
- classification;
- Brier score;
- log loss;
- calibration;
- document retrieval;
- qualitative evidence;

does **not** establish profitable trading.

Do not describe forecasting improvements as:

- alpha;
- profitable edge;
- exploitable edge;
- market-beating;
- trading profitability;

unless a separate, properly designed experiment supports that claim.

This repository's primary target is a business outcome, not a security return.

---

## 6. Tests are not predictive evidence

Tests establish implementation correctness.

They do not establish predictive validity.

Keep separate:

### Software evidence
- unit tests;
- integration tests;
- type checking;
- schema validation;
- fixture reproduction;
- deterministic replay.

### Research evidence
- held-out labels;
- metrics;
- uncertainty;
- calibration;
- prospective outcomes;
- error analysis.

Never substitute one category for the other.

---

## 7. No hidden trial history

Preserve meaningful experiment history.

Record or version:

- protocol replacements;
- model variants;
- prompt changes;
- exclusions;
- feature changes;
- calibration changes;
- failed experiments;
- negative results.

Do not repeatedly tune against a holdout and report only the final successful variant.

---

## 8. No LLM self-grading as ground truth

An LLM cannot be the sole judge of its own extraction quality.

Final extraction evaluation requires:

- human-reviewed labels;
- externally resolved outcomes;
- or another independently defensible source of ground truth.

LLMs may assist with:

- candidate generation;
- annotation tooling;
- disagreement surfacing;
- schema validation;
- error categorization;

but those activities are not equivalent to independent human ground truth.

---

## 9. Distinguish retrospective from prospective evidence

A current model may know historical events from pretraining or other exposure.

Therefore:

- historical evaluation is useful for pipeline development;
- historical held-out evaluation is useful but must be qualified;
- prospective forecasts recorded before outcomes exist provide the strongest evidence.

Never call a forecast prospective if it was created after the outcome was already publicly knowable.

Never back-date records to simulate prospectivity.

---

## 10. Negative and abstaining results are valid

Valid outputs include:

- `NO-GO`;
- abstention;
- insufficient evidence;
- unsupported source;
- unresolved target;
- missing quarter;
- ambiguous disclosure;
- failure to beat a baseline;
- inconclusive comparison.

Do not force a prediction merely to increase sample size.

---

## 11. No autonomous trading scope

This project remains a:

- research;
- forecasting;
- evidence;
- and decision-support system.

Do not add:

- broker execution;
- autonomous trading;
- order routing;
- live position management;

unless the user explicitly creates a separate execution-system scope.

---

# Phase 2 Research Target

The target variable is whether:

**next-quarter year-over-year revenue growth**

is lower than:

**the just-reported quarter's year-over-year revenue growth.**

The precise mathematical definition must be frozen in the research protocol.

Do not invent alternative targets mid-experiment because they produce more attractive results.

Examples of changes requiring a new protocol identity include:

- replacing revenue growth with EPS growth;
- changing YoY to QoQ;
- changing binary slowdown to a multi-class target;
- changing the forecast horizon;
- changing the cohort;
- changing the authoritative revenue source;
- changing the forecast timestamp;
- materially changing exclusion rules.

---

# Required Phase 2 Workstreams

## 2A — Task and Data Contract

Before serious model work, define and version:

- one sector;
- approximately 20–30 comparable companies;
- stable company identifiers;
- fiscal-quarter alignment rules;
- exact forecast creation time;
- information cutoff;
- revenue-growth units;
- slowdown label;
- authoritative resolution source;
- acquisition treatment;
- divestiture treatment;
- restatement treatment;
- currency treatment;
- missing-quarter treatment;
- fiscal-calendar-change treatment;
- cohort;
- forecast horizon;
- exclusions;
- evaluation metrics;
- evaluation splits;
- dependence assumptions;
- inconclusive-result rules.

Recommended structured thesis/evidence fields include:

- claim;
- horizon;
- prior probability;
- observable drivers;
- evidence for;
- evidence against;
- invalidation conditions;
- missing evidence;
- resolution source;
- current forecast;
- revision reason.

The protocol must be machine-readable in addition to human-readable documentation.

Frozen protocol semantics must have a stable version or identity.

---

## 2B — Point-in-Time Disclosure Ingestion

Primary source types include:

- 10-K filings;
- 10-Q filings;
- relevant 8-K exhibits;
- investor-relations earnings releases;
- SEC submission metadata;
- XBRL metadata/facts where useful.

Prefer original, publicly accessible sources.

Preserve, where available:

- company identity;
- stable identifier;
- ticker;
- CIK;
- filing/form type;
- accession/source identifier;
- reporting period;
- accepted/published availability timestamp;
- original/amended status;
- source URL;
- retrieval timestamp;
- raw document hash;
- parsed spans;
- stable source references.

A downstream forecast should be traceable back to the exact source version that informed it.

---

# Storage and Infrastructure

Use the simplest architecture that satisfies the research requirements.

For the first credible slice, prefer:

- Python;
- SQLite;
- typed structures;
- explicit schemas;
- deterministic fixtures;
- ordinary filesystem artifacts;
- CLI commands;
- reproducible scripts.

SQLite is sufficient unless a concrete requirement demonstrates otherwise.

Do not introduce infrastructure merely because it is more sophisticated.

Avoid by default:

- Kafka;
- distributed compute;
- microservices;
- vector databases;
- data lakes;
- Kubernetes;
- separate backend services;
- foundation-model training infrastructure;
- unnecessary cloud dependencies.

Complexity must be justified by an actual research requirement.

---

# Ingestion Requirements

Ingestion should be:

- rerunnable;
- idempotent where appropriate;
- revision-aware;
- provenance-preserving;
- deterministic on fixtures;
- testable offline.

Repeated ingestion must not silently duplicate logical records.

Amendments and restatements must not silently overwrite earlier versions.

When a source changes, preserve the relevant history.

A correction should remain traceable to:

1. previous version;
2. new version;
3. availability timestamps;
4. content hashes;
5. downstream dataset versions where applicable.

---

# Citation and Evidence Provenance

Structured evidence extracted from documents must retain exact support.

Where practical, an evidence item should identify:

- source document;
- source version/hash;
- source identifier/accession;
- reporting period;
- availability timestamp;
- stable span reference;
- quoted or normalized evidence;
- extraction configuration/model identity.

Do not produce unsupported qualitative summaries that cannot be traced to source material.

The system should make it possible to answer:

> Exactly which contemporaneously available passage caused this evidence record or forecast revision?

---

# 2C — Extraction Evaluation

Begin with **one extraction task**.

Examples include:

- demand strengthening/weakening;
- guidance direction;
- changed business assumptions.

Prefer the task whose annotation criteria can be made most objective.

Do not begin by attempting to extract every conceivable financial concept.

---

# Annotation Dataset

Target approximately **150–300 manually reviewed snippets** for the first serious extraction evaluation.

The dataset should intentionally contain:

- positive examples;
- difficult negatives;
- ambiguous language;
- numeric statements;
- table/text conflicts;
- evidence supporting a thesis;
- evidence contradicting a thesis.

Create a versioned annotation guide.

The guide should define:

- label meanings;
- span requirements;
- ambiguity;
- abstention;
- numeric handling;
- contradictory evidence;
- difficult negatives;
- table/text disagreement;
- missing context.

Split labels before final evaluation.

The active `guidance-v2-single-reviewer` policy uses Dakari as the sole human annotator. Do not require or invent a second reviewer. One genuine completed human review supplies each reference label; preserve correction lineage and report that independent inter-annotator agreement is not measured. A self-recheck is not independent review. Preserve the older frozen protocol and its historical second-review requirements rather than rewriting them.

---

# Human Annotation Boundary

Agents may:

- assemble candidate snippets;
- propose preliminary labels;
- generate annotation interfaces;
- flag ambiguous examples;
- validate annotation schemas;
- generate QA checks.

Agents must **not** represent model-generated labels as human-reviewed ground truth.

If human review has not occurred:

1. prepare the annotation corpus;
2. prepare the annotation guide;
3. prepare review tooling;
4. prepare split identities;
5. clearly mark review status;
6. continue non-blocked engineering work;
7. do not claim final held-out extraction performance.

---

# Extraction Baselines

The first extraction experiment should compare:

1. deterministic/rule-based baseline;
2. simple text-model baseline;
3. LLM-assisted structured extraction.

Do not add a large model zoo.

Metrics should include where applicable:

- span support;
- precision;
- recall;
- F1;
- abstention;
- numeric accuracy;
- citation validity;
- failure categories.

Record the exact model/version/configuration used.

---

# 2D — Forecasting Evaluation

Forecasting comparisons should be incremental.

Required initial baselines:

## Model A — Sector / Base Rate

Simple and interpretable.

## Model B — Numeric Only

Regularized model using only preregistered lagged fundamentals available by the information cutoff.

## Model C — Text Only

Use frozen structured qualitative features.

## Model D — Numeric + Text

Combine the preregistered numeric and qualitative inputs.

Do not add additional models merely to search for a positive result.

---

# Forecast Probability Rules

Do not map vague verbal confidence directly into probability.

For example, avoid arbitrary mappings such as:

- "likely" = 70%;
- "very likely" = 85%;
- "moderate confidence" = 60%.

Probability calibration must rely on previously resolved outcomes and a declared method.

Do not calibrate using unresolved or future outcomes.

---

# Forecast Evaluation Requirements

Use chronological evaluation.

Include a gap where necessary to prevent unresolved labels from entering training.

Report at least:

- Brier score;
- bounded log loss;
- calibration by probability range;
- forecast count;
- company count;
- quarter count;
- exclusions;
- resolution coverage;
- paired score differences;
- uncertainty around score differences;
- dependence treatment;
- inference cost;
- model identity;
- protocol identity;
- data identity.

Separate:

1. retrospective development;
2. retrospective held-out evidence;
3. prospective evidence.

Do not combine them into one headline metric.

---

# Uncertainty

Report uncertainty around model comparisons.

Do not present a small raw metric difference as meaningful without considering sampling uncertainty and dependence.

Use:

- company clustering;
- date clustering;
- clustered bootstrap/resampling;
- or another defensible method;

as appropriate to the design.

Document the chosen method.

If the effective sample size is too small for a strong conclusion, say so.

---

# Calibration

Calibration is part of the evidence, not decoration.

Where sample size permits, report:

- probability bins;
- predicted probability;
- observed frequency;
- count per bin;
- calibration error or equivalent descriptive measure.

Do not overinterpret sparse bins.

---

# 2E — Prospective Forecast Ledger

The prospective ledger is a priority because calendar time cannot be recreated later.

Start it as soon as:

- the protocol is frozen;
- source provenance is reliable;
- forecast creation semantics are defined.

Do not delay the ledger solely to make the modeling architecture more elaborate.

---

# Immutable Forecast Records

Each frozen forecast should include:

- forecast ID;
- protocol identity;
- creation timestamp;
- information cutoff;
- target company;
- target quarter;
- source document hashes;
- prior probability;
- revised probability;
- supporting evidence;
- opposing evidence;
- missing evidence;
- abstention state;
- model identity;
- prompt/configuration identity;
- inference cost where applicable;
- resolution rule;
- revision lineage.

Do not mutate an existing frozen forecast to reflect a later belief.

Create a new revision linked to the previous record.

Preserve the historical state.

---

# Prospective Integrity

Never:

- back-date forecasts;
- rewrite forecast creation timestamps;
- insert later documents into earlier forecasts;
- rewrite probabilities after seeing results;
- resolve forecasts before the authoritative outcome exists;
- label retrospective records as prospective.

If an eligible future quarter is currently unresolved and the required information is available, a genuine prospective forecast may be created using the frozen protocol and the **actual current timestamp**.

---

# 2F — Reviewer Interface

The reviewer interface is secondary.

Do not build it before the underlying:

- provenance;
- extraction;
- evaluation;
- ledger;

paths work.

The minimal interface should expose:

- prior probability;
- current probability;
- exact cited evidence;
- evidence for;
- evidence against;
- missing evidence;
- ambiguous evidence;
- abstention;
- revision history;
- model identity;
- document provenance;
- resolution;
- forecast score.

Prefer a minimal interface compatible with the existing repository architecture.

Do not introduce a new frontend stack without a concrete need.

---

# Agent Workflow

For every significant assignment:

## Step 1 — Read

Read:

- this `AGENTS.md`;
- the relevant roadmap section;
- `README.md`;
- dependency/project configuration;
- relevant design docs;
- affected code;
- affected tests.

Do not modify code before understanding the existing implementation.

---

## Step 2 — Inspect Git State

Run and inspect appropriate Git commands such as:

`git status`

and relevant history/diff commands.

Preserve unrelated user modifications.

Do not overwrite work simply because it is unexpected.

---

## Step 3 — Establish Baseline

Before changing behavior, determine the smallest test, command, or scenario that demonstrates current behavior.

Run it when practical.

Do not assume the repository is currently green.

Record pre-existing failures separately from failures introduced by the task.

---

## Step 4 — Reuse Existing Architecture

Prefer modifying the existing architecture over creating parallel systems.

Do not introduce:

- second configuration frameworks;
- duplicate schemas;
- redundant CLIs;
- competing database abstractions;
- duplicate evaluation frameworks;

unless the existing approach is demonstrably unsuitable.

---

## Step 5 — Implement One Vertical Slice

Prefer one complete path:

source
→ storage
→ provenance
→ extraction
→ forecast/evaluation
→ evidence artifact

over many half-finished abstractions.

Build the smallest coherent feature that proves the intended behavior.

Then expand.

---

## Step 6 — Exercise Real Behavior

Do not stop at unit tests.

Run the actual command or scenario that demonstrates the changed behavior.

For fixture workflows, exercise them without network access where appropriate.

---

## Step 7 — Preserve Evidence

Preserve the artifacts needed to reproduce the result.

Do not commit:

- secrets;
- private credentials;
- machine-local state;
- huge replaceable downloads;
- unnecessary caches;
- sensitive raw data.

Small deterministic fixtures are encouraged.

---

## Step 8 — Document Reality

Documentation must distinguish:

- implemented functionality;
- measured evidence;
- assumptions;
- prospective work;
- limitations.

Do not describe future functionality as implemented.

---

## Step 9 — Produce Evidence Manifest

For meaningful research runs, record as appropriate:

- source revision;
- protocol identity;
- dataset identity;
- configuration;
- model identity;
- prompt identity;
- command;
- artifacts;
- results;
- exclusions;
- known limitations.

---

# Multi-Agent Work

When multiple agents are available, use them deliberately.

Parallel subagents are best used for:

- repository audit;
- protocol review;
- ingestion/provenance review;
- statistics/evaluation review;
- test/reproducibility review;
- security review.

Avoid allowing multiple agents to make overlapping edits to the same architecture simultaneously.

Preferred pattern:

1. parallel read-only investigation;
2. primary-agent synthesis;
3. one integration owner;
4. implementation;
5. parallel read-only review;
6. primary-agent reconciliation.

The primary agent owns architectural consistency.

---

# Subagent Rules

A subagent must:

- read this file;
- remain within its assigned scope;
- distinguish observations from recommendations;
- cite exact repository locations where useful;
- avoid speculative rewrites;
- report blockers clearly;
- avoid overlapping implementation unless explicitly authorized.

Subagents should not redesign unrelated parts of the project.

---

# Skill and Tool Usage

Inspect the available skills/tools before substantial work.

Use relevant specialist skills where they provide concrete value for:

- Python packaging;
- testing;
- SQL/database work;
- financial/SEC ingestion;
- schema design;
- statistical evaluation;
- CLI implementation;
- documentation;
- security;
- static analysis.

Do not invoke tools or skills merely to maximize tool usage.

The simplest reliable path is preferred.

---

# Git Safety

Unless the user explicitly requests otherwise:

Do not:

- commit;
- push;
- force push;
- rebase shared history;
- reset hard;
- clean untracked files destructively;
- rewrite history;
- delete branches;
- rename remote repositories;
- create releases.

You may prepare the working tree for review.

At the end of significant work, report:

- current branch;
- Git status;
- major changed files;
- untracked artifacts;
- whether changes are committed.

---

# Secrets and Credentials

Never hard-code:

- API keys;
- database passwords;
- tokens;
- cookies;
- private credentials.

Use environment configuration consistent with repository conventions.

Fixtures must not depend on private credentials.

If an exposed credential is discovered:

1. stop using it;
2. report the location;
3. remove it from active code;
4. recommend rotation if it may have been real;
5. do not print the secret unnecessarily.

---

# External Data Retrieval

When retrieving SEC, investor-relations, or other public financial documents:

- prefer authoritative/original sources;
- respect source identity;
- preserve source URL;
- preserve retrieval time;
- preserve availability time separately;
- preserve document hashes;
- handle amendments explicitly.

Do not silently substitute a newer document for the historically available version.

---

# Deterministic Fixtures

The repository should contain a small distributable fixture capable of exercising the important research path without:

- private credentials;
- a huge local database;
- network access;
- proprietary data.

The fixture should be large enough to demonstrate:

- document ingestion;
- provenance;
- parsed citations;
- extraction;
- annotation/evaluation plumbing;
- immutable forecast records;
- report generation.

The fixture is for reproducibility and correctness.

It is not automatically representative evidence of forecasting performance.

---

# Reproducibility

The first credible Phase 2 slice should expose one documented entry path that can regenerate the fixture analysis from a clean environment.

The command should eventually cover:

1. fixture database initialization;
2. fixed-corpus ingestion;
3. provenance verification;
4. structured extraction;
5. held-out extraction evaluation when legitimate reviewed labels exist;
6. immutable forecast creation;
7. forecasting baseline evaluation when data permits;
8. machine-readable results;
9. figures/report generation.

Do not claim reproducibility unless the documented command was actually exercised.

---

# Testing Expectations

Use existing repository tooling first.

Discover actual commands from:

- `pyproject.toml`;
- `Makefile`;
- task runner configuration;
- CI configuration;
- README;
- existing scripts.

Do not invent new command conventions without need.

Where configured, run relevant:

- unit tests;
- integration tests;
- linting;
- formatting checks;
- static typing;
- schema validation;
- fixture reproduction;
- CLI smoke tests.

Every meaningful bug fix should receive a regression test where practical.

Report exact failures rather than hiding them.

---

# Evidence Package

Use repository conventions where possible.

An equivalent of the following evidence structure should emerge:

```text
research/
├── protocol.md
├── manifest.json
├── fixtures/
├── labels/
├── results/
├── figures/
├── ledger/
├── research-note.md
└── reproduce.*
```

Do not force these exact directory names if the repository already has an equivalent organization.

The required contract is the **evidence**, not the folder naming.

---

# Research Note Requirements

A research note should answer:

1. What exact question was asked?
2. What information was available at forecast time?
3. What baseline would make the new method unnecessary?
4. How were labels and resolution defined?
5. How were repeated or related observations handled?
6. What was frozen before evaluation?
7. What result was observed?
8. What uncertainty surrounds the result?
9. What failed?
10. What remains unsupported?
11. Can another person reproduce the result?
12. What claim is explicitly not justified?

Include negative results.

Include representative failure cases.

Do not hide exclusions or unresolved observations.

---

# Major Phase Ordering

Default Phase 2 implementation order:

1. **2A — Task/data contract**
2. **2B — Point-in-time disclosure ingestion**
3. **2C — Extraction evaluation infrastructure and human-label workflow**
4. **2E — Start prospective ledger as early as protocol reliability permits**
5. **2D — Forecasting baseline comparison**
6. **2F — Minimal reviewer interface**

This ordering intentionally begins the prospective ledger before extensive model refinement.

Calendar time cannot be recreated later.

---

# Model Development Discipline

Do not optimize complexity before proving the baseline.

Prefer:

simple baseline
→ measurable failure
→ justified improvement

over:

complex architecture
→ retrospective story about why it is useful.

Before adding a new model, answer:

> What existing baseline does this model need to beat or complement?

If that question has no clear answer, do not add the model yet.

---

# Holdout Discipline

Once the final held-out set is frozen:

- do not repeatedly inspect it while tuning;
- do not change exclusions based on disappointing cases;
- do not redefine labels to improve metrics;
- do not replace the cohort because another cohort performs better;
- do not tune prompts against final test examples;
- do not use the holdout as development data.

If substantial design changes become necessary after inspecting the holdout:

1. preserve the original result;
2. create a new protocol/version;
3. establish a new untouched evaluation set if possible;
4. document why the previous design was replaced.

---

# Reporting Counts

Whenever forecasting metrics are reported, include counts that reveal the actual evidence base.

At minimum consider:

- total forecasts;
- resolved forecasts;
- unresolved forecasts;
- companies;
- quarters;
- dates;
- excluded observations;
- abstentions;
- missing-source cases.

Do not report a metric without enough context to understand the denominator.

---

# Failure Analysis

Do not report only aggregate metrics.

Preserve failure categories such as:

- unsupported claim;
- wrong evidence span;
- numeric extraction error;
- table/text conflict;
- stale source;
- missing source;
- ambiguous language;
- temporal leakage prevention;
- incorrect quarter alignment;
- overreaction to qualitative evidence;
- underreaction;
- inappropriate abstention;
- failure to abstain.

At least a few representative failures should appear in the research note.

---

# Three Audited Example Types

As the project matures, preserve at least three audited examples:

1. **Useful belief revision**
   - new contemporaneous evidence appropriately changes the forecast.

2. **Overreaction / failure**
   - extracted evidence changes the forecast too aggressively or incorrectly.

3. **Correct abstention / insufficient evidence**
   - the system refuses to manufacture confidence.

These examples must be selected transparently and not presented as statistically representative unless they actually are.

---

# Architecture Preferences

Prefer:

- explicit data models;
- typed Python;
- clear function boundaries;
- simple dependency injection where useful;
- deterministic behavior;
- immutable research artifacts;
- structured logging;
- stable IDs;
- content hashing;
- schema validation;
- command-line reproducibility;
- human-readable outputs alongside machine-readable outputs.

Avoid unnecessary framework churn.

---

# Scope Control

Do not add the following unless directly required for the current research question:

- generic chatbot;
- generic RAG UI;
- broad company coverage;
- real-time stock prices;
- broker integration;
- portfolio optimization;
- options analytics;
- social-media sentiment feeds;
- autonomous research agents inside the product;
- fine-tuning;
- custom foundation models;
- distributed systems;
- additional frontend frameworks;
- unnecessary databases;
- unrelated market-data infrastructure.

More features are not automatically progress.

---

# Definition of the First Credible Slice

The first credible Phase 2 slice is complete when a **fresh checkout** can:

1. ingest a small fixed financial-document corpus;
2. preserve point-in-time source metadata;
3. preserve exact document provenance;
4. produce structured evidence with citations;
5. evaluate extraction against legitimate held-out human-reviewed labels when available;
6. emit an immutable forecast record;
7. regenerate an evaluation report through one documented command.

If legitimate human labels are still pending, the engineering slice may be complete while extraction evidence remains explicitly pending human review.

Do not conflate those states.

---

# Definition of Broader Phase Completion

The entire Phase 2 should **not** be declared fully complete merely because the software has been implemented.

Prospective evidence requires actual calendar time.

The broader phase remains open until genuine prospective forecasts begin resolving.

Historical results may be published with appropriate qualifications while the prospective ledger continues accumulating.

---

# Status Vocabulary

When reporting Phase 2 progress, use statuses such as:

- `COMPLETE`
- `COMPLETE — HUMAN REVIEW PENDING`
- `STARTED — PROSPECTIVE OUTCOMES PENDING`
- `NOT STARTED`
- `BLOCKED`

Do not mark a workstream `COMPLETE` when required evidence does not yet exist.

---

# End-of-Task Report

After substantial work, report:

## What changed

Major implementation changes.

## Research decisions

Any protocol or schema decisions made.

## Evidence produced

Only actual measured/generated evidence.

## Tests run

Exact commands and results where practical.

## Reproduction

Exact command for reproducing the relevant result.

## Human review needed

What still requires genuine human judgment.

## Prospective status

Whether genuine unresolved forecasts exist.

## Limitations

Known weaknesses and unsupported claims.

## Files changed

Major files added or modified.

## Git state

Branch and working-tree status.

## Next action

The smallest logical next step.

---

# Final Standard

The project should optimize for:

**defensibility over complexity**

**provenance over convenience**

**point-in-time correctness over dataset size**

**baselines over novelty**

**reproducibility over screenshots**

**calibration over confidence language**

**honest uncertainty over headline metrics**

**prospective evidence over retrospective storytelling**

**research quality over feature count**

When in doubt, choose the implementation that makes it easier for another researcher to answer:

> What did the system know, when did it know it, what did it predict, what baseline did it face, and can I reproduce the result?
