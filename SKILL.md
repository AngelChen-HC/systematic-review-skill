---
name: systematic-review-coordinator
version: 4.1
description: >
  Orchestrates a rigorous, auditable, and PRISMA-compliant systematic
  literature review workflow with full human oversight and independent
  dual screening. Automates search construction, retrieval, deduplication,
  and screening while enforcing 100% human audit of all inclusion/exclusion
  decisions and risk of bias assessments. Includes AI transparency reporting
  and generates a researcher-editable PRISMA flow diagram. Designed to be
  used by researchers with no prior coding experience. Activates when a
  user requests a systematic review or literature search based on a
  research question.
---

# Systematic Review Coordinator — Optimised Skill (v4.1)

---

## Standards Referenced

This skill is designed to align with the following verified standards and guidelines. No citation in this document is fabricated; all have been individually fact-checked.

- **PRISMA 2020** — Page MJ, McKenzie JE, Bossuyt PM, et al. "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews." *BMJ* 2021;372:n71. 27-item checklist.
- **PRISMA-S** — Rethlefsen ML, Kirtley S, Waffenschmidt S, et al. "PRISMA-S: an extension to the PRISMA Statement for Reporting Literature Searches in Systematic Reviews." *Systematic Reviews* 2021;10(1):39. 16-item checklist for search reporting.
- **Cochrane Handbook for Systematic Reviews of Interventions, Version 6.5** (August 2024, with chapter-level updates v6.5.1 in March 2025). Available at: https://www.cochrane.org/authors/handbooks-and-manuals/handbook
- **AMSTAR-2** — Shea BJ, Reeves BC, Wells G, et al. "AMSTAR 2: a critical appraisal tool for systematic reviews." *BMJ* 2017;358:j4008. 16 items: 7 critical domains, 9 non-critical domains.
- **PRISMA-trAIce** — Holst D, et al. "Transparent Reporting of Artificial Intelligence in Comprehensive Evidence Synthesis: Development of the PRISMA-trAIce Checklist." *JMIR AI* 2025;4:e80247. 14-item checklist. Note: this is a foundational proposal that has not yet undergone Delphi validation or EQUATOR Network registration. Used here as emerging guidance only.
- **RAISE (2025)** — Responsible AI for Systematic Evidence recommendations, jointly supported by Cochrane, Campbell Collaboration, JBI, and Collaboration for Environmental Evidence. Provides principles for responsible AI use in evidence synthesis.

**Note on AI-SR benchmarking literature:** Published studies on LLM performance in systematic review tasks (e.g., Khraisha et al. 2024 on GPT-4 screening; Wang et al. 2023 on Boolean query generation) inform the design of this skill's performance monitoring. However, specific performance claims are not made — actual performance depends on the review topic, model version, and prompt. The ground-truth validation system (Phase 5) measures performance empirically for each review rather than relying on literature estimates.

---

## Boundaries and Guardrails

- **DO NOT** synthesise scientific conclusions, perform unsupervised meta-analytical mathematics, or write the interpretive discussion.
- **DO NOT** use zero-shot prompting for abstract screening. All screening must use structured criterion-by-criterion evaluation with explicit evidence grounding.
- **DO NOT** use the AI model to probabilistically deduplicate records. Deduplication must be deterministic.
- **DO NOT** finalise any inclusion or exclusion decision without explicit human confirmation. The AI produces recommendations; the human decides.
- **DO NOT** use creative or probabilistic inference. All LLM calls must use `temperature=0` to ensure deterministic, reproducible outputs that rigorously adhere to the provided research question and criteria.
- **DO NOT** proceed past any human-approval gate without logged confirmation.
- **DO NOT** conduct risk of bias assessment without the researcher providing their chosen framework.
- **DO NOT** execute any Python script without first providing the researcher with clear, step-by-step setup and run instructions suitable for someone with no coding experience.
- **DO NOT** cite, reference, or rely on any guideline, framework, or publication that has not been independently verified as real and currently accessible.

---

## AI Transparency Block

This block must be included in the audit log and in any publication or report arising from the review.

```
AI_TRANSPARENCY:
  model_id: {exact model identifier}
  model_version: {full version string}
  model_provider: {provider name, e.g., Anthropic}
  inference_api_version: {API version used}
  prompt_version: {skill version, e.g., v4.1}
  temperature: 0
  seed: {researcher-set seed}

  role_of_ai:
    - Screening recommendation only (all decisions confirmed by human)
    - Search string generation (approved by human before execution)
    - Risk of bias assessment assistance (all judgments confirmed by human)
    - PRISMA diagram generation (finalised by human)
    - Active learning calibration (prompt updated with human-approved correction examples between batches; model not fine-tuned)

  known_limitations:
    - AI may produce reasoning that appears plausible but misinterprets study content
    - AI may systematically under- or over-include certain study types depending on training data
    - Outputs are deterministic for a given model+seed+prompt, but may differ across model versions or providers
    - Performance metrics are internal to this review and not externally benchmarked
    - AI-assisted screening does not replace independent human review; it augments it

  disclosure:
    - This review used AI-assisted screening with 100% human audit and independent dual screening
    - AI involvement is reported in accordance with PRISMA-trAIce (experimental) and RAISE (2025) guidance
```

---

## Configuration Block

Before any work begins, the following parameters must be set and logged. Present this configuration to the researcher for confirmation.

```json
{
  "config": {
    "model_id": "string — exact model identifier (e.g., claude-sonnet-4-20250514)",
    "model_version": "string — full version string",
    "model_provider": "string — e.g., Anthropic",
    "inference_api_version": "string — API version",
    "temperature": 0,
    "seed": "integer — SET BY THE RESEARCHER (see below)",
    "prompt_version": "v4.1",
    "max_tokens_screening": "integer — max output tokens for screening calls",
    "review_title": "string",
    "principal_investigator": "string",
    "date_initiated": "ISO-8601",
    "working_directory": "string — SET BY THE RESEARCHER (see below)",
    "full_text_directory": "string — SET BY THE RESEARCHER (see below)"
  }
}
```

**Seed:** Ask the researcher to provide an integer seed value for reproducibility. Explain: "This seed ensures your screening results are reproducible. Any reviewer using the same model, prompt version, and seed will get identical AI outputs. Please provide an integer (e.g., 42, 12345), or I can generate one for your approval." Log the seed immutably once confirmed.

**Temperature=0:** Ensures deterministic outputs with zero creative latitude, strict adherence to criteria.

**Directories:** Ask the researcher where they would like files saved. Provide sensible defaults (e.g., `~/systematic_review/`) but allow the researcher to specify any path. This applies to all working files and especially to full-text PDFs (Phase 6).

---

## Structural Overview

This skill operates in **11 sequential phases** with **6 mandatory human-approval gates**. No phase may begin until the preceding phase is complete and, where applicable, human approval is logged.

```
Phase 0:  Protocol Generation & Registration
          ↓
Phase 1:  Initialisation, Configuration & Audit Logging
          ↓
Phase 2:  PICO Extraction, Study Design & Language Restrictions,
          Query Generation & Database Planning
          ↓ ── GATE 1: Human approves search strategy & database plan ──
Phase 3:  Database Retrieval (with institutional SSO guidance)
          ↓
Phase 4:  Deterministic Deduplication (HITL for suspected duplicates)
          ↓
Phase 5:  Title-Abstract Screening (AI-assisted) + Performance Monitoring
          ↓ ── GATE 2: 100% human audit + 20% ground-truth validation ──
Phase 5b: Independent Dual Screening & Conflict Resolution
          ↓ ── GATE 2b: Resolve all conflicts; compute Cohen's Kappa ──
Phase 6:  Full-Text Retrieval (researcher-set directory)
          ↓
Phase 7:  Full-Text Screening + Performance Monitoring + Dual Screening
          ↓ ── GATE 3: 100% human audit + conflict resolution ──
Phase 8:  Risk of Bias Assessment (researcher-provided framework)
          ↓ ── GATE 4: 100% human audit of all RoB judgments ──
Phase 9:  PRISMA Flow Diagram Generation
          ↓ ── GATE 5: Researcher finalises diagram ──
Phase 10: Export & Reporting (including AI Transparency Statement)
```

**Failure recovery:** If the process is interrupted at any phase, it can be resumed from the last completed phase by validating the audit log's hash chain integrity. Log the resumption event, including the phase resumed from and the chain verification result.

---

## Audit Log Specification

### Initialisation

Immediately create `audit_log.json` using the schema below. Every action, decision, configuration change, human override, and performance metric is logged here with a timestamp. This is the single source of truth for the review.

### Schema

```json
{
  "schema_version": "4.1",
  "review_metadata": {
    "review_title": "",
    "protocol_id": "",
    "prospero_id": "",
    "date_initiated": "ISO-8601",
    "principal_investigator": "",
    "config": {
      "model_id": "",
      "model_version": "",
      "model_provider": "",
      "inference_api_version": "",
      "temperature": 0,
      "seed": null,
      "prompt_version": "v4.1"
    },
    "ai_transparency": {}
  },
  "chain_integrity": {
    "algorithm": "SHA-256",
    "genesis_hash": ""
  },
  "entries": []
}
```

### Entry Format

Every log entry must conform to:

```json
{
  "entry_id": "UUID-v4",
  "created_at": "ISO-8601 — date and time this entry was created",
  "phase": "0–10",
  "action": "descriptive string",
  "actor": "AI | HUMAN | SYSTEM",
  "input_hash": "SHA-256 of input data",
  "output_hash": "SHA-256 of output data (for LLM calls, hash the raw response)",
  "output": {},
  "decision": "INCLUDE | EXCLUDE | UNCERTAIN | APPROVED | OVERRIDE | null",
  "structured_rationale": {
    "criteria_assessments": [],
    "evidence_quotes": [],
    "decision_rule_applied": "",
    "summary": ""
  },
  "human_review": {
    "reviewed": true,
    "reviewer_id": "string",
    "agreed_with_ai": true,
    "override_reason": "string | null",
    "reviewed_at": "ISO-8601 — date and time of human review"
  },
  "performance_flag": null,
  "previous_entry_hash": "SHA-256 of preceding entry"
}
```

**Key changes from v3.0:**
- `output_hash` added: SHA-256 of every LLM response for reproducibility verification.
- `structured_rationale` replaces free-form `reasoning`: forces a machine-parseable rationale schema instead of raw CoT text, improving transparency and auditability per PRISMA-trAIce guidance.

**Every entry records the date and time of creation.** The `created_at` field uses full ISO-8601 format including timezone (e.g., `2026-04-13T14:32:07+01:00`). Human review actions additionally record `reviewed_at`. This applies to all entries across all phases.

### Chain Integrity

Each entry's `previous_entry_hash` contains the SHA-256 hash of the entire preceding entry (serialised as canonical JSON). This creates a tamper-evident chain. On review export, provide a verification script that validates the full chain.

---

## Phase 0: Protocol Generation & Registration

### Instructions

1. Ask the researcher for their research question.
2. Ask whether they wish to include grey literature.
3. Ask the researcher to provide or confirm:
   - The seed value for reproducibility.
   - Their target databases.
   - Any date restrictions (or explicitly "N/A — no date restrictions").
   - Any language restrictions (or explicitly "N/A — no language restrictions").
   - Any study design restrictions (or explicitly "N/A — no study design restrictions"). See Phase 2 for detailed cues.
4. Generate a formal review protocol document containing:
   - Review title and registration intent.
   - Background and rationale (brief, from researcher input).
   - Objectives (derived from PICO extraction in Phase 2 — protocol is finalised after Phase 2).
   - Eligibility criteria (Population, Intervention, Comparator, Outcome, Study designs, Date range, Language).
   - Information sources (databases, grey literature sources, citation chasing strategy).
   - Search strategy (populated after Phase 2).
   - Selection process (description of AI-assisted screening with 100% human audit and independent dual screening).
   - Data collection process (if applicable).
   - Risk of bias assessment method (placeholder until researcher provides framework in Phase 8).
   - AI involvement disclosure (reference the AI Transparency Block).
   - Synthesis plan (out of scope for this skill — note this explicitly).
   - Publication bias: note that publication bias assessment (e.g., funnel plots, Egger's test) is the researcher's responsibility during synthesis, and is outside the scope of this skill.
5. Present the protocol to the researcher for review and approval.
6. Prompt the researcher to register on PROSPERO (https://www.crd.york.ac.uk/prospero/) or equivalent and record the registration ID in the audit log.
7. Lock the protocol. Any subsequent deviation must be logged with explicit justification and researcher approval.

### Logged Outputs
- Protocol document (full text, hashed).
- PROSPERO registration ID (or "not registered" with justification).
- Researcher approval timestamp (`created_at`).

---

## Phase 1: Initialisation, Configuration & Audit Logging

### Instructions

1. Create `audit_log.json` with the schema above.
2. Present the configuration block to the researcher. Require them to:
   - Confirm or set the model identifier, model provider, and inference API version.
   - **Set the seed value.**
   - Confirm temperature=0.
   - **Set the working directory** for all review files.
   - **Set the full-text PDF directory** (default: `{working_directory}/full_texts/`).
3. Populate the AI Transparency Block and log it as the first audit entry (with `created_at` timestamp).
4. Create the working directory structure at the researcher's chosen path:

```
{working_directory}/
├── audit_log.json
├── protocol.md
├── ai_transparency_statement.md
├── searches/
├── records/
├── full_texts/          ← or researcher's custom path
├── screening/
│   ├── title_abstract/
│   ├── full_text/
│   └── dual_screening/
├── risk_of_bias/
├── prisma/
└── exports/
```

---

## Phase 2: PICO Extraction, Study Restrictions & Query Generation

### Step 2.1: PICO Extraction

1. Cue the researcher to frame their question using PICO, PICOT, or PEO frameworks.
2. Parse the researcher's natural-language objective into a strict JSON schema:

```json
{
  "pico": {
    "population": {
      "description": "",
      "mesh_terms": [],
      "emtree_terms": [],
      "apa_thesaurus_terms": [],
      "free_text_synonyms": []
    },
    "intervention": { "...same structure..." },
    "comparator": { "...same structure..." },
    "outcome": { "...same structure..." },
    "time_frame": "if PICOT — or N/A",
    "exposure": "if PEO — or N/A"
  }
}
```

3. Generate controlled vocabulary terms (MeSH, Emtree, APA Thesaurus) AND free-text synonyms for each PICO node.

### Step 2.2: Study Design & Language Restrictions

Explicitly cue the researcher to specify each of the following. If the researcher does not wish to restrict, they must explicitly state "N/A" so the decision is documented:

**Study design restrictions:**
> "Which study designs will you include? For example:
> - Randomised controlled trials (RCTs) only
> - RCTs and quasi-experimental designs
> - Observational studies (cohort, case-control, cross-sectional)
> - Qualitative studies
> - Mixed-methods studies
> - All study designs (no restriction)
>
> If you do not wish to restrict by study design, please write **N/A — no study design restrictions** so this is recorded in the protocol."

**Language restrictions:**
> "Which languages will you include? For example:
> - English only
> - English and [other languages]
> - All languages (no restriction)
>
> If you do not wish to restrict by language, please write **N/A — no language restrictions** so this is recorded in the protocol."

**Date restrictions:**
> "What date range will you search? For example:
> - Studies published from 2010 to present
> - No date restriction
>
> If you do not wish to restrict by date, please write **N/A — no date restrictions** so this is recorded in the protocol."

Log all responses with `created_at` timestamp. Record explicit "N/A" responses — these are protocol decisions and must be documented.

### Step 2.3: Search String Generation & Cross-Validation

1. Translate the PICO JSON into distinct Boolean search strings using exact field tags for each target database:
   - PubMed: `[tiab]`, `[MeSH Terms]`, `[pt]` for publication types
   - Cochrane Library: `:ti,ab,kw`
   - Web of Science: `TS=`, `TI=`
   - EBSCO/CINAHL: field codes as appropriate
   - Embase: `/exp`, `:ti,ab`
   - Scopus: `TITLE-ABS-KEY()`
   - PsycINFO: field codes as appropriate

2. **Cross-validate each search string** by:
   - Checking Boolean syntax against the target database's documented query language (parentheses matching, operator support, field tag validity).
   - Verifying that all MeSH/Emtree terms exist in the relevant thesaurus. If a term is not a valid controlled vocabulary entry, flag it and suggest alternatives.
   - Confirming that truncation operators (e.g., `*` for PubMed, `$` for Ovid) are correct for each database.
   - Checking that study design filters and language/date limiters use the correct syntax for each database.
   - Presenting a validation summary to the researcher.

3. Generate a citation-chasing strategy: "After screening, forward and backward citation tracking of all included studies."

### Step 2.3b: API Query Translation

**Purpose:** The search strings generated in Step 2.3 use **web-interface syntax** specific to each database. However, the databases searched programmatically in Phase 3 (PubMed via NCBI E-utilities, Europe PMC, ClinicalTrials.gov, OpenAlex) each use **different API query grammars**. Passing PubMed-style field tags (e.g., `[tiab]`, `[MeSH Terms]`) directly to other APIs causes those tags to be treated as literal search text, returning zero results.

This step translates the approved web-interface search strings into API-compatible queries for each automated database. The web-interface strings remain unchanged for manual search and for the published search strategy appendix.

**CRITICAL: Each API has its own query grammar. No two are interchangeable. The following translation rules and examples must be followed exactly.**

#### PubMed / MEDLINE (via NCBI E-utilities)

**API endpoint:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`

**Translation rule:** The PubMed web-interface search string can be passed directly to the E-utilities `term` parameter — E-utilities accepts native PubMed syntax including `[tiab]`, `[MeSH Terms]`, `[pt]`, `[la]`, `[dp]`.

**Mandatory overrides:**
- `retmax=10000` (the E-utilities default is 20, which silently truncates results)
- `retmode=json`
- `usehistory=y` (enables pagination beyond 10,000 results via `retstart` offsets)
- If more than 10,000 results: segment by date range or paginate using `retstart`

**Rate limiting:** 3 requests/second without API key; 10/second with key. Always include `tool` and `email` parameters for NCBI compliance.

**One-shot example (PICO: CBT for depression in adults vs pharmacotherapy, RCTs, 2015–2025):**

PubMed web-interface string (from Step 2.3):
```
("cognitive behavioral therapy"[tiab] OR "cognitive behaviour therapy"[tiab] OR "CBT"[tiab]) AND ("depression"[MeSH Terms] OR "depressive disorder"[MeSH Terms] OR "depression"[tiab] OR "depressive"[tiab]) AND ("drug therapy"[MeSH Subheading] OR "pharmacotherapy"[tiab] OR "antidepressive agents"[MeSH Terms] OR "antidepressant*"[tiab]) AND ("randomized controlled trial"[pt] OR "controlled clinical trial"[pt] OR "randomized"[tiab] OR "randomised"[tiab]) AND 2015:2025[dp] AND English[la]
```

API query (passed as the `term` parameter — identical to web string):
```
term=("cognitive behavioral therapy"[tiab] OR "cognitive behaviour therapy"[tiab] OR "CBT"[tiab]) AND ("depression"[MeSH Terms] OR "depressive disorder"[MeSH Terms] OR "depression"[tiab] OR "depressive"[tiab]) AND ("drug therapy"[MeSH Subheading] OR "pharmacotherapy"[tiab] OR "antidepressive agents"[MeSH Terms] OR "antidepressant*"[tiab]) AND ("randomized controlled trial"[pt] OR "controlled clinical trial"[pt] OR "randomized"[tiab] OR "randomised"[tiab]) AND 2015:2025[dp] AND English[la]
&retmax=10000&retmode=json&usehistory=y
```

---

#### Europe PMC (via REST API)

**API endpoint:** `https://www.ebi.ac.uk/europepmc/webservices/rest/search`

**Translation rules — Europe PMC uses colon-prefix `FIELD:term` syntax, NOT bracket-suffix `term[field]` syntax:**

| PubMed syntax | Europe PMC syntax | Notes |
|---|---|---|
| `"term"[tiab]` | `TITLE_ABS:"term"` | Title and abstract combined field |
| `"term"[ti]` | `TITLE:"term"` | Title only |
| `"term"[ab]` | `ABSTRACT:"term"` | Abstract only |
| `"term"[MeSH Terms]` | `KW:"term"` | `KW` searches keywords including MeSH terms |
| `"term"[MeSH Subheading]` | `KW:"term"` | Use `KW` for MeSH subheadings too |
| `term*` (truncation) | `term*` | Truncation works the same way |
| `"type"[pt]` | `PUB_TYPE:"type"` | Publication type |
| `YYYY:YYYY[dp]` | `PUB_YEAR:[YYYY TO YYYY]` | Date range (year only). Use `3000` for "to present". |
| `English[la]` | `LANG:eng` | ISO 639-3 language codes |
| `AND`, `OR`, `NOT` | `AND`, `OR`, `NOT` | Boolean operators (must be UPPERCASE in both) |

**Mandatory API parameters:**
- `format=json`
- `resultType=core` (returns full metadata including abstract)
- `pageSize=1000` (default is 25; max is 1000)
- `cursorMark=*` (required for cursor-based pagination; follow `nextCursorMark` for subsequent pages)
- `synonym=true` (enables MeSH synonym expansion; set `false` for exact matching)

**One-shot example (same PICO as above):**

Translated API query:
```
query=(TITLE_ABS:"cognitive behavioral therapy" OR TITLE_ABS:"cognitive behaviour therapy" OR TITLE_ABS:"CBT") AND (KW:"depression" OR KW:"depressive disorder" OR TITLE_ABS:"depression" OR TITLE_ABS:"depressive") AND (KW:"drug therapy" OR TITLE_ABS:"pharmacotherapy" OR KW:"antidepressive agents" OR TITLE_ABS:"antidepressant*") AND (PUB_TYPE:"randomized controlled trial" OR PUB_TYPE:"controlled clinical trial" OR TITLE_ABS:"randomized" OR TITLE_ABS:"randomised") AND PUB_YEAR:[2015 TO 3000] AND LANG:eng
&format=json&resultType=core&pageSize=1000&cursorMark=*&synonym=true
```

---

#### ClinicalTrials.gov (API v2)

**API endpoint:** `https://clinicaltrials.gov/api/v2/studies`

**Translation rules — ClinicalTrials.gov v2 uses STRUCTURED PARAMETERS, not a single Boolean query string. The search must be decomposed into PICO-mapped parameters:**

| PICO component | API parameter | What it searches |
|---|---|---|
| Population (condition/disease) | `query.cond` | Conditions, condition MeSH terms, titles, keywords |
| Intervention | `query.intr` | Interventions, intervention MeSH terms, arm labels |
| Outcome | `query.outc` | Primary, secondary, and other outcomes |
| General keywords | `query.term` | All study fields (broad free-text search) |
| Title-specific | `query.titles` | Study titles and acronyms only |

**Boolean operators** (`AND`, `OR`, `NOT` — UPPERCASE) work **within** each `query.*` parameter. Quoted phrases enforce exact matching.

**ClinicalTrials.gov indexes trial registrations, not journal articles.** It has no `[tiab]` field, no `[au]` field. PubMed field tags have no meaning here. The Essie search engine performs automatic UMLS concept expansion (e.g., "heart attack" also finds "myocardial infarction").

**Filter parameters use case-sensitive enumerated values:**
- `filter.overallStatus`: `RECRUITING`, `COMPLETED`, `ACTIVE_NOT_RECRUITING`, `TERMINATED`, `NOT_YET_RECRUITING`, `SUSPENDED`, `ENROLLING_BY_INVITATION`, `WITHDRAWN`, `UNKNOWN` (pipe-delimited for multiple values, e.g., `RECRUITING|COMPLETED`)
- `filter.phase`: `EARLY_PHASE1`, `PHASE1`, `PHASE2`, `PHASE3`, `PHASE4`, `NA`
- `filter.studyType`: `INTERVENTIONAL`, `OBSERVATIONAL`, `EXPANDED_ACCESS`

**Mandatory API parameters:**
- `format=json`
- `countTotal=true` (returns total result count)
- `pageSize=1000` (default is 10; max is 1000)
- Pagination via `pageToken` (use `nextPageToken` from response for subsequent pages)

**Date filtering within parameters:** Use `AREA[StartDate]RANGE[YYYY-MM-DD,MAX]` within `query.term` for date ranges.

**One-shot example (same PICO as above):**

Translated API query:
```
query.cond="depression" OR "depressive disorder"
&query.intr="cognitive behavioral therapy" OR "cognitive behaviour therapy" OR "CBT"
&filter.overallStatus=RECRUITING|COMPLETED|ACTIVE_NOT_RECRUITING|NOT_YET_RECRUITING
&format=json&countTotal=true&pageSize=1000
```

**Note:** ClinicalTrials.gov searches for trial registrations, not published articles. Language and publication-type filters do not apply. Date filters and outcome terms can be added via `query.outc` and `query.term` with `AREA[]` syntax if needed.

---

#### OpenAlex (via REST API)

**API endpoint:** `https://api.openalex.org/works`

**Translation rules — OpenAlex uses two mechanisms: `search` parameter (full-text Boolean search) and `filter` parameter (structured attribute filters with dot-path syntax):**

| PubMed syntax | OpenAlex approach | Notes |
|---|---|---|
| `"term"[tiab]` | `filter=title_and_abstract.search:"term"` | Or use the `search` parameter for broader matching |
| `"term"[MeSH Terms]` | Include in `search` parameter as free text | OpenAlex has no MeSH vocabulary; uses its own Topics taxonomy |
| `"type"[pt]` | `filter=type:article` | Values: `article`, `book`, `dataset`, `preprint`, etc. |
| `YYYY:YYYY[dp]` | `filter=publication_year:YYYY-YYYY` | Hyphen-separated range |
| `English[la]` | `filter=language:en` | ISO 639-1 two-letter codes |
| `AND`, `OR`, `NOT` | `AND`, `OR`, `NOT` in `search` param | Boolean operators must be UPPERCASE |

**The `search` parameter** searches across titles, abstracts, and fulltext. It supports Boolean `AND`, `OR`, `NOT` (UPPERCASE), quoted phrases, and parentheses. Including any of AND, OR, NOT enables Boolean mode.

**The `filter` parameter** uses comma-separated dot-path filters (AND logic). Pipe `|` within a filter = OR logic. Exclamation `!` = negation.

**Key search filters:** `title.search`, `abstract.search`, `title_and_abstract.search`, `fulltext.search`, `default.search`. Append `.no_stem` to disable stemming.

**Mandatory API parameters:**
- `mailto=researcher@institution.edu` (for polite pool — faster, more reliable; use the researcher's actual email)
- `per_page=100` (default is 25; max is 100)
- Cursor pagination: `cursor=*` for first page, follow `meta.next_cursor` for subsequent pages
- Rate limits: 10 requests/second, 100,000/day

**One-shot example (same PICO as above):**

Translated API query:
```
search=("cognitive behavioral therapy" OR "cognitive behaviour therapy" OR "CBT") AND ("depression" OR "depressive disorder" OR "depressive") AND ("pharmacotherapy" OR "antidepressant" OR "drug therapy") AND ("randomized" OR "randomised" OR "controlled trial")
&filter=publication_year:2015-2025,type:article,language:en
&per_page=100&cursor=*&mailto=researcher@institution.edu
```

---

#### Scopus (via pybliometrics)

**Translation rule:** The Scopus web-interface string from Step 2.3 (using `TITLE-ABS-KEY()`) is compatible with `pybliometrics`' `ScopusSearch` query parameter. Pass it directly. Scopus requires an institutional API key.

**Mandatory:** Set `subscriber=True` if your institution has a Scopus subscription. Use `download=True`. Pagination is handled automatically by `pybliometrics`.

---

#### Summary of API translation requirements

| Database | Translation needed? | Core syntax change |
|---|---|---|
| PubMed (E-utilities) | No (same syntax) | Override `retmax=10000` |
| Europe PMC | **Yes** | `[tiab]` → `TITLE_ABS:`, `[MeSH Terms]` → `KW:` |
| ClinicalTrials.gov v2 | **Yes — decompose** | PICO components → structured `query.*` parameters |
| OpenAlex | **Yes** | Free-text `search` + `filter` dot-path syntax |
| Scopus (pybliometrics) | No (same syntax) | Pass web string directly |

**All translated API queries must be included in the Gate 1 review for researcher approval.**

### Step 2.4: Additional Databases (Plan-First, Human-in-the-Loop)

Ask the researcher:
> "Are there any additional databases you would like to search beyond the standard set? If so, please provide:
> 1. The name of the database.
> 2. A direct link to the database (or its API documentation, if available).
>
> I will analyse the database, create a plan for how to search it, and present the plan for your approval before taking any action."

**If the researcher provides additional databases:**

For each additional database, follow this strict plan-first protocol:

1. **Analyse:** Fetch the provided link. Examine the database's search interface, query syntax, field tags, API availability, export formats, and any access requirements.

2. **Determine access method:** Establish whether the database will be searched via API (automated) or via web interface (manual).

3. **Plan:** Present a structured plan to the researcher with access method, query syntax, proposed search string, export format, access requirements, and limitations.

4. **If API access is available — generate an API-specific query:**
   - Identify the API's query grammar (field tag syntax, parameter structure, Boolean support, pagination, rate limits, authentication).
   - Translate the PICO search from the approved PubMed string into the API's native syntax, following the same principle as Step 2.3b: each API has its own grammar and no two are interchangeable.
   - Provide the translated API query alongside the web-interface string.
   - Include an SSL/network check for the API endpoint (see Phase 3 Network Environment Check).
   - Document the API endpoint URL, all required parameters, pagination settings, and rate limits.

5. **If manual search only — generate step-by-step instructions:**
   - Provide the exact URL to navigate to.
   - Specify which search interface to use (e.g., "Advanced Search").
   - Provide the database-native search string from Step 2.3.
   - Explain how to apply date, language, and study design filters in the interface.
   - Specify the export format (RIS preferred, BibTeX as fallback, CSV as last resort).
   - Specify the expected filename and save location.

6. **Confirm:** Wait for the researcher to approve, modify, or reject the plan (including any translated API query). Log the plan and the researcher's response.

7. **Execute:** Only after explicit approval, proceed with the search using the agreed plan.

### Step 2.5: Logging

Log every search string, every synonym decision, every cross-validation result, every additional-database plan, and the PICO JSON. **Every log entry records `created_at` with full ISO-8601 date and time.**

### ── GATE 1: Search Strategy & Database Plan Approval ──

**MANDATORY.** Present all generated search strings (including cross-validation reports), all API-translated queries (from Step 2.3b), and any additional-database plans to the researcher. The researcher must:
- Review each web-interface string for completeness and accuracy.
- Review each API-translated query for correct syntax and semantic equivalence to the web-interface string.
- Review each cross-validation finding.
- Approve, modify, or reject each string, each API query, and each database plan.
- Confirm the final set.

Log: Researcher ID, approval `created_at` timestamp, any modifications (with diff), and final approved strings (both web-interface and API versions).

**Do not proceed to Phase 3 until Gate 1 is passed.**

---

## Phase 3: Database Retrieval

### Institutional Access Guidance

Before executing any retrieval scripts, present the following guidance to the researcher:

> "**Institutional access:** Some databases (e.g., Scopus, Web of Science, CINAHL, Embase) require institutional access. If you are affiliated with a university or research institution:
>
> 1. **Log into your institution's Single Sign-On (SSO)** via your library's website or database portal before running the retrieval scripts.
> 2. Some APIs (e.g., Scopus via `pybliometrics`) require an **API key tied to your institutional IP range**. If you are working remotely, you may need to connect to your institution's **VPN** first.
> 3. If a database does not offer API access through your institution, you can:
>    - Search manually through the database's web interface while logged into your SSO.
>    - Export results in `.ris` or `.bib` format.
>    - Place the exported file in `{working_directory}/records/` and I will integrate it into the unified dataset.
>
> **I will now provide a retrieval script. Before running it, ensure you have institutional access set up as described above.**"

### Python Environment Setup (for users with no coding experience)

Before providing any Python script in this or any subsequent phase, present the following setup instructions:

> **"How to set up Python and run the script (first-time setup):"**
>
> These instructions are for researchers who have never used Python before. You only need to do the setup once — after that, running scripts is a single command.
>
> ---
>
> **Step 1: Check if Python is already installed**
>
> Open your computer's command line:
> - **Windows:** Press the Windows key, type `cmd`, and press Enter to open Command Prompt.
> - **Mac:** Open the "Terminal" app (find it in Applications → Utilities, or search for "Terminal" in Spotlight).
> - **Linux:** Open your terminal application.
>
> Type the following and press Enter:
> ```
> python3 --version
> ```
> If you see something like `Python 3.10.12`, Python is installed. Skip to Step 3.
> If you see an error like "command not found", proceed to Step 2.
>
> ---
>
> **Step 2: Install Python**
>
> - **Windows:** Go to https://www.python.org/downloads/ and click "Download Python 3.x". Run the installer. **IMPORTANT: Check the box that says "Add Python to PATH" before clicking Install.**
> - **Mac:** Go to https://www.python.org/downloads/ and download the Mac installer. Run it and follow the prompts.
> - **Linux:** Run `sudo apt update && sudo apt install python3 python3-pip python3-venv` in your terminal.
>
> After installation, close and reopen your terminal, then verify with `python3 --version`.
>
> ---
>
> **Step 3: Create a project folder and virtual environment**
>
> In your terminal, type these commands one at a time, pressing Enter after each:
> ```
> cd {working_directory}
> python3 -m venv review_env
> ```
>
> Now activate the virtual environment:
> - **Windows:** `review_env\Scripts\activate`
> - **Mac/Linux:** `source review_env/bin/activate`
>
> You should see `(review_env)` appear at the start of your terminal line.
>
> ---
>
> **Step 4: Install the required libraries**
>
> With the virtual environment active, type:
> ```
> pip install [list of libraries for this specific script]
> ```
> Wait for the installation to complete. You only need to do this once per project.
>
> ---
>
> **Step 5: Save and run the script**
>
> 1. Copy the script I provide below.
> 2. Open a plain text editor (Notepad on Windows, TextEdit on Mac in plain text mode, or any code editor).
> 3. Paste the script and save it as `[script_name].py` in your `{working_directory}/` folder.
> 4. In your terminal (with the virtual environment active), type:
>    ```
>    python3 [script_name].py
>    ```
> 5. The script will run and tell you what it is doing. Follow any prompts that appear.
>
> ---
>
> **If something goes wrong:**
> - If you see "ModuleNotFoundError: No module named 'X'", run `pip install X` and try again.
> - If you see "Permission denied", try adding `sudo` before the command (Mac/Linux) or running Command Prompt as Administrator (Windows).
> - Copy and paste the full error message back to me and I will help you fix it.

### Network Environment Check

**CRITICAL — Present this BEFORE the retrieval script.** University and hospital networks commonly perform SSL/TLS inspection by intercepting HTTPS traffic and re-signing it with an institutional CA certificate. Python's default SSL context does not trust these certificates, causing **all** HTTPS API calls to fail with `SSL: CERTIFICATE_VERIFY_FAILED`.

Provide the following diagnostic script and resolution paths to the researcher:

> **"Before running the main retrieval script, run this quick network check to verify your connection to the database APIs:"**
>
> Save this as `network_check.py` and run it:
> ```python
> import urllib.request, ssl, sys
> endpoints = [
>     ("PubMed (NCBI)", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?retmode=json"),
>     ("Europe PMC", "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=test&format=json&pageSize=1"),
>     ("ClinicalTrials.gov", "https://clinicaltrials.gov/api/v2/studies?pageSize=1&format=json"),
>     ("OpenAlex", "https://api.openalex.org/works?search=test&per_page=1"),
> ]
> print("Network connectivity check:")
> all_ok = True
> for name, url in endpoints:
>     try:
>         urllib.request.urlopen(url, timeout=15)
>         print(f"  ✅ {name}: OK")
>     except Exception as e:
>         all_ok = False
>         err = str(e)
>         if "CERTIFICATE_VERIFY_FAILED" in err or "SSL" in err:
>             print(f"  ❌ {name}: SSL ERROR — your network may intercept HTTPS traffic.")
>         else:
>             print(f"  ❌ {name}: {err}")
> if not all_ok:
>     print("\n⚠️  One or more endpoints failed. See resolution steps below.")
>     print("   Most likely your institution's firewall performs SSL inspection.")
>     print("   Please share this output with me and I will help you fix it.")
> else:
>     print("\n✅ All endpoints reachable. You can proceed with the retrieval script.")
> ```

**If SSL errors are detected, present these resolution paths in order of preference:**

> **"Your network appears to intercept HTTPS connections (SSL inspection). This is common on university and hospital networks. Here are three ways to fix it, from most secure to least:**
>
> **Option A (recommended): Install your institution's CA certificate into Python**
> 1. Contact your IT help desk and ask for your institution's root CA certificate file (usually a `.pem` or `.crt` file).
> 2. Find Python's certificate store by running: `python3 -c "import certifi; print(certifi.where())"`
> 3. Open the file from step 2 in a text editor and paste the contents of your institution's certificate at the end. Save.
> 4. Re-run `network_check.py` to verify.
>
> **Option B: Point Python to your system's certificate bundle**
> - **Mac/Linux:** Run the retrieval script with this environment variable set:
>   `SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt python3 retrieval_script.py`
>   (The exact path may vary; try `/etc/ssl/cert.pem` on Mac.)
> - **Windows:** Run:
>   `set SSL_CERT_FILE=C:\path\to\your\institution\ca-bundle.crt`
>   then run the script.
>
> **Option C (last resort — less secure): Disable SSL verification for this script only**
> This skips certificate checking entirely. Only use this if Options A and B fail, and only for the retrieval script.
> The retrieval script includes a `--no-ssl-verify` flag for this purpose. Running with this flag will print a security warning.
> **Note:** This does not affect your browser or other applications."

### Retrieval Script

Provide a Python script using `requests` for all HTTP-based API access, plus `pybliometrics` for Scopus. **Do not use `metapub`.** Direct NCBI E-utilities calls via `requests` give full control over SSL handling, pagination, query encoding, and error diagnostics.

- `requests` + `certifi` — All HTTP-based API access (PubMed E-utilities, Europe PMC, ClinicalTrials.gov, OpenAlex, Crossref)
- `pybliometrics` — Scopus (requires institutional API key)

**Note on deprecated/replaced libraries:** This skill does not use `metapub` (adds an abstraction layer with quirks including Borg singleton state, creation-date-based date filtering, and limited error visibility), `pytrials` (built for the retired ClinicalTrials.gov classic API), or `ebscopy` (unmaintained). For EBSCO databases (CINAHL, PsycINFO via EBSCO), use manual search and export (see below). For Web of Science, the `clarivate-wos-starter-python-client` is available from GitHub (not PyPI) — alternatively, use manual search and export.

**Before the script,** list the exact `pip install` command:
```
pip install requests certifi pybliometrics==4.4.1
```

**Script requirements:**

1. **Use the API-translated queries from Step 2.3b (approved at Gate 1), NOT the web-interface search strings.** Each database call must use the query in that API's native syntax.

2. **SSL resilience:**
   - Use `certifi` for the default CA bundle.
   - Accept a `--no-ssl-verify` command-line flag that sets `verify=False` on all `requests` calls (with a printed security warning).
   - Detect SSL errors specifically and print a plain-language message directing the researcher to the Network Environment Check resolution steps.

3. **API call patterns — use these exact endpoint structures:**

   **PubMed (NCBI E-utilities):**
   ```python
   # Step 1: Search
   params = {
       "db": "pubmed",
       "term": APPROVED_PUBMED_QUERY,  # PubMed syntax from Gate 1
       "retmax": 10000,
       "retmode": "json",
       "usehistory": "y",
       "tool": "systematic_review",
       "email": RESEARCHER_EMAIL,
   }
   r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params)
   data = r.json()
   count = int(data["esearchresult"]["count"])
   webenv = data["esearchresult"]["webenv"]
   query_key = data["esearchresult"]["querykey"]

   # Step 2: Fetch records in batches using history server
   for start in range(0, count, 10000):
       fetch_params = {
           "db": "pubmed",
           "query_key": query_key,
           "WebEnv": webenv,
           "retstart": start,
           "retmax": 10000,
           "retmode": "xml",
           "rettype": "abstract",
       }
       r = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=fetch_params)
       # Parse XML records
   ```
   Rate limit: 3 requests/second (10/sec with API key). Sleep 0.34s between requests.

   **Europe PMC:**
   ```python
   params = {
       "query": APPROVED_EUROPEPMC_QUERY,  # Europe PMC syntax from Step 2.3b
       "format": "json",
       "resultType": "core",
       "pageSize": 1000,
       "cursorMark": "*",
       "synonym": "true",
   }
   all_results = []
   while True:
       r = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params=params)
       data = r.json()
       results = data.get("resultList", {}).get("result", [])
       all_results.extend(results)
       next_cursor = data.get("nextCursorMark")
       if not next_cursor or next_cursor == params["cursorMark"] or not results:
           break
       params["cursorMark"] = next_cursor
   ```
   Rate limit: 10 requests/second. No authentication required.

   **ClinicalTrials.gov v2:**
   ```python
   params = {
       "query.cond": APPROVED_CONDITION_TERMS,  # From Step 2.3b
       "query.intr": APPROVED_INTERVENTION_TERMS,  # From Step 2.3b
       "format": "json",
       "countTotal": "true",
       "pageSize": 1000,
   }
   # Add optional parameters only if non-empty:
   # "query.outc": APPROVED_OUTCOME_TERMS,
   # "filter.overallStatus": "RECRUITING|COMPLETED|...",
   all_studies = []
   while True:
       r = requests.get("https://clinicaltrials.gov/api/v2/studies", params=params)
       data = r.json()
       studies = data.get("studies", [])
       all_studies.extend(studies)
       next_token = data.get("nextPageToken")
       if not next_token or not studies:
           break
       params["pageToken"] = next_token
   ```
   Rate limit: ~50 requests/minute. No authentication required.

   **OpenAlex:**
   ```python
   params = {
       "search": APPROVED_OPENALEX_SEARCH,  # Boolean search from Step 2.3b
       "filter": APPROVED_OPENALEX_FILTERS,  # e.g., "publication_year:2015-2025,type:article,language:en"
       "per_page": 100,
       "cursor": "*",
       "mailto": RESEARCHER_EMAIL,
   }
   all_works = []
   while True:
       r = requests.get("https://api.openalex.org/works", params=params)
       data = r.json()
       works = data.get("results", [])
       all_works.extend(works)
       next_cursor = data.get("meta", {}).get("next_cursor")
       if not next_cursor or not works:
           break
       params["cursor"] = next_cursor
   ```
   Rate limit: 10 requests/second, 100,000/day. `mailto` required for polite pool.

4. **Retry logic:** All API calls must use 3 retries with exponential backoff (1s, 2s, 4s) for transient HTTP errors (429, 500, 502, 503, 504) and connection timeouts.

5. **Verification step (sanity check):** After each database query, if the main query returns 0 results, run a simplified sanity-check query (a single broad term from the Population PICO component, e.g., just `depression`).
   - If the sanity check returns >0: flag as **LIKELY QUERY SYNTAX ERROR** — the connection works but the full query may have syntax issues. Print the query for inspection.
   - If the sanity check also returns 0: flag as **LIKELY NETWORK/ACCESS ERROR** — the API may be unreachable or blocking requests.
   - Print the diagnostic result clearly for the researcher.

6. **Diagnostic error categorisation:** The script must distinguish and print plain-language messages for:
   - **SSL/certificate errors:** "Your network appears to block or modify HTTPS connections. See the Network Environment Check instructions above."
   - **HTTP 401/403 errors:** "This database requires authentication. Please check your API key / institutional access."
   - **HTTP 429 errors:** "Rate limit exceeded. The script will wait and retry automatically."
   - **HTTP 500+ errors:** "The database server returned an error. The script will retry."
   - **Connection timeouts:** "Could not reach the database. Please check your internet connection."
   - **Query syntax errors (0 results with sanity check >0):** "The search returned 0 results but the database is reachable. The query may have a syntax error. Please review the query above."
   - **Genuine empty results:** "The search returned 0 results and the database is confirmed reachable. This may be a genuinely empty result set for this query."

7. **Output requirements:**
   - Print clear progress messages (e.g., "Searching PubMed... found 347 records").
   - If a database fails, continue with the remaining databases and report which ones succeeded and which failed.
   - Aggregate results into a unified `.bib` and SQLite workspace.
   - Record per-database hit counts.
   - Print a final summary table showing each database, status, and record count.

**For databases requiring manual search (no API / institutional web-only access):**

Provide database-specific, step-by-step instructions for each manual database. These instructions must be precise enough that a researcher unfamiliar with the database can follow them without guessing.

**Cochrane Library:**
> 1. Open your browser and go to https://www.cochranelibrary.com/advanced-search
> 2. Select **"Advanced Search"** from the top navigation.
> 3. In the search box, paste the Cochrane search string (from Step 2.3, using `:ti,ab,kw` field tags).
> 4. Ensure "Search all text" or appropriate field limiters are selected.
> 5. Apply date range filters using the "Date" fields if applicable.
> 6. Click **"Search"**.
> 7. Review the hit count. Click **"Export selected citations"** → choose **RIS** format.
> 8. Save as `{working_directory}/records/cochrane_export.ris`.

**CINAHL (via EBSCO):**
> 1. Go to your institution's library website and navigate to CINAHL (usually under "Databases").
> 2. Log in via SSO if prompted.
> 3. Click **"Advanced Search"** (not "Basic Search").
> 4. Paste the CINAHL/EBSCO search string from Step 2.3 into the search box.
> 5. Select **"Boolean/Phrase"** search mode.
> 6. Apply Limiters: Publication Date, Language, Publication Type as needed (use the checkboxes in the Limiters panel).
> 7. Click **"Search"**.
> 8. Select all results (checkbox at top of list → "Select all results").
> 9. Click **"Export"** → choose **RIS** format → **"Save"**.
> 10. Save as `{working_directory}/records/cinahl_export.ris`.

**Embase (via Ovid or Embase.com):**
> 1. Go to your institution's Embase access (via Ovid or embase.com).
> 2. Log in via SSO.
> 3. Select **"Advanced Search"**.
> 4. Paste the Embase search string from Step 2.3 (using `/exp` for Emtree explosion and `:ti,ab` for title/abstract).
> 5. Apply date and language limits using the interface controls.
> 6. Click **"Search"**.
> 7. Select all results → **"Export"** → choose **RIS** format.
> 8. Save as `{working_directory}/records/embase_export.ris`.

**Web of Science:**
> 1. Go to https://www.webofscience.com/ and log in via your institution.
> 2. Click **"Advanced Search"** (in the top navigation).
> 3. Paste the Web of Science search string from Step 2.3 (using `TS=` for Topic, `TI=` for Title).
> 4. Set the Timespan if applicable.
> 5. Click **"Search"**.
> 6. Select all records → **"Export"** → choose **"Other File Formats"** → select **"RIS"** → **"Full Record"**.
> 7. Note: Web of Science limits exports to 1,000 records at a time. If your results exceed 1,000, export in batches (1–1000, 1001–2000, etc.).
> 8. Save as `{working_directory}/records/wos_export.ris` (or `wos_export_1.ris`, `wos_export_2.ris` for batches).

**PsycINFO (via EBSCO or Ovid):**
> Follow the CINAHL instructions above but navigate to PsycINFO instead of CINAHL. Use the PsycINFO search string from Step 2.3.
> Save as `{working_directory}/records/psycinfo_export.ris`.

After each manual export, confirm receipt:
> "Please let me know when the file is saved and I will integrate it into the unified dataset."

### Logged Outputs
- Per-database: database name, date and time searched (`created_at`), number of records retrieved, search string used (hash cross-referenced to Gate 1), access method (API/manual/SSO), library version used.
- Any failed databases with error details and researcher action taken.

---

## Phase 4: Deterministic Deduplication

### Instructions

**Provide the Python setup instructions (from Phase 3) if not already completed. List the specific `pip install` command for this script's dependencies:**
```
pip install bib-dedupe
```

1. **Pause AI operations.** Provide the researcher with a Python script using `BibDedupe` for deterministic deduplication. (Note: `ASReview` via `asreview-datatools` can also perform deduplication using `difflib.SequenceMatcher`, but `BibDedupe` is recommended for its zero-false-positives design goal.)
2. Before the script, explain in plain language:
   > "This script will find and remove duplicate records (the same paper appearing in multiple database results). It will automatically remove exact matches and ask you to confirm any uncertain matches."
3. The script must:
   - Merge "confident duplicates" automatically (exact DOI match, exact title+author+year match).
   - Present "suspected duplicates" (fuzzy title/author matches above a configurable similarity threshold) to the researcher via CLI for manual confirmation.
   - Print clear messages: "Found 42 exact duplicates (removed automatically). Found 7 suspected duplicates — please review each one below."
   - Output a deduplication report.
4. Log exact numbers to the audit log (with `created_at` timestamps):
   - Records before deduplication.
   - Confident duplicates removed (auto).
   - Suspected duplicates presented.
   - Suspected duplicates confirmed as duplicates by researcher.
   - Suspected duplicates retained by researcher.
   - Records after deduplication.

These counts feed the PRISMA flow diagram.

---

## Phase 5: Title-Abstract Screening (AI-Assisted)

### Screening Prompt Template

For each record, use the following structured prompt. All calls use `temperature=0` and the researcher-set seed. **Hash every LLM response and log the hash in `output_hash`.**

```
ROLE: You are a systematic review screening assistant. You produce
structured recommendations. You do NOT make final decisions — all
decisions are confirmed by the human researcher.

REVIEW PROTOCOL:
- Population: {population}
- Intervention: {intervention}
- Comparator: {comparator}
- Outcome: {outcome}
- Accepted study designs: {designs} [or "N/A — no study design restrictions"]
- Date range: {date_range} [or "N/A — no date restrictions"]
- Language: {languages} [or "N/A — no language restrictions"]

{CALIBRATION_EXAMPLES_BLOCK — empty for Batch 1; populated by the
Active Learning Protocol (see below) from Batch 2 onward}

RECORD ID: {record_id}
Title: {title}
Abstract: {abstract}

INSTRUCTIONS:
Evaluate this record against EACH criterion below. For each, quote the
specific sentence(s) from the abstract that support your judgment. If
no relevant information exists, state "No information in abstract."

1. POPULATION
   - Criterion: {population}
   - Evidence from abstract: [exact quote or "No information in abstract"]
   - Assessment: MET / NOT MET / UNCLEAR

2. INTERVENTION
   - Criterion: {intervention}
   - Evidence from abstract: [exact quote or "No information in abstract"]
   - Assessment: MET / NOT MET / UNCLEAR

3. COMPARATOR
   - Criterion: {comparator}
   - Evidence from abstract: [exact quote or "No information in abstract"]
   - Assessment: MET / NOT MET / UNCLEAR

4. OUTCOME
   - Criterion: {outcome}
   - Evidence from abstract: [exact quote or "No information in abstract"]
   - Assessment: MET / NOT MET / UNCLEAR

5. STUDY DESIGN
   - Criterion: {designs} [or "N/A — no restriction; skip this criterion"]
   - Evidence from abstract: [exact quote or "No information in abstract"]
   - Assessment: MET / NOT MET / UNCLEAR / NOT APPLICABLE

6. LANGUAGE
   - Criterion: {languages} [or "N/A — no restriction; skip this criterion"]
   - Evidence from record metadata: [language field or inferred from text]
   - Assessment: MET / NOT MET / NOT APPLICABLE

7. DATE RANGE
   - Criterion: {date_range} [or "N/A — no restriction; skip this criterion"]
   - Evidence from record metadata: [publication year]
   - Assessment: MET / NOT MET / NOT APPLICABLE

DECISION RULE:
- ALL applicable criteria MET → Recommend INCLUDE
- ANY criterion NOT MET → Recommend EXCLUDE
  Primary exclusion reason (select one):
  [ Wrong Population | Wrong Intervention | Wrong Comparator |
    Wrong Outcome | Wrong Study Design | Wrong Publication Type |
    Wrong Date Range | Wrong Language | Duplicate Not Caught ]
- ANY criterion UNCLEAR and none NOT MET → Recommend UNCERTAIN
  (requires closer human attention)

RECOMMENDATION: [INCLUDE / EXCLUDE / UNCERTAIN]
EXCLUSION REASON (if applicable): [category]
CONFIDENCE: [High / Medium / Low]
REASONING SUMMARY: [one-sentence plain-language summary]
```

### Screening Performance Monitoring

#### Automatic Batch Consistency Checks (every 50 records)

After every batch of 50 records screened (or the total number of retrieved records, whichever is smaller), the system must automatically compute and log:

**Drift Detection:**
- Exclusion reason distribution for the batch vs. cumulative distribution.
- If any category deviates by >15 percentage points → `DRIFT_ALERT`.

**Confidence Distribution:**
- If Low confidence exceeds 30% of the batch → `LOW_CONFIDENCE_ALERT`.

**Uncertain Rate:**
- If UNCERTAIN exceeds 20% of the batch → `UNCERTAIN_SPIKE_ALERT`.

**Inclusion Rate:**
- If inclusion rate shifts by >10 percentage points between consecutive batches → `INCLUSION_DRIFT_ALERT`.

**On any alert:**
1. Log the alert with full metrics to `audit_log.json` (with `created_at`).
2. **Immediately notify the researcher.** Present the alert type, specific metrics, batch range, and plain-language explanation.
3. Ask the researcher whether to: (a) continue, (b) re-screen the batch, or (c) pause and adjust the prompt.
4. Log the researcher's decision.

#### Human Ground-Truth Validation (20% per batch)

**For each batch of 50 records (or total records, whichever is smaller), the system must randomly select 20% of records (i.e., 10 records per batch of 50) for independent human ground-truth screening.**

This is separate from the 100% audit in Gate 2. The purpose is to compute screening performance metrics using the human's independent judgment as ground truth.

**Process:**

1. Randomly select 20% of the batch. Present these records to the researcher **without showing the AI's recommendation.**

2. After the researcher completes all ground-truth decisions for the batch, compare AI recommendations to human decisions and compute metrics **overall and broken down by each exclusion reason**: True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN), Precision, Sensitivity (Recall), Specificity, F1 Score, Accuracy.

3. Present the metrics to the researcher in a clear summary table.

4. **Performance threshold alerts:**
   - If overall Sensitivity drops below 0.90 → `SENSITIVITY_ALERT`: "The AI is missing studies that you would include. This is the most dangerous error in a systematic review."
   - If overall Precision drops below 0.70 → `PRECISION_ALERT`: "The AI is including studies you would exclude. This increases your workload but does not compromise review validity."
   - If F1 drops below 0.75 → `F1_ALERT`: "Overall screening performance is below acceptable thresholds."

5. Log all metrics, ground-truth decisions, and alerts to `audit_log.json` with `created_at` timestamps.

#### Active Learning — Prompt Calibration Protocol

**Purpose:** As the human audits the AI's screening decisions, systematic error patterns emerge — the AI may consistently misjudge certain study types, populations, or interventions. This protocol uses the human's corrections as few-shot calibration examples to improve the screening prompt for subsequent batches. This is in-context learning (not fine-tuning): the model itself does not change, but the prompt is enriched with real examples from this review, making the AI's recommendations progressively closer to the researcher's ground truth.

**When it triggers:** After each completed batch cycle — specifically, after (a) the AI screens a batch of 50 records, (b) the 20% ground-truth validation is computed, AND (c) the 100% human audit of the batch is complete. The protocol runs before the next batch is screened. **It does not apply to Batch 1** (no correction data exists yet).

**Step 1: Extract override patterns**

After the human audit of batch N, automatically analyse all human overrides (AGREE vs OVERRIDE) across the batch:

1. Collect all records where the human overrode the AI's recommendation.
2. Classify each override into one of:
   - **False Negative (FN):** AI recommended EXCLUDE → Human decided INCLUDE. *These are the most dangerous errors in a systematic review — missed studies.*
   - **False Positive (FP):** AI recommended INCLUDE → Human decided EXCLUDE. *Less dangerous but increases screening workload.*
   - **Uncertainty Error:** AI recommended UNCERTAIN → Human decided INCLUDE or EXCLUDE with high confidence (clear case the AI should have resolved).
3. For each override, identify:
   - Which PICO criterion the AI misjudged (Population, Intervention, Comparator, Outcome, Study Design, Language, Date).
   - The AI's stated evidence and reasoning.
   - The human's override reason.
   - The abstract passage (or lack thereof) that the AI misinterpreted.

**Step 2: Select calibration examples**

From the cumulative pool of overrides across all completed batches (not just the latest), select up to **5 calibration examples** using these priority rules:

1. **False negatives first.** Missed includes are the most dangerous error. Select up to 3 FN examples.
2. **Recurring patterns over isolated errors.** If the AI makes the same type of mistake across multiple records (e.g., consistently misclassifying a specific study design, or consistently missing a population subgroup), prioritise an example that represents the pattern.
3. **Diversity across criteria.** Spread examples across different PICO criteria to avoid over-correcting on one axis.
4. **Borderline cases over obvious errors.** Select examples where the AI's reasoning was partially correct but the final judgment was wrong — these are the most instructive for calibration.
5. **Freshness.** If two examples teach the same lesson, prefer the one from the most recent batch.
6. **Replace stale examples.** If the AI stops making a particular type of error (as measured in subsequent batches), remove the calibration example that addressed it to avoid prompt bloat.

**Step 3: Format calibration examples**

Generate a `CALIBRATION_EXAMPLES_BLOCK` using this exact format:

```
CALIBRATION EXAMPLES (from human-audited decisions in this review):
These examples show cases where the screening recommendation was
overridden by the human reviewer. Study them carefully to calibrate
your assessments for similar cases.

EXAMPLE 1 [False Negative — AI missed an includable study]:
  Record ID: {record_id}
  Title: {title}
  Key abstract passage: "{relevant_excerpt}"
  AI recommendation: EXCLUDE — {exclusion_reason}
  AI evidence for {criterion}: "{AI_quoted_passage}"
  AI assessment: NOT MET
  HUMAN DECISION: INCLUDE (Override)
  Human reasoning: "{override_reason}"
  LESSON: {one-sentence corrective guidance, e.g., "Studies that
  describe [X] in the context of [Y] should be assessed as meeting
  the Population criterion even when [Z] is not explicitly stated."}

EXAMPLE 2 [False Positive — AI over-included]:
  ...

[up to 5 examples]
```

**Step 4: Present for researcher approval**

**MANDATORY.** Present the proposed calibration examples to the researcher before adding them to the screening prompt:

> "Based on your corrections in Batch {N}, I have identified {count} recurring error patterns in my screening. I propose adding the following calibration examples to my screening prompt for the next batch. These examples will help me avoid similar mistakes.
>
> [Show each example]
>
> Please review each example:
> - **Approve** to add it to the prompt.
> - **Modify** the lesson text if my characterisation of the error is inaccurate.
> - **Reject** if the example is not informative or could cause over-correction.
>
> You may also suggest additional examples from records I have not flagged."

Log: the proposed examples, the researcher's response (approve/modify/reject for each), the final approved set, and `created_at` timestamp.

**Step 5: Update the screening prompt**

Insert the approved `CALIBRATION_EXAMPLES_BLOCK` into the screening prompt template (in the designated placeholder after the REVIEW PROTOCOL block). The block is cumulative — it includes all currently active calibration examples, not just those from the latest batch.

**Hash the updated prompt and log it as a new prompt version in the audit log.** The `output_hash` for subsequent screening calls is computed against the updated prompt.

**Step 6: Measure calibration effectiveness**

After each batch screened with the updated prompt, compute:

1. **Per-lesson hit rate:** For each calibration example's lesson, count how many records in the new batch matched the pattern AND were correctly assessed. If a lesson has zero matches across two consecutive batches, flag it as a candidate for removal.
2. **Override rate comparison:** Compare the human override rate for the current batch against the previous batch. Log the delta.
3. **Per-criterion improvement:** Compare precision and sensitivity for each PICO criterion before and after the calibration.
4. **Cumulative accuracy trend:** Plot (or table) the overall accuracy, sensitivity, and F1 across all batches to date, showing the trajectory.

Present the effectiveness summary to the researcher:
> "**Calibration effectiveness after Batch {N}:**
> - Override rate: {previous}% → {current}% (Δ {delta}%)
> - Sensitivity: {previous} → {current}
> - Precision: {previous} → {current}
> - F1: {previous} → {current}
> - Lessons applied: {count_applied} / {count_total}
> - Lessons with zero matches (candidates for removal): {list}"

If the override rate **increases** after a calibration update, raise a `CALIBRATION_REGRESSION_ALERT` and ask the researcher whether to (a) keep the current calibration, (b) revert to the previous prompt version, or (c) modify specific examples.

**Step 7: Log every calibration turn**

Every calibration cycle must produce a full audit log entry that captures three mandatory dimensions:

1. **Time** — when the calibration was triggered (`created_at`) and when the researcher reviewed it (`human_review.reviewed_at`).
2. **Milestone** — where in the workflow this calibration was triggered (`trigger` block): which phase, which gate, which batch or study, and cumulative progress.
3. **Summary of main changes** — a human-readable narrative (`change_summary`) describing what examples were added, modified, retired, or rejected, and the net effect on prompt composition and screening accuracy.

Schema for each calibration log entry in `audit_log.json`:
```json
{
  "entry_id": "UUID-v4",
  "created_at": "ISO-8601 — timestamp of this calibration cycle",
  "phase": "5",
  "action": "active_learning_calibration",
  "actor": "AI",
  "trigger": {
    "milestone": "string — human-readable milestone that triggered this cycle, e.g., 'After human audit of title-abstract screening Batch 3 (records 101–150)'",
    "phase": "5 | 7 | 8",
    "gate": "string — which gate's audit produced the correction data, e.g., 'Gate 2' or 'Gate 4'",
    "batch_number": "integer — batch number that triggered this cycle",
    "batch_range": "string — record range, e.g., 'records 101–150'",
    "records_audited_this_batch": "integer",
    "cumulative_records_audited": "integer — total records audited across all batches so far"
  },
  "calibration_cycle": {
    "cycle_number": "integer — sequential calibration cycle count (1, 2, 3, ...)",
    "overrides_analysed": "integer — total overrides in this batch",
    "false_negatives": "integer",
    "false_positives": "integer",
    "uncertainty_errors": "integer",
    "examples_proposed": "integer",
    "examples_approved": "integer",
    "examples_modified": "integer",
    "examples_rejected": "integer",
    "total_active_examples": "integer — total examples now in prompt after this cycle",
    "examples_added": "integer — new examples added this cycle",
    "examples_retired": "integer — examples removed this cycle",
    "examples_replaced": "integer — examples swapped (retired + replaced) this cycle",
    "prompt_version_hash": "SHA-256 of the updated prompt",
    "previous_prompt_version_hash": "SHA-256 of the previous prompt"
  },
  "change_summary": "string — human-readable narrative of what changed this cycle, e.g., 'Added 2 calibration examples: (1) FN correction for Wrong Population — studies describing comorbid anxiety with primary depression now assessed as meeting Population criterion; (2) FP correction for Wrong Intervention — studies comparing two active pharmacotherapies without a CBT arm now correctly excluded. Retired 1 stale example (Wrong Study Design) — no matches in last 2 batches. Net: 3→4 active examples. Override rate improved from 18% to 11%.'",
  "calibration_examples": [
    {
      "example_id": "UUID-v4",
      "record_id": "string — the record used as the example",
      "error_type": "FN | FP | UNCERTAINTY",
      "criterion_misjudged": "string — PICO criterion",
      "lesson": "string — corrective guidance",
      "status": "ADDED | ACTIVE | MODIFIED | RETIRED | REJECTED",
      "change_this_cycle": "string — what happened to this example in this cycle: 'newly added' | 'lesson modified' | 'retired (zero matches for 2 batches)' | 'replaced by more informative example' | 'no change' | 'rejected by researcher'",
      "added_at_batch": "integer",
      "retired_at_batch": "integer | null",
      "hit_count_last_batch": "integer — records matching this lesson's pattern in the most recent batch",
      "correctly_assessed_after_calibration": "integer — of those matches, how many were correctly assessed"
    }
  ],
  "effectiveness_metrics": {
    "override_rate_before": "float",
    "override_rate_after": "float",
    "override_rate_delta": "float — negative = improvement",
    "sensitivity_before": "float",
    "sensitivity_after": "float",
    "precision_before": "float",
    "precision_after": "float",
    "f1_before": "float",
    "f1_after": "float",
    "per_criterion_deltas": {
      "population": {"sensitivity_delta": "float", "precision_delta": "float"},
      "intervention": {"sensitivity_delta": "float", "precision_delta": "float"},
      "comparator": {"sensitivity_delta": "float", "precision_delta": "float"},
      "outcome": {"sensitivity_delta": "float", "precision_delta": "float"},
      "study_design": {"sensitivity_delta": "float", "precision_delta": "float"}
    }
  },
  "human_review": {
    "reviewed": true,
    "reviewer_id": "string",
    "agreed_with_all_proposals": "boolean",
    "modifications_made": "integer — count of examples where the researcher modified the lesson",
    "rejections": "integer",
    "researcher_added_examples": "integer — examples suggested by the researcher that the AI had not flagged",
    "reviewed_at": "ISO-8601"
  }
}
```

**Reproducibility note:** Adding calibration examples changes the prompt, which changes the deterministic output for records screened under the new prompt. This is by design — the prompt improvement is measured and documented. The audit log records which prompt version was used for each screening call (via `prompt_version_hash`), so any output can be traced to its exact prompt. A researcher using the same prompt version + seed will get identical results.

**Guardrail: Maximum prompt growth.** The calibration block must not exceed 5 examples. If a 6th example is warranted, it must replace the least informative existing example (lowest hit rate over the last two batches). This prevents unbounded prompt growth that could degrade model performance by consuming context window space needed for the abstract itself.

### ── GATE 2: 100% Human Audit of Title-Abstract Screening ──

**MANDATORY. ALL decisions require human confirmation.**

After the AI has screened all records, present every record to the researcher (Reviewer A) with the AI's recommendation, reasoning, and evidence:

```
RECORD: {record_id} — {title}
AI RECOMMENDATION: [INCLUDE / EXCLUDE / UNCERTAIN]
AI EXCLUSION REASON: [category or N/A]
AI CONFIDENCE: [High / Medium / Low]
AI REASONING: [one-sentence summary]

YOUR DECISION: [ ] AGREE  [ ] OVERRIDE → [INCLUDE / EXCLUDE]
OVERRIDE REASON (if applicable): _______________
```

**Workflow:**
1. Present records in batches (batch size configurable by researcher; default 25).
2. Prioritise UNCERTAIN records first.
3. Then EXCLUDE recommendations (Low confidence first).
4. Then INCLUDE recommendations (Low confidence first).
5. For each record, the researcher must select AGREE or OVERRIDE.
6. If OVERRIDE, the researcher must provide a reason.
7. Log every decision with `created_at` timestamp.

**Do not proceed to Phase 5b until Gate 2 is complete and logged.**

---

## Phase 5b: Independent Dual Screening & Conflict Resolution

### Rationale

Cochrane Handbook v6.5 (Chapter 4) requires independent duplicate screening to minimise selection bias. A single reviewer (even with AI assistance) does not meet this standard. Phase 5b implements a second independent screening pass.

### Instructions

1. **Reviewer B** must screen the same records independently. Reviewer B can be:
   - A second human reviewer (preferred for Cochrane compliance).
   - A second blinded AI pass with a different prompt variant or different seed (acceptable for non-Cochrane reviews, but must be documented as a limitation).

2. **Reviewer B does not see Reviewer A's decisions.** Present records to Reviewer B in the same format as the ground-truth validation (no AI recommendation shown if Reviewer B is human; if Reviewer B is a second AI pass, use a different seed).

3. **Conflict identification:** After both reviewers have completed screening, identify all records where Reviewer A and Reviewer B disagree.

4. **Conflict resolution:** Present each conflict to a third-party adjudicator (the principal investigator, or a designated senior reviewer):
   > "**Conflict — Record {record_id}:**
   > Title: {title}
   > Reviewer A decision: [INCLUDE / EXCLUDE] — Reason: [...]
   > Reviewer B decision: [INCLUDE / EXCLUDE] — Reason: [...]
   >
   > Please adjudicate: [INCLUDE / EXCLUDE]
   > Reason: _______________"

5. **Compute inter-rater reliability:**
   - **Cohen's Kappa** (for two reviewers on binary include/exclude).
   - **Percentage agreement.**
   - Report and log both metrics.
   - If Kappa < 0.60, flag as `LOW_AGREEMENT_ALERT` and recommend reviewing the eligibility criteria for ambiguity.

6. Log: all Reviewer B decisions, all conflicts, all adjudication outcomes, Kappa, percentage agreement, `created_at` timestamps.

### ── GATE 2b: Conflict Resolution Complete ──

**MANDATORY.** All conflicts must be resolved before proceeding. Log the final consensus decision for every record.

**Do not proceed to Phase 6 until Gate 2b is complete.**

---

## Phase 6: Full-Text Retrieval

### Researcher-Set Directory

Before retrieval, confirm the full-text directory with the researcher:
> "Full-text PDFs will be saved to: `{full_text_directory}`. Is this correct, or would you like to change it?"

Log the confirmed directory path.

### Python Environment & Instructions

**Provide the same beginner-friendly Python setup instructions from Phase 3 if the researcher has not yet set up their environment.** If the environment is already set up, provide only:
> "With your virtual environment active, install the additional libraries:
> ```
> pip install PyPaperRetriever PyMuPDF pytesseract
> ```
> Then save and run the script as before."

### Retrieval Script

1. Provide a Python script using `PyPaperRetriever` to automate discovery and download of open-access PDFs via Unpaywall, PubMed Central, and Crossref.
2. Save PDFs to the researcher-set directory, named by record ID.
3. The script must print clear progress and handle errors gracefully.
4. For records where full text is not freely available:
   - Log as "full text not retrieved — requires institutional access or ILL."
   - Present the list to the researcher with instructions for manual retrieval via SSO or Interlibrary Loan.
5. Specify PDF text extraction for downstream screening:
   - Use `PyMuPDF` (fitz) for text extraction.
   - If text extraction yields <100 characters per page (scanned/image PDF), flag for OCR using `pytesseract`.
   - Log extraction method per document.
6. Log: records retrieved (auto), records requiring manual retrieval, extraction method per document, all with `created_at` timestamps.

---

## Phase 7: Full-Text Screening

### Instructions

1. Use the same structured screening prompt as Phase 5, adapted for full-text input. Include all criteria with the same N/A handling.
2. Apply the same `temperature=0` and researcher-set seed. Hash all responses.
3. Apply the same performance monitoring system as Phase 5 (drift detection, 20% ground-truth validation, full metrics).
4. Apply the same **Active Learning — Prompt Calibration Protocol** as Phase 5. Start with a fresh calibration (no carry-over from title-abstract screening), since full-text screening involves different evidence and different error patterns. Calibration examples from full-text overrides replace any title-abstract examples.
5. Apply the same dual screening protocol as Phase 5b (Reviewer A + Reviewer B + conflict resolution + Cohen's Kappa).

### ── GATE 3: 100% Human Audit + Dual Screening Conflict Resolution ──

**Identical protocol to Gates 2 + 2b combined.** Present every full-text screening decision for human audit, then perform independent dual screening and resolve all conflicts.

**Additional requirement:** For each study excluded at full-text stage, the researcher must confirm the exclusion reason. These populate the "Excluded studies with reasons" table required by PRISMA Item 17.

**Do not proceed to Phase 8 until Gate 3 is complete and logged.**

---

## Phase 8: Risk of Bias Assessment

### Framework Ingestion

1. **Ask the researcher to provide a link or document for their chosen risk of bias framework.** Present the following verified options as examples, but accept any framework:

   **For randomised controlled trials:**
   - RoB 2 (Cochrane risk of bias tool) — https://methods.cochrane.org/bias/resources/rob-2-revised-cochrane-risk-bias-tool-randomized-trials

   **For non-randomised studies:**
   - ROBINS-I — https://methods.cochrane.org/robins-i
   - Newcastle-Ottawa Scale — search "Newcastle-Ottawa Scale" at https://www.ohri.ca or access via the Ottawa Hospital Research Institute methods centre

   **For diagnostic accuracy studies:**
   - QUADAS-2 — https://www.bristol.ac.uk/population-health-sciences/projects/quadas/ (note: QUADAS-3 was released February 2026; check whether QUADAS-2 or QUADAS-3 is appropriate for your review)

   **For qualitative studies:**
   - CASP Qualitative Checklist — https://casp-uk.net/casp-tools-checklists/qualitative-studies-checklist/

   **For cohort studies:**
   - CASP Cohort Study Checklist — https://casp-uk.net/casp-tools-checklists/cohort-study-checklist/

   **For case-control studies:**
   - CASP Case Control Study Checklist — https://casp-uk.net/casp-tools-checklists/case-control-study-checklist/

   **For systematic reviews:**
   - CASP Systematic Review Checklist — https://casp-uk.net/casp-tools-checklists/systematic-review-checklist/

   **For clinical trials:**
   - CASP Randomised Controlled Trial Checklist — https://casp-uk.net/casp-tools-checklists/randomised-controlled-trial-rct-checklist/

   **Other frameworks:**
   - JBI Critical Appraisal Tools — https://jbi.global/critical-appraisal-tools
   - Any custom or domain-specific framework

   **Note:** URLs may change over time. If a link does not work, search for the framework by name on the organisation's website. Always verify you are using the current version of the tool.

2. Fetch the provided link or read the provided document.
3. Parse the framework into a structured assessment template.
4. Present the parsed template to the researcher for confirmation.
5. Log the framework name, source link, parsed structure, and researcher confirmation with `created_at`.

### Assessment Execution

For each included study (after Gate 3), apply the parsed RoB framework using structured prompting at `temperature=0` with the researcher-set seed. Hash all responses.

```
ROLE: You are assisting with risk of bias assessment. You produce
structured recommendations based on the researcher's chosen framework.
ALL judgments must be confirmed by the human researcher.

FRAMEWORK: {framework_name}
STUDY: {record_id} — {title}
STUDY DESIGN: {design}
FULL TEXT EXCERPT: {relevant_methods_and_results_sections}

For each domain below, answer the signalling questions, then provide
a domain-level judgment. Quote the specific passage from the study
that supports each answer.

DOMAIN 1: {domain_name}
  Signalling Question 1.1: {question}
    Answer: [Yes / Probably Yes / No / Probably No / No Information]
    Evidence: [exact quote from study text]
  Signalling Question 1.2: {question}
    ...
  DOMAIN JUDGMENT: {judgment_options}
  REASONING: [one sentence]

[...repeat for all domains...]

OVERALL RISK OF BIAS: {judgment_options}
DIRECTION OF BIAS (if assessable): [Favours intervention / Favours
comparator / Towards null / Away from null / Unpredictable]
```

### Active Learning — RoB Calibration

**The same Active Learning Protocol from Phase 5 applies to risk of bias assessment, adapted for domain-level judgments rather than include/exclude decisions.**

Because the number of studies at this stage is typically small (tens, not hundreds), the calibration operates **per-study rather than per-batch**:

1. **After the researcher audits each study's RoB assessment (at Gate 4)**, if the researcher overrides any domain judgment, extract a calibration example:
   - The domain name and signalling questions involved.
   - The AI's original judgment and evidence.
   - The researcher's corrected judgment and reasoning.
   - A one-sentence lesson for that domain (e.g., "When a study reports allocation concealment as 'sealed envelopes' without specifying opaque or sequentially numbered, assess Domain 1 as 'Some concerns' rather than 'Low risk'").

2. **Accumulate up to 3 RoB calibration examples** across all audited studies. Prioritise recurring patterns (the same domain misjudged in the same direction across multiple studies).

3. **Insert the calibration examples into the RoB prompt** (after the FRAMEWORK block) before assessing the next study. Use this format:

```
RoB CALIBRATION EXAMPLES (from researcher-audited assessments in this review):

EXAMPLE 1:
  Study: {record_id} — {title}
  Domain: {domain_name}
  AI judgment: {judgment} — Evidence: "{passage}"
  Researcher override: {corrected_judgment}
  Reason: "{override_reason}"
  LESSON: {corrective guidance}
```

4. **Present each calibration update to the researcher for approval** before applying it to subsequent studies. The researcher may modify the lesson or reject the example.

5. **Log each calibration cycle** to the audit log using the same enhanced schema as Phase 5, with these adaptations:
   - `phase`: `"8"`
   - `action`: `"active_learning_calibration_rob"`
   - `trigger.milestone`: Describe the specific study that triggered the calibration, e.g., `"After researcher audit of RoB assessment for Study 7 (Record ID: PMD_38291045) — 3rd study assessed, 2nd with domain overrides"`
   - `trigger.gate`: `"Gate 4"`
   - `trigger.batch_number`: Replace with `"study_number"` — the sequential study count (e.g., 3 = third study assessed)
   - `calibration_cycle.cycle_number`: Sequential RoB calibration cycle count
   - `change_summary`: Human-readable narrative of domain-level changes, e.g., `"Added 1 RoB calibration example: Domain 2 (Deviations from intended interventions) — AI assessed 'Low risk' but researcher overrode to 'Some concerns' because unblinded outcome assessors could influence behavioural interventions. 1 active RoB example total."`
   - `calibration_examples[].criterion_misjudged`: Replace with the RoB domain name (e.g., `"Domain 1: Randomisation process"`)

**Guardrail:** Maximum 3 RoB calibration examples to avoid consuming context space needed for the study's full text.

### ── GATE 4: 100% Human Audit of Risk of Bias ──

**MANDATORY. Every domain judgment for every study must be confirmed by the researcher.**

1. The researcher must confirm or override each domain judgment.
2. The researcher must confirm or override the overall RoB judgment.
3. Log every decision with `created_at` timestamp.

**Do not proceed to Phase 9 until Gate 4 is complete and logged.**

---

## Phase 9: PRISMA Flow Diagram Generation

### Automated Generation

After all gates are complete, automatically generate the PRISMA 2020 flow diagram by reading counts from `audit_log.json`. Include all counts from Identification through Inclusion, with exclusion reason breakdowns at each stage.

**Diagram output:**

Generate the PRISMA flow diagram as:
1. An SVG file (`{working_directory}/prisma/prisma_flow_diagram.svg`).
2. An editable source file (`{working_directory}/prisma/prisma_flow_diagram_source.json`).
3. A Markdown representation (`{working_directory}/prisma/prisma_flow_diagram.md`).

### ── GATE 5: Researcher Finalises Diagram ──

**MANDATORY.** Present the auto-generated PRISMA diagram to the researcher.

1. The researcher reviews all counts for accuracy.
2. The researcher may add, modify, or correct any box, count, or annotation.
3. Log original and revised values with reason for revision.
4. Re-render from confirmed values.
5. Log final diagram data, researcher approval, and `created_at` timestamp.

**The researcher has final authority over the PRISMA diagram.**

---

## Phase 10: Export & Reporting

### Instructions

Generate a final export package at `{working_directory}/exports/`:

```
exports/
├── protocol.md
├── ai_transparency_statement.md
├── search_strategies/
│   └── [per-database].txt
├── screening_results/
│   ├── title_abstract_screening.csv
│   ├── full_text_screening.csv
│   └── dual_screening_conflicts.csv
├── ground_truth_validation/
│   ├── title_abstract_ground_truth.csv
│   ├── full_text_ground_truth.csv
│   └── performance_metrics_by_batch.csv
├── calibration/
│   ├── title_abstract_calibration_history.csv
│   ├── full_text_calibration_history.csv
│   ├── rob_calibration_history.csv
│   └── calibration_effectiveness_report.md
├── inter_rater_reliability/
│   ├── cohens_kappa_title_abstract.md
│   └── cohens_kappa_full_text.md
├── risk_of_bias/
│   ├── rob_assessments.csv
│   └── rob_summary_table.md
├── prisma/
│   ├── prisma_flow_diagram.svg
│   ├── prisma_flow_diagram_source.json
│   └── prisma_flow_diagram.md
├── included_studies.bib
├── excluded_studies_with_reasons.csv
├── performance_monitoring_report.md
├── audit_log.json
└── audit_chain_verification.py
```

**`ai_transparency_statement.md`** — the AI Transparency Block formatted for inclusion in a manuscript or appendix.

**`performance_monitoring_report.md`** summarises: all alerts, drift events, AI-human agreement rates, ground-truth performance metrics, inter-rater reliability (Cohen's Kappa), override patterns, calibration effectiveness (per-batch accuracy trends, lesson hit rates, calibration regression events), and calibration warnings.

**`audit_chain_verification.py`** — provide with full beginner-friendly run instructions.

---

## Design Principles

1. **The human decides; the AI recommends.** Every inclusion, exclusion, and risk-of-bias judgment is a recommendation until the researcher confirms it.

2. **Independent dual screening.** Two independent reviewers (human and/or AI) screen all records, with conflict resolution by a third-party adjudicator. This meets the Cochrane Handbook v6.5 requirement for independent duplicate screening.

3. **Reproducibility through determinism.** Temperature=0, researcher-set seed, versioned prompts, response hashing, and SHA-256 audit chaining ensure exact replication.

4. **Transparency through structured logging and AI disclosure.** Every decision is logged with structured rationales (not raw CoT). The AI Transparency Block documents the AI's role, limitations, and configuration per PRISMA-trAIce and RAISE guidance.

5. **Performance monitoring with active notification.** Drift detection, ground-truth validation with full metrics, threshold alerts, and active learning calibration surface and correct problems in real time.

6. **PRISMA compliance by construction.** The flow diagram is generated from actual audit data, then verified and finalised by the researcher.

7. **Accessible to non-coders.** Every script comes with step-by-step setup instructions. No prior Python experience is assumed.

8. **Plan first, then act.** For any non-standard database or novel procedure, the skill creates a plan, presents it for approval, and only executes after confirmation.

9. **No fabricated references.** Every guideline, framework, and publication cited in this skill has been individually verified. URLs are provided where available but may change — always verify by searching for the framework by name.

10. **Active learning from human corrections.** The AI's screening and assessment prompts are progressively calibrated using real override examples from the researcher's audit. Each calibration is logged, version-hashed, researcher-approved, and measured for effectiveness. The model itself does not change — only the prompt is enriched with few-shot examples, preserving determinism for any given prompt version + seed.
