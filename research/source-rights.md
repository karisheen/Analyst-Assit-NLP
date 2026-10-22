# Source rights: SEC-hosted earnings-exhibit fixture

Reviewed: 2026-10-05. This is a project-specific research and publication decision, not a legal opinion, an issuer licence, or a representation that every SEC-hosted item is public domain.

## Decision and scope

**SEC-hosted public 8-K earnings exhibits are a defensible replacement channel for this small, reproducible research fixture**, relying on the SEC's express statement about reuse of **EDGAR public filing content**, read together with its linked copying/distribution policy and exceptions. This conclusion is a qualified interpretation of those statements, not an express SEC approval of this project or an AI-specific licence.

The replacement set is six article-HTML exhibits for INTU FY2024 Q3/Q4, MANH 2024 Q1/Q2, and PAYC 2024 Q1/Q2. Acquisition/integration records identify these accessions:

| Issuer | Accessions |
|---|---|
| INTU | `0000896878-24-000024`, `0000896878-24-000035` |
| MANH | `0000950170-24-046886`, `0000950170-24-085622` |
| PAYC | `0000950170-24-051272`, `0000950170-24-088567` |

The [fixture manifest](fixtures/manifest.json) is the per-document acquisition record: use its exact exhibit URLs, issuer identities, retrieval times and byte hashes, rather than interpreting this policy review as a separate audit of all document metadata. Article HTML, not a crawl of linked images or external sites, is the intended retained material. External logo/image assets were not downloaded for the replacement acquisition.

This replaces the old ADBE/CRM/NOW investor-relations downloads; it does not retrospectively clear those downloads. INTU, MANH and PAYC are already in the frozen cohort. That source-channel replacement left the original protocol `c00be1d921c79ec472bc6dc449692929936f58e6ab43b1190ce39521fd7bf5ba` unchanged. The subsequent single-reviewer policy has a new identity described in [protocol.md](protocol.md); it changes no source-use permissions. Neither source-rights review nor the six-file fixture establishes forecast validity, original-vintage eligibility, genuine human labels or held-out evaluation results.

## Primary SEC evidence

The SEC pages below were retrieved from the primary host during this review. The native reader returned HTTP 403; `curl` with the declared user agent `FundamentalForecastLab dakariantoine@gmail.com` returned the policy HTML. [Selected exact excerpts](rights/sec-policy-excerpts.json) preserve the relevant wording and URLs locally. They are transcribed excerpts with HTML entities decoded, **not** full-page snapshots or independently timestamped archives. The review date does not establish what policy applied on a historical earnings-release date.

### Public filing reuse, not government authorship

[SEC Webmaster Frequently Asked Questions, “Is content on sec.gov free? Do I need permission to reuse EDGAR content?”](https://www.sec.gov/about/webmaster-frequently-asked-questions#reuse), displayed “Last Reviewed or Updated: Aug. 23, 2024”:

> All Government-created content on sec.gov and EDGAR public filing content are free to access and reuse. See Website Dissemination for our permissions policy.

The wording explicitly includes public filing content separately from government-created content. Issuer-authored earnings releases do **not** become United States government works merely because they are submitted to or hosted by the SEC. This project relies on the stated reuse policy for that channel, not on a claim of universal public-domain status or a government-works copyright exemption for private authors.

The immediately following [FAQ exception](https://www.sec.gov/about/webmaster-frequently-asked-questions#reuse2), answering “Is any of the content not free to reuse?”, says:

> Very little. Examples include stock art photos used to illustrate various sec.gov pages.

That example is not an exhaustive clearance of all third-party material. Do not expand this decision to arbitrary photographs, artwork, third-party reports, external resources or every exhibit category.

### Linked dissemination policy and exceptions

The FAQ links to [Website Dissemination](https://www.sec.gov/privacy.htm#dissemination). That URL resolves to the SEC's [Privacy Information page](https://www.sec.gov/about/privacy-information#dissemination), displayed “Last Reviewed or Updated: Nov. 29, 2023”:

> Information presented on sec.gov is considered public information and may be copied or further distributed by users of the web site without the SEC’s permission. Please consider appropriate citation to the SEC as the source.

This supports retaining and redistributing the SEC-acquired fixture and its attributed extracts. “Without the SEC’s permission” is not a representation that the SEC owns all underlying rights or indemnifies downstream users. The same section says:

> Please do not use the SEC seal or any of the other logos or artwork from this site.

It also states:

> In addition, please be advised that “SEC,” the EDGAR logo, and the names EDGAR, EDGARLink, and EDGARLink Online are the SEC's registered trademarks. You may not use them in a trade name, trademark, or domain name of an SEC- or EDGAR-related business without a license from the SEC. You may refer in text to the existence of EDGAR and the EDGAR system without a license, so long as you are not creating the impression that your business is affiliated with or approved by the SEC.

No SEC seal, agency logo or artwork is licensed as project branding. Retained HTML references to images are provenance, not a grant to fetch, republish or promote the images themselves. Preserve issuer and third-party notices in the source document; do not claim ownership of them or place the raw exhibits under a blanket project-code licence.

The [external-link policy](https://www.sec.gov/about/privacy-information#links) adds:

> Once you link to another site, you are subject to the policies of that site.

A link from an exhibit does not extend the SEC permission to the linked issuer, wire-service or image host.

### Automated access

The [FAQ](https://www.sec.gov/about/webmaster-frequently-asked-questions#code-support) allows scripted access and asks users to declare their user agent. The [Internet Security Policy](https://www.sec.gov/about/privacy-information#security) specifies:

> Current guidelines limit users to a total of no more than 10 requests per second, regardless of the number of machines used to submit requests.

Use the declared contact-bearing user agent above, stay below that aggregate ceiling, respect blocking, and do not circumvent controls. Access permission and rate compliance are separate from copyright/reuse permission. The policy can change; recheck it before materially expanding acquisition.

## AI and model-evaluation boundary

[INFERENCE] The broad reuse statement is a reasonable basis for this fixture's deterministic ingestion, text normalization, source-span extraction, annotation, reproducible tests, and limited research comparisons of rules, TF-IDF and LLM extraction. Retaining the SEC-acquired documents and derived text with provenance is necessary for reproducing those operations. This is the approved project interpretation, not language expressly mentioning AI in the quoted policy.

The reviewed reuse provisions do **not** expressly address training general-purpose or generative models, fine-tuning, model weights, vendor retention, cross-border processing or commercial model-data licensing. Absence of an AI prohibition is not an explicit unrestricted AI-training grant. Do not advertise these exhibits as a universally cleared AI-training corpus, sublicense issuer rights, or infer permission for unrelated mass harvesting. External model evaluation must separately account for the provider's input/retention/training terms and applicable privacy obligations; no hosted-model execution or provider-specific clearance is established by this review. A broader training or commercial redistribution project warrants a separate rights assessment and, where needed, permission from the relevant holders.

### PAYC's Business Wire dateline

The PAYC releases contain a `BUSINESS WIRE` dateline, but the replacement bytes were acquired as SEC-hosted public 8-K exhibits, not from Business Wire. [INFERENCE] This places the acquisition within the SEC's express public-filing reuse statement; it does **not** establish that Business Wire or other contributors surrendered copyright or that the SEC can override a separately binding agreement. Preserve the dateline and notices. Do not fetch the wire-hosted version or linked assets under the assumption that the SEC policy applies there.

[Business Wire's primary Terms of Use URL](https://www.businesswire.com/terms-of-use) was located, but direct reader and declared-user-agent retrieval both returned HTTP 403 during this review. No unverified AI clause is quoted or treated as cleared here. The wire-hosted route is **not approved** by this decision. If an individual exhibit contains a conflicting express restriction or separately licensed content, pause that item's redistribution and obtain specific review rather than assuming the hosting channel cures every underlying right.

## Attribution and no endorsement

For each retained document, preserve issuer name, release title/fiscal period, exact SEC exhibit URL, accession, retrieval time and byte hash in the fixture manifest. Identify normalized text, extracts, annotations and model outputs as project transformations, not SEC-authored or official versions. Keep raw bytes separate from those transformations.

Use this attribution in descriptions of the fixture:

> Issuer-authored earnings releases obtained from public SEC EDGAR 8-K exhibits; source URLs and retrieval provenance are recorded in the fixture manifest. Reuse is based on the SEC's published public-filing reuse and website-dissemination policies. Neither the SEC nor the issuers nor any wire service endorses, sponsors or has approved this project or its outputs.

## Timestamp and original-version caveats

The [SEC FAQ on availability lag](https://www.sec.gov/about/webmaster-frequently-asked-questions#lag) says:

> Filings are often available on sec.gov within 1-3 minutes of the EDGAR system timestamp. The lag time can increase significantly with high server load. We don’t guarantee and cannot predict this lag.

Its [timestamp explanation](https://www.sec.gov/about/webmaster-frequently-asked-questions#timestamps) explicitly states:

> There is no timestamp to indicate when filing content is first available on sec.gov.

Consequently, an acceptance timestamp is **not** proven website-publication time. Do not add a fixed one- or three-minute adjustment and call it verified availability. Keep fiscal period, release dateline, filing date, SEC acceptance, source-version availability and actual retrieval time distinct. A day-only release date is not midnight. A hash fixes the bytes retrieved now; it does not certify their release-time existence or completeness. A SEC-hosted exhibit also does not prove that the issuer did not publish earlier through another channel.

The [frozen protocol](protocol.md) interprets SEC acceptance in `America/New_York` before UTC conversion and requires an independently supported information clock and original-version evidence. This note does not change those rules. Retrospective fixture captures remain pipeline-development reconstructions unless those separate requirements are satisfied; reuse permission cannot make them prospective observations.

## Alternate channels considered and not selected

### SEDAR / SEDAR+

The current successor channel's [primary Terms of Use](https://www.sedarplus.ca/onlinehelp/terms-of-use) redirected to [CSA SEDAR+ Resources](https://systems.securities-administrators.ca/terms-of-use/), with displayed terms last updated April 28, 2023. Section 2 permits limited unaltered extracts/copies for informational, educational, research or internal business use, subject to conditions including:

> you do not engage in frequent, public, commercial or mass distribution of Public Information

and:

> you do not use any or all of the Public Information to construct a database of any kind, nor store the Public Information (in whole or in part) in databases for access by you or any third party, nor offer or provide any services containing all or part of the Public Information;

Section 2(f) also prohibits scraping/automated reproduction of multiple pieces, referring to section 5. Section 2(g) requires title/source attribution; section 2(h) bars implying official versions or endorsement. These conditions do not supply a clean basis for the proposed stored, processed and publicly reproducible fixture. **Reject SEDAR+ for this replacement without a suitable separate permission/agreement.** This is not an assertion that all research use is prohibited, nor a finding about every historical SEDAR contract; no legacy SEDAR permission is established here.

### Companies House

[Companies House, “Our public task, copyright and Crown copyright”](https://www.gov.uk/government/publications/companies-house-accreditation-to-information-fair-traders-scheme/public-task-copyright-and-crown-copyright), displayed updated August 9, 2019, distinguishes agency-produced Crown copyright material from material on the public register. Section 2.2 says:

> Companies House imposes no rules or requirements on how the information on the public register is used.

But section 3 expressly requires:

> all customers, including bulk customers, must take their own legal advice regarding possible breach of third party copyright

It also forbids reproduction of the Crown insignia and requires source credit for material from its guidance, website, publications or statistical tables. Thus open register access and the agency publication's Open Government Licence are not blanket clearance of companies' submitted documents. **Do not substitute this channel**: it does not resolve the third-party-rights question and does not itself provide the same frozen-cohort quarterly earnings/guidance observations. This is a scope/clearance decision, not a claim that Companies House data cannot be reused.

## Publication boundary: clean branch, private history remains prohibited

**Commit `f1ad186` contains the old restricted raw fixture files. Do not push or publish that commit or any of its descendants.** Replacing files in the current tree does not remove the old blobs from Git history; this SEC-channel decision does not retroactively authorize their publication. The hold includes branches, tags, bundles, release archives and other exports that carry the old history or files.

The clean publication branch is constructed from the existing public base `f4219257ee032f4e260aa93c347ea7c4e901f597`, importing only the current source tree, not the private commit's ancestry. It retains the six SEC exhibits, their six SEC acceptance-header pages, source metadata and these qualified reuse records. Retired raw files, derived research outputs, private backups and human annotation files are excluded. Before pushing, verify both the proposed tree and its reachable history against the retired blob identities, inspect contents for secrets or copied retired text, and exercise the clean checkout. A clean current tree alone is not evidence of clean history.

Preserve the old commits, complete private working snapshot and research artifacts in private backups. Never merge the private-history branch into the publication branch or use `git push --all`, `--mirror`, or `--tags` from that repository. Push only the explicitly reviewed clean branch. This construction does not rewrite existing public commits or retroactively authorize the retired material; its hold remains in force.

## Residual risk summary

The direct SEC statements are materially stronger support than mere public accessibility. Nevertheless, they are agency website statements, not negotiated licences or issuer warranties. Residual risks include underlying issuer/wire/third-party rights, document-specific notices, logos/artwork and personal information, different jurisdictions, later policy changes, and model-provider uses beyond this fixture's scope. Keep this decision limited to the SEC-acquired public earnings-exhibit text and associated provenance, preserve attribution, and revisit it for conflicting notices or materially broader use. No conclusion here depends on calling issuer works government-authored or universally public domain.
