# Systematic Review & Meta-Analysis Coordinator — README (v8.0)

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

The skill guides you through the phases of a systematic review, from formulating your research question to generating a PRISMA flow diagram — and, where you want it, all the way through data extraction and a full quantitative meta-analysis with GRADE certainty assessment. It supports both **new reviews** and **updates of existing reviews** (re-running a published or PROSPERO-registered review's searches to capture newly published studies, deduplicating against your prior corpus, and screening only what is genuinely new).

### Phase 0: Protocol Generation & Registration
Helps you write a formal review protocol and prompts you to register it on PROSPERO (https://www.crd.york.ac.uk/prospero/), the international registry for systematic review protocols.

### Phase 1: Setup & Configuration
Creates a secure, tamper-evident audit log that records every decision. You set a "seed" number that is logged for traceability and makes sampling steps (pilot selection, spot-check selection) exactly reproducible. Reproducibility of the review as a whole comes from versioned, hashed screening instructions and complete decision logging — see the skill's Reproducibility Statement. You also choose where files are saved on your computer. An AI Transparency Statement is generated documenting the model, its role, and its limitations.

### Phase 2: Search Strategy
Breaks your research question into structured components (PICO) and generates database search strings with the correct syntax for each target database. Explicitly asks you about study design, language, and date restrictions. Cross-validates search strings for syntax errors and controlled vocabulary accuracy. **Translates search strings into API-native syntax** for each automated database (PubMed, Europe PMC, ClinicalTrials.gov, OpenAlex) — each API uses a different query grammar, so queries must be translated, not copy-pasted. If you want to search a specialised database, the skill analyses it and creates a tailored plan for your approval, including API query translation if applicable. **New in v8 — Benchmark Retrieval Validation (Step 2.3d):** before you approve the strategy, the skill tests whether it *actually retrieves known-relevant papers*. You supply 2–5 key anchor references early on; a seeded gold set of ~10 in-scope papers is drawn from their reference lists, and Gate 1 does not pass until the strategy retrieves them all (or every miss carries a logged justification). This catches wrong synonyms and over-narrow terms that a syntax check cannot — it is a recall check only, and for review updates it runs as an optional regression test that never re-tunes your reused strings.

### Phase 3: Database Retrieval
Provides scripts to automatically search databases using translated API queries. **Includes a network environment check** that detects institutional SSL inspection (common on university networks) and provides resolution steps. If some databases require your university login, the skill explains how to set that up (SSO, VPN, API keys). For databases without automated access, it gives database-specific step-by-step manual search and export instructions.

### Phase 4: Deduplication
Removes duplicate records using a reliable, deterministic method (BibDedupe). Exact matches are removed automatically; uncertain matches are shown to you for a decision.

### Phase 5: Title-Abstract Screening
The AI reads every title and abstract and recommends whether each study should be included or excluded, with a detailed explanation. **You review and confirm every single decision.** Performance monitoring runs automatically, and you independently screen a random 20% sample per batch so accuracy metrics can be computed.

### Phase 5b: Independent Dual Screening
A second reviewer independently screens all records without seeing the first reviewer's decisions. All disagreements are resolved by a third-party adjudicator. Inter-rater reliability (Cohen's Kappa) is computed. This meets the Cochrane requirement for independent duplicate screening.

### Phase 5c: Learned Alignment — Local Fine-Tuning (new in v8, optional)
Entirely optional, and off by default. When the prompt-calibration loop stops improving (or when you ask), the skill can fine-tune a **small open-weights model running on your own computer** using the screening decisions you have already audited — so it learns *your* judgment on *your* criteria. Two new gates protect this:

- **Gate 2c — the fine-tuning decision.** Before anything trains, you see a full, honest notice: time required, what it costs (no per-token API fees — it runs locally; the honest unit is compute time and disk), exactly which of your data is used (only this review's audited decisions; never your ground-truth validation records; nothing is uploaded anywhere), what you might gain, what you might not, and the drawbacks of **both** choices. **Opting out is a fully valid, logged answer** — the review is just as rigorous without Phase 5c — and the scripts mechanically refuse to train without your recorded opt-in.
- **Gate 5c — adapter promotion.** A trained adapter is never used until it beats the current setup on ground-truth records it has never seen (recall of includes ≥ 0.95, specificity protected) **and** you explicitly confirm. Failed adapters are archived; if a promoted one later degrades, the system automatically rolls back to the previous state and tells you.

The fine-tuned model only recommends and triages — it never finalises a decision, never auto-excludes, and every one of its outputs passes through the same human gates as everything else. Adapters are review-specific calibration artifacts, exported with your reproducibility package but flagged non-transferable.

### Phase 6: Full-Text Retrieval
Downloads full PDFs of included studies from open-access sources. For paywalled papers, tells you which ones to download manually through your university library.

### Phase 7: Full-Text Screening
Same rigorous process as Phases 5 and 5b — AI-assisted screening, 100% human audit, dual screening, performance monitoring.

### Phase 7b: Study Data Extraction (new in v7)
Before extracting anything, the skill proposes a **Target Data-Point List** derived from your own research question and protocol, and asks you to confirm or modify it. Extraction is then piloted on a few studies with a blind human audit and an error-rate gate before scaling — the same pilot-before-scale discipline the skill applies to screening. Every extracted value carries a **verbatim quote plus its exact document location** (page and line in the logged text of the PDF), verified both by a script and by you. A second, independent extraction of outcome data catches what the first missed, and every disagreement is classified by its root cause — a transcription slip, a missing convention, a defect in the data-point list, or a sign that something upstream (your outcome definition, the eligibility criteria) needs attention. No arithmetic happens at this stage: values are recorded exactly as the papers report them.

### Phase 8: Risk of Bias Assessment
You provide a link to your chosen risk-of-bias framework (e.g., Cochrane RoB 2, CASP checklists, Newcastle-Ottawa Scale). The AI applies it study-by-study and presents its assessment. **You confirm every judgment.**

### Phases 8c–8e: Meta-Analysis (new in v6, optional)
If you want quantitative synthesis, the skill first checks — per outcome — whether pooling is appropriate at all (routing unsuitable outcomes to a structured narrative synthesis, SWiM). It then presents an **Analytical Approach Summary**: every statistical choice (effect measure, model, methods for heterogeneity, subgroups, sensitivity analyses, publication-bias checks) explained in plain language, with alternatives and consequences, for your approval — nothing runs until you approve the plan. The skill asks whether you prefer **R or Python**, generates a beginner-annotated analysis script with pinned library versions, and asks whether you want to run it yourself (full instructions provided) or have the skill run it for you. **All statistics are computed by the executed script — never by the AI.** You verify every reported number against the script's output, confirm GRADE certainty judgments, and receive publication-ready forest/funnel plots, a Summary of Findings table, and a statistical methods paragraph.

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
Temperature=0 minimises output variability. Model version, provider, and inference API version are logged — including the model version actually used for each screening batch, since long screens span sessions. Reproducibility rests on versioned/hashed prompts and criteria plus complete decision logging (see the skill's Reproducibility Statement), not on seed-level determinism of the AI's reasoning.

### Beginner-Friendly Scripts
Every Python script comes with complete setup instructions for someone who has never used a terminal before.

### Drift Detection
If the AI's behaviour changes across batches, the skill detects this and notifies you immediately.

### Active Learning Calibration
As you audit the AI's screening decisions, the skill learns from your corrections. After each batch, it extracts the most informative override examples and — with your approval — adds them to the screening prompt as calibration examples. This progressively improves the AI's recommendations for subsequent batches. The same mechanism applies to risk of bias assessment. Every calibration update is logged, version-hashed, and measured for effectiveness. This is the *fast path*: the orchestrating model itself is never fine-tuned — only the prompt is enriched.

### Learned Alignment (new in v8, optional)
The *slow path*: a local open-weights model (1–8B, on your machine) can be fine-tuned on this review's audited decisions via LoRA/QLoRA adapters. It is entered only through an informed opt-in (Gate 2c, with the full time/cost/data/effectiveness notice and the drawbacks of both options), deployed only through a recall-safe promotion gate plus your confirmation (Gate 5c), and it never trains on ground-truth validation records (enforced by scripts that abort on any violation). Every adapter is versioned, hash-identified, and fully provenance-logged; declining the whole feature is a first-class, logged, methodologically sound choice.

### Search Benchmark Validation (new in v8)
Before Gate 1, the search strategy is tested against a seeded gold set of known-relevant papers (known-item / relative recall) — the strategy must retrieve them, or every miss must be diagnosed, fixed, or justified.

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
| Publication bias | Addressed | Phases 8c–8e: contour-enhanced funnel plots; Egger's/Peters' tests only at ≥10 studies; trim-and-fill as sensitivity only |
| Statistical methods | Addressed | Phases 8c–8e: human-approved analysis plan (Gate 4c); statistics computed only by pinned, hashed R/Python scripts |

---

## Limitations

These limitations are important and should not be understated:

- **AI may produce plausible but incorrect reasoning.** The AI can misinterpret abstracts, miss nuances, or apply criteria inconsistently. That is why 100% human oversight and independent dual screening are built in. AI-assisted screening does not replace independent human review — it augments it.
- **Performance metrics are internal and not externally benchmarked.** The ground-truth validation measures how well the AI matches your judgments for this specific review. These metrics are not transferable to other reviews, topics, or models.
- **Quantitative synthesis is in scope, interpretation is not.** Since v6 the skill performs meta-analysis, publication-bias diagnostics, and GRADE — but every statistic is computed by executed, version-pinned R/Python scripts (never by the AI), every analytical choice requires your approval first, and the interpretive discussion remains entirely yours.
- **Fine-tuning (Phase 5c) has its own limits.** A model tuned on this review's decisions can overfit your early errors; when it serves as Reviewer B its errors are correlated with yours (weaker error-independence than a second human — disclosed as a limitation); no performance gain is promised in advance, and a real possible outcome is that no adapter ever passes the promotion gate. Adapters are review-specific and non-transferable.
- **Database API access varies.** Some databases require institutional credentials, VPN access, or manual searching. The skill provides guidance but cannot bypass access restrictions.
- **LLM determinism has limits.** Temperature=0 reduces variability, but for multi-step, tool-using ("agentic") screening a seed does not guarantee identical reasoning across runs, and outputs may differ across model versions, providers, sessions, or infrastructure changes. The skill therefore builds reproducibility on versioned, hashed prompts/criteria and complete per-record decision logging; the response hashing system lets you verify whether outputs changed.
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

**Optional — Phase 5c fine-tuning stack** (only needed if you opt in at Gate 2c; versions verified live on PyPI at v8 authoring, 2026-07-10; install with `pip install -r scripts/requirements-finetune.txt`):

| Library | Version | Purpose |
|---------|---------|---------|
| `torch` | 2.13.0 | Local model runtime |
| `transformers` | 5.13.0 | Model/tokeniser loading |
| `datasets` | 5.0.0 | Training-set handling |
| `accelerate` | 1.14.0 | Training runtime |
| `peft` | 0.19.1 | LoRA/QLoRA adapters |
| `trl` | 1.8.0 | SFT / DPO / KTO trainers |
| `bitsandbytes` | 0.49.2 | 4-bit QLoRA — **CUDA GPUs only**; skip on CPU/Apple silicon |

The base model itself (default Qwen2.5-1.5B-Instruct; 1–8B tiers by hardware) is downloaded once from Hugging Face at first use — it is not part of this repository.

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
5. *(Optional, only for Phase 5c fine-tuning)* ~10–20 GB of free disk and ideally an NVIDIA GPU; CPU-only works with the smallest model tier (hours, not minutes). You will only ever be asked about this at Gate 2c, with the full cost notice — and "no" is a fully valid answer.

### Getting Started

1. Provide your research question. The skill will ask you to frame it using PICO.
2. Set your preferences: study design restrictions, language restrictions, date restrictions, target databases, seed value, and file save locations.
3. Follow the phases. At each gate, you will be asked to review and confirm before proceeding.

### At Each Gate

| Gate | What You Do |
|------|------------|
| Gate 1 | Approve search strings (web + API versions) — v8: including the benchmark retrieval result |
| Gate 2a | Confirm the criteria lock after calibration pilots pass the κ gate |
| Gate 2 | Review every title-abstract screening decision |
| Gate 2b | Resolve all dual-screening conflicts |
| Gate 2c *(v8, only if raised)* | Make the informed fine-tuning decision — opt in or out after the full time/cost/data/effectiveness notice |
| Gate 5c *(v8, only if training ran)* | Review the promotion report and confirm (or refuse) adapter deployment |
| Gate 3 | Review every full-text screening decision + resolve conflicts |
| Gates 3b / 3c / 3d | Confirm the extraction data-point list; lock the extraction guideline after pilots; lock the verified extraction dataset |
| Gate 4 | Review every risk-of-bias judgment |
| Gates 4c / 4d / 4e | Approve the analysis plan; confirm execution mode + outputs; verify every reported number and GRADE judgment |
| Gate 5 | Review and finalise the PRISMA flow diagram |

### What You Get at the End

A complete export folder containing: protocol, AI transparency statement, search strategies, screening results (with dual-screening conflicts), ground-truth validation data, inter-rater reliability reports, risk-of-bias assessments, PRISMA flow diagram (SVG + editable source), included/excluded studies, performance monitoring report, full audit log, and a chain verification script — plus, for reviews that used Phase 5c, the learned-alignment trail: adapters with provenance manifests, dataset cards and exclusion manifests, promotion reports with your Gate 5c confirmations, and the full activation/rollback history (including any documented opt-out at Gate 2c).

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
| "BLOCKED — Gate 2c (fine-tuning decision) not passed" | By design: no training runs without your informed opt-in. Run `python3 scripts/decide_fine_tuning.py --config learned_alignment/adapter_training.json`, read the notice, and type your decision. |
| `bitsandbytes` fails to install (Mac / CPU machine) | Expected — it is CUDA-only. Keep `"quantization": "none"` with the 1.5B model tier; skip that requirements line. |
| GPU out-of-memory during training | Drop one hardware tier: smaller base model, or switch `"quantization"` to `"4bit"` (NVIDIA GPUs). |

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0 | Original skill: 6-phase workflow |
| 2.0 | Added: risk of bias assessment, evaluation pipeline, PRISMA diagram, audit chain |
| 3.0 | Added: 100% human oversight, 20% ground-truth validation with metrics, study design/language/date restriction cues, database cross-validation, custom database plan-first protocol, institutional SSO guidance, beginner-friendly Python instructions, researcher-set directories, CASP frameworks, datetime logging |
| 4.0 | **Citation integrity:** removed fabricated reference (De Vries et al. 2024); replaced with verified RAISE (2025) and PRISMA-trAIce. **Dual screening:** added Phase 5b with independent Reviewer B, conflict resolution, and Cohen's Kappa (Cochrane compliance). **AI transparency:** added structured AI Transparency Block per PRISMA-trAIce and RAISE. **Toolchain fix:** replaced deprecated `pytrials` and `ebscopy` with direct API access (ClinicalTrials.gov v2, Europe PMC, OpenAlex, Crossref). Fixed ASReview/recordlinkage mischaracterisation. **Audit log:** added `output_hash` for LLM response hashing; replaced raw CoT with `structured_rationale` schema. **URLs:** fixed broken links for Newcastle-Ottawa Scale, QUADAS-2, CASP RCT checklist. **Cochrane version:** updated from v6.4 to v6.5. **Failure recovery:** added hash-chain-validated resume from any phase. |
| 4.1 | **API query translation (Step 2.3b):** added mandatory translation of web-interface search strings into API-native syntax for each automated database (PubMed E-utilities, Europe PMC, ClinicalTrials.gov v2, OpenAlex), with verified one-shot examples and field-mapping tables. Root cause fix: passing PubMed-style `[tiab]`/`[MeSH Terms]` tags to other APIs caused those tags to be treated as literal text, returning 0 results from all non-PubMed databases. **SSL/network resilience (Phase 3):** added Network Environment Check with diagnostic script and three resolution paths for institutional SSL inspection (the immediate cause of all 4 databases failing with `CERTIFICATE_VERIFY_FAILED`). **Replaced `metapub` with direct E-utilities via `requests`:** eliminates Borg singleton quirks, creation-date default, and masked HTTP errors; gives full control over SSL, pagination, and error diagnostics. **Explicit API call templates:** Phase 3 now includes exact endpoint structures, parameter names, and pagination patterns for all four automated databases. **Pagination hardened:** all API calls now override dangerously small defaults (PubMed 20→10000, Europe PMC 25→1000, ClinicalTrials.gov 10→1000, OpenAlex 25→100 with cursor pagination). **Verification step:** after each database query returning 0 results, a sanity-check query distinguishes between query syntax errors and network/access errors. **Diagnostic error categorisation:** script now distinguishes SSL errors, HTTP auth errors, rate limits, server errors, timeouts, query syntax errors, and genuine empty results with plain-language messages. **Manual search instructions expanded:** database-specific step-by-step guides for Cochrane, CINAHL, Embase, Web of Science, and PsycINFO (replacing generic template). **Additional databases (Step 2.4):** extended plan-first protocol to require API query translation and SSL checks for any researcher-specified database. **Gate 1 expanded:** researcher now reviews both web-interface strings and API-translated queries. **Added `certifi`** to dependencies. **Active learning calibration (Phases 5, 7, 8):** after each batch of human-audited screening decisions, the system extracts the most informative override examples and (with researcher approval) inserts them as few-shot calibration examples into the screening prompt for subsequent batches, progressively improving AI recommendations toward the researcher's ground truth. Includes: priority-ranked example selection (false negatives first), maximum 5 examples per prompt (3 for RoB), researcher approval of every calibration update, per-batch effectiveness measurement (override rate, sensitivity, precision trends), calibration regression detection, and full audit logging with prompt version hashing. Same mechanism adapted for risk of bias domain-level judgments (Phase 8). Calibration data included in Phase 10 export. AI Transparency Block updated to disclose active learning. Design principle 10 added. |
| 8.0 | **Learned Alignment (Phase 5c, optional, trigger-based):** fine-tunes a LOCAL 1–8B open-weights screener (never the orchestrating model) on the review's own audited decisions via LoRA/QLoRA (`peft` 0.19.1 / `trl` 1.8.0 / `transformers` 5.13.0, all versions verified on PyPI at authoring); training signal harvested deterministically from existing audit artifacts (pilot blind audits, audited batches AGREE/OVERRIDE, adjudicated conflicts, full-text decisions, Phase 7b transcription-class corrections only — the root-cause router unchanged); ground-truth validation records excluded from all training by an asserted record-ID manifest and reserved as the promotion test set. **New Gate 2c** (informed fine-tuning decision: full time/API-cost/research-data/efficiency/effectiveness notice with drawbacks of both options; typed opt-in/opt-out, mechanically enforced by the scripts; opt-out is a logged, first-class outcome). **New Gate 5c** (recall-safe promotion: binary retain/discard sensitivity ≥ max(incumbent, 0.95), specificity ≥ incumbent − 0.05, parse-failures ≤ 2%, full Phase-5a metric panel with Wilson CIs and exact-McNemar/bootstrap honesty; researcher confirmation mandatory; failed adapters archived; automatic rollback on drift, automatic promotion never). Full provenance per adapter (semver, weight SHA-256, dataset hash + record-ID manifest, base id + pinned revision, hyperparameters, promotion report), all hash-chained; AI Transparency Block rewritten (per-batch {orchestrator id, adapter version+hash, prompt hash}; "model not fine-tuned" line retired); Design Principle 10 recast as two-speed learning; adapters framed as calibration to this researcher's audited judgment — not ground truth — and exported non-transferable. Six shipped scripts + `srlib/` (decide_fine_tuning, build_training_set, train_adapter, evaluate_adapter, promote_adapter, screen_with_adapter). **Also folds in the Brief #2 patches:** Step 2.3d Benchmark Retrieval Validation gating Gate 1 (seeded gold set, per-database + pooled recall, miss-diagnosis loop, recall-only disclaimer; update-mode regression variant); Phase 0 anchor-reference elicitation (dual purpose); credential-store/keychain security boundary (never touched, even transiently, without durable consent); "Upgrading Mid-Review" version-boundary policy + `skill_version_customisation` entry; per-audited-batch κ/PABAK/direction logging + scripted prior-batch re-scan after post-lock rule amendments; generic boundary-policy calibration templates (Step 5a.6); hashed human-readable `screening_criteria_locked.md` rulebook; frontmatter description compressed to the 1,024-character skill-loader limit. |
| 7.0 | **Study Data Extraction as a first-class phase (Phase 7b, before RoB):** researcher-confirmed Target Data-Point List (Gate 3b) derived from the PICO/protocol with explicit do-not-extract decisions; extraction-conventions registry (time points, ITT vs per-protocol, endpoint vs change, arm mapping, denominators, table-vs-text precedence); extraction calibration loop — 3–5-study stratified pilots with blind field-level human audit, gated on numeric error rate (default ≤5%) and zero unresolved anchor failures, convergence pilot, guideline lock (Gate 3c); root-cause router for every audited disagreement (transcription → calibration example; convention → registry rule; TDPL defect → logged amendment; upstream misspecification → UPSTREAM_SPECIFICATION_FLAG); mandatory quote-plus-location evidence anchors (PDF hash, page, text-layer line range, structural reference) machine-verified by a shipped script; independent dual extraction with adjudication; 100% human verification (risk-based audit explicitly excluded); dataset locked and hashed (Gate 3d). Phase 6 now persists per-document text layers so anchors resolve; RoB may cite the same layers. Gate 4b retired into Gate 3d; 13 gates total. |
| 6.0 | **Meta-analysis extension (Phases 8c–8e):** per-outcome appropriateness check with SWiM routing; 15-item analytical decision menu compiled into a plain-language Analytical Approach Summary; Analysis Plan Approval gate blocking all statistical execution; Python-or-R preference question with recommended default; beginner-annotated, version-pinned, seeded, hashed analysis scripts (metafor/meta verified on CRAN); mandatory run-yourself-or-skill-executes question with never-auto-execute rule and verify-on-receipt protocol; heterogeneity reporting with prediction intervals and caveats; ≥10-studies rule for funnel asymmetry tests; trim-and-fill as sensitivity only; GRADE with confirm/override and Summary of Findings; statistical methods paragraph cross-checked against the plan; protocol now pre-specifies the synthesis plan per PRISMA items 13a–13f; guardrail recast as "the human decides; the AI recommends; the code computes". |
| 5.0 | **Update-Review Mode (P0):** Phase 0 mode selector (new vs update); reuse of prior protocol/PROSPERO with amendment logging; per-database last-search dates with a confirm-don't-assume rule; prior-corpus ingestion; Phase 4b dedup against the prior corpus with carry-forward of prior decisions; amendments apply at screening only, never widening/narrowing search breadth. **Screening at Scale (P0):** mandatory stable content-derived record IDs (hash of normalised DOI, else normalised title+year); default 250-record execution batches with per-batch raw metadata, append-only checkpointed decisions files, and audit worksheets; checkpoint/resume with logged resumption events; upfront records→batches→sessions throughput estimates and researcher-chosen pacing; hard classifier-vs-reader rule (keyword/triage classifiers are labelled aids, never the authoritative screen). **Pilot → Calibrate → Scale (P0):** new mandatory Phase 5a with 50-record pilots stratified by AI decision × confidence, blind 100% human audit, κ gate (binary retain/discard κ ≥ 0.60 on a fresh pilot), disagreement-driven rule extraction, convergence requirement (a fresh, harder pilot passing without new rules), criteria lock, and new Gate 2a. **Reproducibility honesty (P0):** replaced seed-determinism claims with an explicit Reproducibility Statement (versioned/hashed prompts and criteria, complete decision logging, deterministic seeded sampling, per-batch model-version logging); seed reframed as traceability; transparency block and design principles updated to match. **Date-limiting reference (P1):** per-platform "date added" syntax starting points (Ovid limit fields, EBSCO EM, Scopus ORIG-LOAD-DATE, ProQuest PDN, interface limiters), all gated by a verify-live-with-your-librarian rule; explicit prohibition on substituting free APIs for institutional databases. **Eligibility-rules registry (P1):** versioned machine-readable registry of researcher-approved rules beyond raw PICO (publication-type nuance, condition boundaries, informant-vs-subject, traits-vs-diagnosis, proxy outcomes), written by the calibration loop and injected into the screening prompt; UNCERTAIN routing and confidence levels formally defined. **κ interpretation (P1):** always report κ + raw % agreement + PABAK in 3-category and binary forms, with the kappa-paradox base-rate caveat and direction-of-disagreement rule. **Environment fallbacks (P1):** stdlib urllib HTTP fallback when requests/pip are broken; pure-stdlib deterministic dedup fallback when bib-dedupe won't install; SSL resolution reordered to non-invasive script-scoped option first, with consent-gated certificate-bundle changes and a never-touch-the-OS-trust-store rule; export integrity checks (abstract completeness, hit-count vs export-count reconciliation). **Risk-based audit (P2):** opt-in documented alternative to strict 100% audit at large N (100% of UNCERTAIN/INCLUDE/low-confidence excludes + seeded sample of high-confidence excludes with escalation), with the Cochrane trade-off stated verbatim and reported as a limitation. **Kickoff checklist (P2):** Phase 0 checklist eliciting mode, source-to-role mapping, corpus baseline, last-search dates, API-substitution policy, export requirements, amendment rules, Reviewer B identity, audit depth, and pacing. **PRISMA update layout (P2):** update flow-diagram bookkeeping (prior-review column, records removed as already in prior corpus, carried-forward decisions, combined included-studies total). |
