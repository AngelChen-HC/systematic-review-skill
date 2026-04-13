# Systematic Review Coordinator — README (v4.1)

## What Is This?

This is an AI-assisted skill that helps researchers conduct **systematic literature reviews** — the gold-standard method for finding, evaluating, and summarising all relevant research on a specific question. It follows the internationally recognised **PRISMA 2020** guidelines and is designed to meet the standards expected by journals, Cochrane, and ethics committees.

**The AI assists; you decide.** The skill automates the time-consuming parts (searching databases, removing duplicates, initial screening) while ensuring that every single decision is reviewed and confirmed by you, the researcher. Nothing is included or excluded from your review without your explicit approval.

---

## Who Is This For?

- **Researchers** conducting systematic reviews for publication, dissertations, or policy reports.
- **Postgraduate students** performing their first systematic review and wanting a structured, standards-compliant workflow.
- **Review teams** who want to use AI to accelerate screening while maintaining full methodological rigour.

**No coding experience is required.** The skill provides step-by-step instructions for every technical step, including how to install Python and run scripts for the first time.

---

## What Does It Do?

The skill guides you through 11 phases of a systematic review, from formulating your research question to generating a PRISMA flow diagram.

### Phase 0: Protocol Generation & Registration
Helps you write a formal review protocol and prompts you to register it on PROSPERO (https://www.crd.york.ac.uk/prospero/), the international registry for systematic review protocols.

### Phase 1: Setup & Configuration
Creates a secure, tamper-evident audit log that records every decision. You set a "seed" number that makes the AI's outputs reproducible. You also choose where files are saved on your computer. An AI Transparency Statement is generated documenting the model, its role, and its limitations.

### Phase 2: Search Strategy
Breaks your research question into structured components (PICO) and generates database search strings with the correct syntax for each target database. Explicitly asks you about study design, language, and date restrictions. Cross-validates search strings for syntax errors and controlled vocabulary accuracy. **Translates search strings into API-native syntax** for each automated database (PubMed, Europe PMC, ClinicalTrials.gov, OpenAlex) — each API uses a different query grammar, so queries must be translated, not copy-pasted. If you want to search a specialised database, the skill analyses it and creates a tailored plan for your approval, including API query translation if applicable.

### Phase 3: Database Retrieval
Provides scripts to automatically search databases using translated API queries. **Includes a network environment check** that detects institutional SSL inspection (common on university networks) and provides resolution steps. If some databases require your university login, the skill explains how to set that up (SSO, VPN, API keys). For databases without automated access, it gives database-specific step-by-step manual search and export instructions.

### Phase 4: Deduplication
Removes duplicate records using a reliable, deterministic method (BibDedupe). Exact matches are removed automatically; uncertain matches are shown to you for a decision.

### Phase 5: Title-Abstract Screening
The AI reads every title and abstract and recommends whether each study should be included or excluded, with a detailed explanation. **You review and confirm every single decision.** Performance monitoring runs automatically, and you independently screen a random 20% sample per batch so accuracy metrics can be computed.

### Phase 5b: Independent Dual Screening
A second reviewer independently screens all records without seeing the first reviewer's decisions. All disagreements are resolved by a third-party adjudicator. Inter-rater reliability (Cohen's Kappa) is computed. This meets the Cochrane requirement for independent duplicate screening.

### Phase 6: Full-Text Retrieval
Downloads full PDFs of included studies from open-access sources. For paywalled papers, tells you which ones to download manually through your university library.

### Phase 7: Full-Text Screening
Same rigorous process as Phases 5 and 5b — AI-assisted screening, 100% human audit, dual screening, performance monitoring.

### Phase 8: Risk of Bias Assessment
You provide a link to your chosen risk-of-bias framework (e.g., Cochrane RoB 2, CASP checklists, Newcastle-Ottawa Scale). The AI applies it study-by-study and presents its assessment. **You confirm every judgment.**

### Phase 9: PRISMA Flow Diagram
Automatically generates the required PRISMA flow diagram from the audit log. You review, correct, and finalise it.

### Phase 10: Export
Packages everything into a complete, publication-ready set of files including an AI Transparency Statement.

---

## Main Features

### 100% Human Oversight
Every inclusion and exclusion decision is confirmed by the researcher. The AI never autonomously decides what goes into your review.

### Independent Dual Screening
Two independent reviewers screen all records. Disagreements are resolved by adjudication. Cohen's Kappa is computed and reported. This meets the Cochrane Handbook v6.5 standard.

### Screening Performance Metrics
The skill continuously measures AI accuracy against your independent judgments: precision, sensitivity, specificity, F1 score, accuracy, and TP/TN/FP/FN — overall and for each exclusion reason.

### AI Transparency Statement
A structured disclosure of the AI's role, model version, known limitations, and configuration, formatted for inclusion in your manuscript per PRISMA-trAIce (experimental) and RAISE (2025) guidance.

### Tamper-Evident Audit Log
Every action is logged with a timestamp and cryptographically chained (SHA-256). Every LLM response is hashed. A verification script is provided.

### Reproducibility
Temperature=0 and a researcher-set seed ensure deterministic outputs. Model version, provider, and inference API version are all logged.

### Beginner-Friendly Scripts
Every Python script comes with complete setup instructions for someone who has never used a terminal before.

### Drift Detection
If the AI's behaviour changes across batches, the skill detects this and notifies you immediately.

### Active Learning Calibration
As you audit the AI's screening decisions, the skill learns from your corrections. After each batch, it extracts the most informative override examples and — with your approval — adds them to the screening prompt as calibration examples. This progressively improves the AI's recommendations for subsequent batches. The same mechanism applies to risk of bias assessment. Every calibration update is logged, version-hashed, and measured for effectiveness. The model itself is not fine-tuned — only the prompt is enriched with few-shot examples.

---

## Standards Compliance

This skill is designed to align with:

- **PRISMA 2020** — Page MJ et al. *BMJ* 2021;372:n71. 27-item checklist for reporting systematic reviews.
- **PRISMA-S** — Rethlefsen ML et al. *Systematic Reviews* 2021;10(1):39. 16-item checklist for search reporting.
- **Cochrane Handbook v6.5** (August 2024). Available at: https://www.cochrane.org/authors/handbooks-and-manuals/handbook
- **AMSTAR-2** — Shea BJ et al. *BMJ* 2017;358:j4008. 16 items (7 critical, 9 non-critical).
- **RAISE (2025)** — Responsible AI for Systematic Evidence, jointly supported by Cochrane, Campbell Collaboration, JBI, and Collaboration for Environmental Evidence.
- **PRISMA-trAIce** — Holst D et al. *JMIR AI* 2025;4:e80247. 14-item transparency checklist for AI in evidence synthesis. Note: this is an experimental proposal, not yet formally validated or registered with EQUATOR.

**AMSTAR-2 critical domain coverage:**

| Domain | Status | How Addressed |
|--------|--------|---------------|
| Protocol registration | Addressed | Phase 0: PROSPERO registration prompted |
| Search adequacy | Addressed | Phase 2: multiple databases, controlled vocabulary, citation chasing |
| Duplicate screening | Addressed | Phase 5b: independent dual screening with Cohen's Kappa |
| RoB assessment | Addressed | Phase 8: researcher-provided framework, 100% human audit |
| Exclusions justification | Addressed | Gates 2, 3: confirmed exclusion reasons for every study |
| Publication bias | Flagged | Noted as researcher responsibility during synthesis (outside skill scope) |
| Statistical methods | N/A | Synthesis is outside skill scope |

---

## Limitations

These limitations are important and should not be understated:

- **AI may produce plausible but incorrect reasoning.** The AI can misinterpret abstracts, miss nuances, or apply criteria inconsistently. That is why 100% human oversight and independent dual screening are built in. AI-assisted screening does not replace independent human review — it augments it.
- **Performance metrics are internal and not externally benchmarked.** The ground-truth validation measures how well the AI matches your judgments for this specific review. These metrics are not transferable to other reviews, topics, or models.
- **This skill does not perform meta-analysis or evidence synthesis.** It covers the review process up to and including risk-of-bias assessment. Synthesis, GRADE assessment, publication bias assessment, and discussion writing are the researcher's responsibility.
- **Database API access varies.** Some databases require institutional credentials, VPN access, or manual searching. The skill provides guidance but cannot bypass access restrictions.
- **LLM determinism has limits.** Temperature=0 and a fixed seed produce deterministic outputs for a given model version and provider. However, outputs may differ across model versions, providers, or infrastructure changes. The response hashing system allows you to verify whether outputs have changed.
- **The quality of the review depends on your decisions.** The skill enforces rigour in process, but cannot guarantee rigour in judgment. Your research question, eligibility criteria, and decisions at each gate determine the review's validity.

---

## Software Dependencies

All dependencies have been verified as of April 2026. Libraries are pinned to specific versions where possible.

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| `requests` | latest | HTTP client for all API access (PubMed, Europe PMC, ClinicalTrials.gov, OpenAlex, Crossref) | Stable, widely used |
| `certifi` | latest | SSL/TLS certificate bundle for HTTPS connections | Stable, widely used |
| `pybliometrics` | 4.4.1 | Scopus retrieval | Actively maintained |
| `bib-dedupe` | latest | Bibliographic deduplication | Actively maintained |
| `PyPaperRetriever` | latest | Open-access PDF retrieval | Published in JOSS 2025 |
| `PyMuPDF` | latest | PDF text extraction | Actively maintained |
| `pytesseract` | latest | OCR for scanned PDFs | Actively maintained |

**APIs accessed directly via `requests` (no wrapper library):**

| API | Purpose | Authentication |
|-----|---------|----------------|
| NCBI E-utilities (PubMed/MEDLINE) | Biomedical literature search and retrieval | None required (API key recommended for higher rate limits) |
| ClinicalTrials.gov API v2 | Clinical trial registry search | None required |
| Europe PMC REST API | Broad biomedical literature | None required |
| OpenAlex API | Open scholarly metadata | None required (polite pool with email) |
| Crossref API | DOI and metadata lookup | None required |

**Not used (and why):**
- `metapub` — replaced with direct NCBI E-utilities calls via `requests` for full control over SSL handling, pagination (`retmax`), query encoding, and error diagnostics. `metapub` uses a Borg singleton pattern, defaults to creation date (`[CRDT]`) for date filtering rather than publication date (`[PDAT]`), and masks underlying HTTP errors.
- `pytrials` — built for the retired ClinicalTrials.gov classic API; replaced by direct v2 API access.
- `ebscopy` — unmaintained, single release; EBSCO databases searched via manual export instead.

---

## How to Use This Skill

### Before You Start

You will need:
1. A research question framed (or ready to be framed) as a PICO question.
2. Access to databases — ideally through a university or institutional library.
3. A computer with internet access. The skill will guide you through installing Python if needed.
4. For dual screening: a second reviewer (human preferred) or willingness to use a second AI pass (documented as a limitation).

### Getting Started

1. Provide your research question. The skill will ask you to frame it using PICO.
2. Set your preferences: study design restrictions, language restrictions, date restrictions, target databases, seed value, and file save locations.
3. Follow the phases. At each gate, you will be asked to review and confirm before proceeding.

### At Each Gate

| Gate | What You Do |
|------|------------|
| Gate 1 | Review and approve search strings (both web-interface and API-translated versions) |
| Gate 2 | Review every title-abstract screening decision |
| Gate 2b | Resolve all dual-screening conflicts |
| Gate 3 | Review every full-text screening decision + resolve conflicts |
| Gate 4 | Review every risk-of-bias judgment |
| Gate 5 | Review and finalise the PRISMA flow diagram |

### What You Get at the End

A complete export folder containing: protocol, AI transparency statement, search strategies, screening results (with dual-screening conflicts), ground-truth validation data, inter-rater reliability reports, risk-of-bias assessments, PRISMA flow diagram (SVG + editable source), included/excluded studies, performance monitoring report, full audit log, and a chain verification script.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Python script won't run | Check that your virtual environment is active. If not, run the activation command from the setup instructions. |
| "ModuleNotFoundError" | Run `pip install [module name]` with your virtual environment active. |
| SSL: CERTIFICATE_VERIFY_FAILED | Your institution's network performs SSL inspection. Run the Network Environment Check script (Phase 3) and follow the resolution steps (install institution CA cert, set SSL_CERT_FILE, or use --no-ssl-verify as last resort). |
| All databases return 0 results | First run the Network Environment Check to rule out SSL/network errors. If the network is fine, check whether the API-translated queries (Step 2.3b) use the correct syntax for each database — PubMed-style field tags like `[tiab]` will not work on Europe PMC, ClinicalTrials.gov, or OpenAlex. |
| Database API returns errors | Check your internet connection. If the database requires institutional access, ensure you are on your university VPN or SSO. |
| AI seems to be screening inconsistently | Check the performance monitoring metrics. If drift or low sensitivity is detected, the skill will alert you. |
| Audit log verification fails | This means an entry has been modified after creation. Check the reported entry for issues. |
| A URL in the skill is broken | URLs change over time. Search for the framework by name on the organisation's website. |

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0 | Original skill: 6-phase workflow |
| 2.0 | Added: risk of bias assessment, evaluation pipeline, PRISMA diagram, audit chain |
| 3.0 | Added: 100% human oversight, 20% ground-truth validation with metrics, study design/language/date restriction cues, database cross-validation, custom database plan-first protocol, institutional SSO guidance, beginner-friendly Python instructions, researcher-set directories, CASP frameworks, datetime logging |
| 4.0 | **Citation integrity:** removed fabricated reference (De Vries et al. 2024); replaced with verified RAISE (2025) and PRISMA-trAIce. **Dual screening:** added Phase 5b with independent Reviewer B, conflict resolution, and Cohen's Kappa (Cochrane compliance). **AI transparency:** added structured AI Transparency Block per PRISMA-trAIce and RAISE. **Toolchain fix:** replaced deprecated `pytrials` and `ebscopy` with direct API access (ClinicalTrials.gov v2, Europe PMC, OpenAlex, Crossref). Fixed ASReview/recordlinkage mischaracterisation. **Audit log:** added `output_hash` for LLM response hashing; replaced raw CoT with `structured_rationale` schema. **URLs:** fixed broken links for Newcastle-Ottawa Scale, QUADAS-2, CASP RCT checklist. **Cochrane version:** updated from v6.4 to v6.5. **Failure recovery:** added hash-chain-validated resume from any phase. |
| 4.1 | **API query translation (Step 2.3b):** added mandatory translation of web-interface search strings into API-native syntax for each automated database (PubMed E-utilities, Europe PMC, ClinicalTrials.gov v2, OpenAlex), with verified one-shot examples and field-mapping tables. Root cause fix: passing PubMed-style `[tiab]`/`[MeSH Terms]` tags to other APIs caused those tags to be treated as literal text, returning 0 results from all non-PubMed databases. **SSL/network resilience (Phase 3):** added Network Environment Check with diagnostic script and three resolution paths for institutional SSL inspection (the immediate cause of all 4 databases failing with `CERTIFICATE_VERIFY_FAILED`). **Replaced `metapub` with direct E-utilities via `requests`:** eliminates Borg singleton quirks, creation-date default, and masked HTTP errors; gives full control over SSL, pagination, and error diagnostics. **Explicit API call templates:** Phase 3 now includes exact endpoint structures, parameter names, and pagination patterns for all four automated databases. **Pagination hardened:** all API calls now override dangerously small defaults (PubMed 20→10000, Europe PMC 25→1000, ClinicalTrials.gov 10→1000, OpenAlex 25→100 with cursor pagination). **Verification step:** after each database query returning 0 results, a sanity-check query distinguishes between query syntax errors and network/access errors. **Diagnostic error categorisation:** script now distinguishes SSL errors, HTTP auth errors, rate limits, server errors, timeouts, query syntax errors, and genuine empty results with plain-language messages. **Manual search instructions expanded:** database-specific step-by-step guides for Cochrane, CINAHL, Embase, Web of Science, and PsycINFO (replacing generic template). **Additional databases (Step 2.4):** extended plan-first protocol to require API query translation and SSL checks for any researcher-specified database. **Gate 1 expanded:** researcher now reviews both web-interface strings and API-translated queries. **Added `certifi`** to dependencies. **Active learning calibration (Phases 5, 7, 8):** after each batch of human-audited screening decisions, the system extracts the most informative override examples and (with researcher approval) inserts them as few-shot calibration examples into the screening prompt for subsequent batches, progressively improving AI recommendations toward the researcher's ground truth. Includes: priority-ranked example selection (false negatives first), maximum 5 examples per prompt (3 for RoB), researcher approval of every calibration update, per-batch effectiveness measurement (override rate, sensitivity, precision trends), calibration regression detection, and full audit logging with prompt version hashing. Same mechanism adapted for risk of bias domain-level judgments (Phase 8). Calibration data included in Phase 10 export. AI Transparency Block updated to disclose active learning. Design principle 10 added. |
