---
name: systematic-review-coordinator
metadata:
  version: "5.0"
description: >
  Orchestrates a rigorous, auditable, and PRISMA-compliant systematic
  literature review workflow — for NEW reviews and for UPDATES of
  existing reviews — with full human oversight and independent dual
  screening. Automates search construction, retrieval, deduplication
  (including dedup against a prior review corpus), and screening at
  scale (stable record IDs, batching, checkpoint/resume), with a
  mandatory pilot→calibrate→scale validation protocol before any full
  screen, while enforcing 100% human audit of all inclusion/exclusion
  decisions and risk of bias assessments. Includes AI transparency
  reporting and generates a researcher-editable PRISMA flow diagram
  (new-review and update layouts). Designed to be used by researchers
  with no prior coding experience. Activates when a user requests a
  systematic review, a review update, or a literature search based on
  a research question.
---

# Systematic Review Coordinator — Optimised Skill (v5.0)

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

**Note on v5 operational additions:** The capabilities added in v5 — Update-Review Mode, Screening at Scale (stable IDs, batching, checkpoint/resume), the Pilot → Calibrate → Scale validation protocol, the eligibility-rules registry, κ interpretation guidance (including % agreement and PABAK), risk-based audit, environment fallbacks, and the PRISMA update layout — are **internal design guidance** derived from direct operational experience running this skill on a live PROSPERO-track review update. They introduce **no new external citations**. Where they touch reporting or methodology, they are grounded in the standards already listed above: PRISMA 2020 (flow-diagram bookkeeping, including for updated reviews), PRISMA-S (search reporting, including date limits and re-run searches), the Cochrane Handbook v6.5 (independent duplicate screening, pilot testing of eligibility criteria and screening forms), and PRISMA-trAIce/RAISE (AI transparency). PABAK (prevalence-adjusted bias-adjusted kappa) is used here as a well-established descriptive agreement statistic; it is computed and reported, not cited as a new standard.

---

## Boundaries and Guardrails

- **DO NOT** synthesise scientific conclusions, perform unsupervised meta-analytical mathematics, or write the interpretive discussion.
- **DO NOT** use zero-shot prompting for abstract screening. All screening must use structured criterion-by-criterion evaluation with explicit evidence grounding.
- **DO NOT** use the AI model to probabilistically deduplicate records. Deduplication must be deterministic.
- **DO NOT** finalise any inclusion or exclusion decision without explicit human confirmation. The AI produces recommendations; the human decides.
- **DO NOT** use creative or probabilistic inference. All LLM calls must use `temperature=0` to minimise output variability and enforce strict adherence to the provided research question and criteria. (See the **Reproducibility Statement** for what `temperature=0` does and does not guarantee for agentic screening — do not describe outputs as "identical" or "exactly replicable" at the reasoning level.)
- **DO NOT** proceed past any human-approval gate without logged confirmation.
- **DO NOT** begin the full title-abstract screen before the calibration-pilot gate (Gate 2a) has been passed and the eligibility criteria locked.
- **DO NOT** substitute free/public APIs (PubMed E-utilities, Europe PMC, OpenAlex, etc.) for the institutional databases named in the protocol (e.g., Ovid MEDLINE/Embase, EBSCO CINAHL/PsycINFO, Scopus, ProQuest, Web of Science). Substitution silently changes the evidence base. It is permitted only as an explicitly approved, logged protocol deviation.
- **DO NOT** use a deterministic keyword classifier, embedding filter, or any other non-reading triage mechanism as the authoritative screen. Such tools may only be used as clearly labelled high-recall triage/stratification aids; authoritative screening recommendations come from genuine per-record reading.
- **DO NOT** conduct risk of bias assessment without the researcher providing their chosen framework.
- **DO NOT** execute any Python script without first providing the researcher with clear, step-by-step setup and run instructions suitable for someone with no coding experience.
- **DO NOT** instruct the researcher to modify their operating-system or browser trust store, or any shared certificate bundle, without first explaining what the change does and obtaining their explicit consent. Prefer non-invasive, script-scoped alternatives (see Phase 3).
- **DO NOT** cite, reference, or rely on any guideline, framework, or publication that has not been independently verified as real and currently accessible.

---

## AI Transparency Block

This block must be included in the audit log and in any publication or report arising from the review.

```
AI_TRANSPARENCY:
  model_id: {exact model identifier}
  model_version: {full version string}
  model_ids_per_batch: {list — model id + version actually used for each
    screening batch; long screens span sessions and the model can change
    between sessions, so this must be recorded per batch, not assumed
    constant}
  model_provider: {provider name, e.g., Anthropic}
  inference_api_version: {API version used}
  prompt_version: {skill version, e.g., v5.0}
  temperature: 0
  seed: {researcher-set seed — logged for traceability; see
    reproducibility_basis below}

  reproducibility_basis:
    - Versioned, hashed screening prompts and eligibility criteria
      (every prompt change produces a new prompt_version_hash)
    - Fully logged per-record inputs, outputs, and structured rationales
    - The complete human-decision audit trail (hash-chained)
    - NOTE: For agentic (multi-step, tool-using) screening, a seed does
      not guarantee token-identical reasoning across runs. Reproducibility
      is achieved through the versioning and logging above, not through
      seed-level determinism of the model's reasoning.

  role_of_ai:
    - Screening recommendation only (all decisions confirmed by human)
    - Search string generation (approved by human before execution)
    - Risk of bias assessment assistance (all judgments confirmed by human)
    - PRISMA diagram generation (finalised by human)
    - Active learning calibration (prompt updated with human-approved correction examples between batches; model not fine-tuned)

  known_limitations:
    - AI may produce reasoning that appears plausible but misinterprets study content
    - AI may systematically under- or over-include certain study types depending on training data
    - temperature=0 minimises but does not eliminate output variability for agentic screening; outputs may also differ across model versions, providers, or sessions of a long screen (hence per-batch model logging)
    - Performance metrics are internal to this review and not externally benchmarked
    - AI-assisted screening does not replace independent human review; it augments it

  disclosure:
    - This review used AI-assisted screening with human audit (100% by default; if the documented risk-based audit variant was used, state it here as a limitation) and independent dual screening
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
    "model_ids_per_batch": "object — batch number → model id + version actually used (appended as batches run; see Reproducibility Statement)",
    "model_provider": "string — e.g., Anthropic",
    "inference_api_version": "string — API version",
    "temperature": 0,
    "seed": "integer — SET BY THE RESEARCHER (logged for traceability; see below)",
    "prompt_version": "v5.0",
    "max_tokens_screening": "integer — max output tokens for screening calls",
    "review_mode": "\"new\" | \"update\" — SET IN PHASE 0 (see Mode Selector)",
    "prior_corpus_paths": "array of strings — update mode only: paths to the prior review's screened corpus exports (RIS/BibTeX/CSV; EndNote libraries must be exported to RIS first)",
    "last_search_dates": "object — update mode only: per-database last-search date, e.g., {\"MEDLINE (Ovid)\": \"2023-05-14\", ...} — CONFIRMED, not assumed (see Phase 0)",
    "screening_batch_size": "integer — default 250 (full-screen execution batches; see Screening at Scale)",
    "audit_batch_size": "integer — default 25 (human audit presentation batches)",
    "audit_mode": "\"full_100_percent\" (default) | \"risk_based\" (opt-in, documented as limitation; see Gate 2)",
    "review_title": "string",
    "principal_investigator": "string",
    "date_initiated": "ISO-8601",
    "working_directory": "string — SET BY THE RESEARCHER (see below)",
    "full_text_directory": "string — SET BY THE RESEARCHER (see below)"
  }
}
```

**Seed:** Ask the researcher to provide an integer seed value. Explain honestly: "This seed is logged for traceability and is passed to any component that supports it (e.g., random sampling for pilots and ground-truth selection, where it *does* guarantee reproducible sampling). For the AI's per-record screening reasoning, the seed does **not** guarantee identical outputs — see the Reproducibility Statement below. Please provide an integer (e.g., 42, 12345), or I can generate one for your approval." Log the seed immutably once confirmed. **Do not describe the seed as ensuring "identical AI outputs" for screening.**

**Temperature=0:** Minimises output variability and creative latitude, enforcing strict adherence to criteria. It does not, on its own, make agentic screening exactly replicable.

**Directories:** Ask the researcher where they would like files saved. Provide sensible defaults (e.g., `~/systematic_review/`) but allow the researcher to specify any path. This applies to all working files and especially to full-text PDFs (Phase 6).

### Reproducibility Statement (read before making any reproducibility claim)

What this skill **can** honestly promise, and how:

1. **Prompt/criteria versioning.** Every screening prompt and every version of the eligibility criteria (including the eligibility-rules registry, Phase 5) is hashed. Every screening decision records the `prompt_version_hash` it was made under. Any decision can be traced to the exact instructions in force at the time.
2. **Complete decision logging.** For every record: the input metadata (hashed), the AI's structured rationale with evidence quotes, the recommendation, the confidence level, and the human's audit decision are logged with timestamps in the hash-chained audit log.
3. **Deterministic sampling.** Pilot samples, ground-truth samples, and batch ordering are drawn by deterministic procedures (stable-ID order or seeded sampling), so *which records were looked at, in what order* is exactly reproducible.
4. **Per-batch model identity.** The model id + version actually used is logged for every batch. Long screens span multiple sessions; the model can change between sessions, and this must be captured rather than assumed constant.

What this skill must **not** claim:

- That `temperature=0` + seed yields token-identical or decision-identical AI reasoning for interactive/agentic screening. The execution harness does not expose seed-level control over per-record reasoning the way a single raw API call might, and even then determinism is not guaranteed across infrastructure. A logged seed for the screening step is traceability, not determinism.
- That a re-run of the screen would produce "identical results." The defensible claim is: *every decision is fully documented, criterion-referenced, evidence-quoted, human-audited, and traceable to a hashed prompt version and a logged model version* — which is what reviewers and reproducers actually need.

All language elsewhere in this skill, in the AI Transparency Block, and in any generated report must be consistent with this statement.

---

## Structural Overview

This skill operates in **sequential phases** with **7 mandatory human-approval gates**. No phase may begin until the preceding phase is complete and, where applicable, human approval is logged. Phase 0 begins with a **Mode Selector** (NEW review vs UPDATE of an existing review); update-mode-only steps are marked ◆ below and are skipped for new reviews.

```
Phase 0:  Mode Selector (NEW | UPDATE), Kickoff Decision Checklist,
          Protocol Generation & Registration
          ◆ UPDATE: prior protocol/PROSPERO reuse, last-search dates,
            prior-corpus location, amendment logging
          ↓
Phase 1:  Initialisation, Configuration & Audit Logging
          ↓
Phase 2:  PICO Extraction, Study Design & Language Restrictions,
          Query Generation & Database Planning
          ◆ UPDATE: reuse prior strings verbatim + per-database
            date restriction (see Date-Limiting Reference)
          ↓ ── GATE 1: Human approves search strategy & database plan ──
Phase 3:  Database Retrieval (with institutional SSO guidance;
          NO free-API substitution for institutional databases)
          ↓
Phase 4:  Stable Record IDs + Deterministic Deduplication
          (HITL for suspected duplicates)
          ◆ Phase 4b (UPDATE): Dedup vs prior corpus + carry-forward
            of prior decisions
          ↓
Phase 5a: Screening Calibration Pilots (pilot → 100% audit → κ gate →
          calibrate → re-pilot; eligibility-rules registry built here)
          ↓ ── GATE 2a: Criteria locked (κ ≥ 0.60 on a fresh pilot,
               convergence demonstrated) ──
Phase 5:  Title-Abstract Screening at Scale (batching, checkpoint/
          resume, throughput planning) + Performance Monitoring
          ↓ ── GATE 2: 100% human audit (default) or documented
               risk-based audit + 20% ground-truth validation ──
Phase 5b: Independent Dual Screening & Conflict Resolution
          ↓ ── GATE 2b: Resolve all conflicts; compute Cohen's Kappa
               (+ % agreement + PABAK) ──
Phase 6:  Full-Text Retrieval (researcher-set directory)
          ↓
Phase 7:  Full-Text Screening + Performance Monitoring + Dual Screening
          ↓ ── GATE 3: 100% human audit + conflict resolution ──
Phase 8:  Risk of Bias Assessment (researcher-provided framework)
          ↓ ── GATE 4: 100% human audit of all RoB judgments ──
Phase 9:  PRISMA Flow Diagram Generation (new-review or update layout)
          ↓ ── GATE 5: Researcher finalises diagram ──
Phase 10: Export & Reporting (including AI Transparency Statement)
```

**Phase 5a runs before the full Phase 5 screen.** It is numbered 5a because it *is* screening — pilot rounds of it — but it is a hard prerequisite: the full screen must not begin until Gate 2a is passed.

**Failure recovery:** If the process is interrupted at any phase, it can be resumed from the last completed phase by validating the audit log's hash chain integrity. Log the resumption event, including the phase resumed from and the chain verification result. **Within Phase 5 and Phase 7, recovery is finer-grained:** screening decisions are checkpointed to disk per batch (and per sub-chunk where possible — see Screening at Scale), so an interrupted screen resumes from the last persisted record, not the start of the phase. Log a `SCREENING_RESUMPTION` event with the batch number, last completed record ID, and chain verification result.

---

## Audit Log Specification

### Initialisation

Immediately create `audit_log.json` using the schema below. Every action, decision, configuration change, human override, and performance metric is logged here with a timestamp. This is the single source of truth for the review.

### Schema

```json
{
  "schema_version": "5.0",
  "review_metadata": {
    "review_title": "",
    "protocol_id": "",
    "prospero_id": "",
    "review_mode": "new | update",
    "prior_review": {
      "comment": "update mode only — null for new reviews",
      "prior_protocol_id_or_prospero_id": "",
      "prior_corpus_paths": [],
      "prior_corpus_record_count": null,
      "last_search_dates": {},
      "last_search_dates_confirmed_by": "researcher | librarian | assumed (flagged as limitation)",
      "protocol_amendments": []
    },
    "date_initiated": "ISO-8601",
    "principal_investigator": "",
    "config": {
      "model_id": "",
      "model_version": "",
      "model_ids_per_batch": {},
      "model_provider": "",
      "inference_api_version": "",
      "temperature": 0,
      "seed": null,
      "prompt_version": "v5.0"
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
  "phase": "0–10 (including 4b, 5a, 5b)",
  "action": "descriptive string",
  "actor": "AI | HUMAN | SYSTEM",
  "record_id": "string | null — the STABLE record ID (see Phase 4) for any entry concerning a specific record; null for phase-level entries",
  "batch_number": "integer | null — screening batch this entry belongs to, if applicable",
  "model_id_used": "string | null — model id + version that produced this output, for AI entries (long screens span sessions; do not assume it matches config.model_id)",
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

**Key changes in v5.0:**
- `review_mode` and `prior_review` metadata (Update-Review Mode).
- `record_id` on every record-level entry uses the **stable record ID** from Phase 4 (hash of normalised DOI, or normalised title if no DOI) — never a positional index.
- `batch_number` and `model_id_used` on screening entries: every batch logs the model id + version actually in use.
- The audit log is complemented by per-batch **checkpoint files** on disk (see Screening at Scale) so screening progress survives interruption; the audit log remains the single source of truth for *decisions*, while checkpoint files are the operational resume mechanism.

**Every entry records the date and time of creation.** The `created_at` field uses full ISO-8601 format including timezone (e.g., `2026-04-13T14:32:07+01:00`). Human review actions additionally record `reviewed_at`. This applies to all entries across all phases.

### Chain Integrity

Each entry's `previous_entry_hash` contains the SHA-256 hash of the entire preceding entry (serialised as canonical JSON). This creates a tamper-evident chain. On review export, provide a verification script that validates the full chain.

---

## Phase 0: Mode Selection, Kickoff Checklist, Protocol Generation & Registration

### Step 0.1: Mode Selector (MANDATORY FIRST QUESTION)

Before anything else, ask:

> "Is this a **NEW** systematic review, or an **UPDATE** of an existing review (e.g., re-running the searches of a published or PROSPERO-registered review to capture studies published since the last search)?"

Log the answer as `review_mode` in the configuration and audit log. Updates are a large share of real-world review work and follow a materially different path; do not force them through the fresh-review workflow.

**If UPDATE, elicit and log all of the following before proceeding:**

1. **Prior protocol identity.** The prior protocol / PROSPERO ID. If the researcher cannot produce a registration ID, record "assumed registered" or "not registered" with justification — this is a reportable limitation, not a blocker.
2. **Prior protocol reuse.** Confirm that the prior protocol's eligibility criteria, RoB tools, and database set are being **reused**. Any change is a **protocol amendment**: log each amendment as a deviation with explicit justification and researcher approval (reuse the existing deviation-logging mechanism from Step 7 below). Amendments to eligibility criteria apply **at screening only — they must not alter search breadth** (see Phase 2 update rules).
3. **Last-search date, per database.** Ask for the last-search date **for each database separately** — they often differ. Then apply this rule: **confirm, don't assume.** Dates recorded in prior papers or spreadsheets are frequently data-entry dates, export dates, or manuscript dates rather than true search cutoffs. Ask the researcher to verify each date against the prior review's PRISMA-S search documentation (or with their librarian). Log each date with `last_search_dates_confirmed_by` (researcher / librarian / assumed — the last flagged as a limitation).
4. **Prior screened corpus location.** Where are the prior review's records and decisions? Accept: an EndNote library (`.enl` — must be exported to RIS before processing), RIS/BibTeX exports, or a CSV/spreadsheet of records with decisions. Confirm **what the corpus contains** — in particular, whether it already includes any previous update rounds (so the dedup baseline is complete). Log paths as `prior_corpus_paths` and the record count.
5. **Source-to-role mapping.** If the researcher supplies spreadsheets/documents from the prior review, explicitly confirm which file/tab plays which role: research question, search strings per database, screening protocol/eligibility criteria, prior decisions. Do not guess; log the confirmed mapping.
6. **Carry-forward rule.** Records in the new retrieval that are already present in the prior corpus are removed before screening (Phase 4b), and any record already adjudicated in the prior review **carries its prior decision forward** — it is not re-screened unless the researcher explicitly requests re-screening (log that request as an amendment).

### Step 0.2: Kickoff Decision Checklist (both modes)

The following decisions are elicited **deliberately at kickoff**, not discovered mid-flight. Present them as a checklist, record every answer (including "decide later at Phase X", which must name the phase), and log all responses:

1. **New vs update** (Step 0.1) and, for updates, prior protocol/registration reuse.
2. **Source-to-role mapping** for any provided documents (Step 0.1.5).
3. **Baseline corpus** for update dedup, and confirmation of its completeness (Step 0.1.4).
4. **True last-search dates per database**, confirmed (Step 0.1.3), and the correct per-database "date added" field to limit on (see the Date-Limiting Reference in Phase 2 — these differ by platform and drift across versions).
5. **API substitution policy.** State the default plainly: *free/public APIs are NOT substituted for the protocol's institutional databases* (see Boundaries and Phase 3). Confirm the researcher understands searches of Ovid/EBSCO/Scopus/ProQuest/Web of Science will be run through the institutional interfaces with manual export.
6. **Export completeness requirements.** Exports must include abstracts (screening is crippled without them — re-export if missing) and hit-count vs export-count discrepancies will be recorded (see Phase 3).
7. **PICO amendment rule** (updates): amendments apply at screening only and do not alter search breadth.
8. *(Deferred by design)* **Nuanced eligibility rules** beyond raw PICO — informant vs subject, condition boundaries, traits vs diagnosis, proxy outcomes, publication-type handling — are expected to surface during the calibration pilots and are captured in the **eligibility-rules registry** (Phase 5a). Tell the researcher this will happen so it is anticipated, not alarming.
9. **Reviewer B identity** for independent dual screening: a second human reviewer (preferred, Cochrane-compliant) or a second blinded AI pass (documented as a limitation). Decide now so Phase 5b is not blocked.
10. **Audit depth** at large N: 100% human audit (default, gold standard) or risk-based audit (opt-in, documented as limitation — see Gate 2). Give the researcher the upfront throughput estimate context from Screening at Scale before they choose.
11. **Full-screen pacing:** stage-and-audit per batch (screen a batch → human audits it → next batch) vs one consolidated pass (screen everything → single audit). Set expectations that a genuine per-record screen of thousands of records **spans multiple sessions** (see Throughput Honesty, Phase 5).

Log the completed checklist as a single audit entry with `created_at`.

### Step 0.3: Protocol Generation & Registration

1. Ask the researcher for their research question (for updates: confirm the prior question, noting any amendment).
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

**Update mode:** Instead of drafting a fresh protocol, generate a **protocol amendment document** that (a) references the prior protocol/PROSPERO record, (b) restates the reused eligibility criteria verbatim, (c) lists every amendment with justification, (d) records the confirmed per-database last-search dates and the update search window, and (e) states the carry-forward rule for previously adjudicated records. Present it for approval and lock it exactly as for a new protocol. Prompt the researcher to update their PROSPERO record where applicable.

### Logged Outputs
- `review_mode` and (update mode) the full prior-review block: prior protocol ID, confirmed last-search dates per database, prior corpus paths and record count, amendments.
- Completed Kickoff Decision Checklist.
- Protocol document or protocol amendment document (full text, hashed).
- PROSPERO registration ID (or "not registered" with justification).
- Researcher approval timestamp (`created_at`).

---

## Phase 1: Initialisation, Configuration & Audit Logging

### Instructions

1. Create `audit_log.json` with the schema above.
2. Present the configuration block to the researcher. Require them to:
   - Confirm or set the model identifier, model provider, and inference API version.
   - **Set the seed value** (logged for traceability — use the honest explanation from the Configuration Block, not "identical outputs" language).
   - Confirm temperature=0.
   - Confirm `review_mode` and, for updates, `prior_corpus_paths` and `last_search_dates` (from Phase 0).
   - Confirm `screening_batch_size` (default 250), `audit_batch_size` (default 25), and `audit_mode` (default full 100%).
   - **Set the working directory** for all review files.
   - **Set the full-text PDF directory** (default: `{working_directory}/full_texts/`).
3. Populate the AI Transparency Block and log it as the first audit entry (with `created_at` timestamp).
4. Create the working directory structure at the researcher's chosen path:

```
{working_directory}/
├── audit_log.json
├── protocol.md
├── ai_transparency_statement.md
├── eligibility_rules_registry.json   ← built during Phase 5a, locked at Gate 2a
├── searches/
├── records/
│   └── prior_corpus/    ← update mode: prior review's exported corpus
├── full_texts/          ← or researcher's custom path
├── screening/
│   ├── pilots/          ← Phase 5a: per-pilot samples, audits, κ reports
│   ├── title_abstract/
│   │   └── batches/     ← per-batch raw metadata, decisions, worksheets, checkpoints
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

**Update mode — reuse, don't regenerate.** For an update review, the prior review's per-database search strings are **reused verbatim**, with exactly one modification: a date restriction limiting results to records added since the confirmed last-search date for that database (see Step 2.3c). Do not "improve" the strings — changed strings change the evidence base and break comparability with the prior review. Any protocol amendment to eligibility (Phase 0) applies **at screening only and must not alter search breadth**. If a prior string is genuinely broken (e.g., a field tag the platform no longer supports), fix the minimum necessary, log it as a deviation, and flag it in the PRISMA-S search documentation. Cross-validation (below) still runs on the reused strings to catch platform drift.

For new reviews:

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

**Scope warning — the automatable set rarely matches real reviews.** The APIs above (PubMed E-utilities, Europe PMC, ClinicalTrials.gov, OpenAlex, plus Scopus where the institution has an API key) cover only part of a typical protocol. Real reviews are predominantly run through **institutional platforms** — Ovid (MEDLINE, Embase, PsycINFO), EBSCO (CINAHL, PsycINFO), Scopus, ProQuest, Web of Science — with manual export. **Do not substitute a free API for an institutional database named in the protocol** (e.g., do not run PubMed E-utilities "instead of" Ovid MEDLINE, or OpenAlex "instead of" Scopus). The indexing, controlled vocabulary handling, and date fields differ; substitution silently changes the evidence base. If the researcher genuinely wants a substitution, it is a protocol deviation: explain the consequence, obtain explicit approval, and log it.

### Step 2.3c: Date-Limiting Syntax Reference (update searches)

An update search must be limited by **when the record entered the database** ("date added" / "entry date"), not by publication date — publication dates lag indexing and using them either misses late-indexed studies or re-retrieves thousands of already-screened records. The correct field differs per platform:

| Platform | Field / mechanism | Example (records added since 14 May 2023) |
|---|---|---|
| Ovid (MEDLINE, Embase, PsycINFO) | Entry/update date fields via the `limit` command — commonly `dt=` (date created), `up=` (update/revision date), `dd=` (date delivered); availability and meaning vary by segment | e.g., `limit N to dd=20230514-20260707` |
| EBSCO (CINAHL, PsycINFO) | `EM` (Entry Month/date) field | `EM 202305-` appended with `AND` |
| Scopus | `ORIG-LOAD-DATE` | `AND ORIG-LOAD-DATE AFT 20230514` |
| ProQuest | `PDN` (or platform date-added limiter in the interface) | `AND PDN(>20230514)` |
| Cochrane Library | Interface limiter: "Date added to database" / custom range in Search Limits | set in the Limits panel; record the exact limiter used |
| Web of Science | Interface Timespan / "Index Date" limiter | set in the interface; record the exact limiter used |
| PubMed (E-utilities / interface) | `[edat]` (Entrez date) or `[crdt]` (create date) rather than `[dp]` | `AND 2023/05/14:3000[edat]` |

**MANDATORY caveats, presented to the researcher verbatim in substance:**

1. **"Verify live with your librarian."** Date-field syntax **drifts across platform versions and licensing segments**. The table above is a starting point, not an authority. Before Gate 1, the researcher (ideally with their institution's librarian) must verify each date limiter live in the actual interface, and the verified syntax is what gets logged and reported per PRISMA-S.
2. **Entry-date vs publication-date trade-off.** Limiting on entry date is standard for updates but can miss records whose entry date predates the last search while the search itself missed them. If the prior review's search documentation is uncertain, offer a buffer (e.g., set the cutoff a few months before the nominal last-search date) and log the choice.
3. **Record what was actually run.** For every database, log the exact final string including the date limiter, the date it was run, and the interface hit count (needed for Phase 3's export integrity check and Phase 9's PRISMA counts).

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
- **Update mode:** confirm that each reused string is verbatim-identical to the prior review's string apart from the date limiter, and confirm that each date limiter's syntax has been **verified live** in the target platform (Step 2.3c) — ideally with the librarian.
- Confirm that no institutional database has been silently replaced by a free API (see the scope warning above).
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

**Reminder (Boundaries):** if a protocol database is institutional-only, the path is manual search + export — never a free-API substitute.

### Export Integrity Check (all manual exports, both modes)

After integrating each manual export, run and log two checks:

1. **Abstract completeness.** Count records with a non-empty abstract field. If a substantial share of records lack abstracts (some platforms' default export profiles omit them — this has crippled screening in practice), **stop and ask the researcher to re-export with abstracts included** (e.g., choose the "full record"/"complete reference" export profile) before proceeding. Log the re-export.
2. **Hit-count vs export-count reconciliation.** Compare the interface hit count (recorded at search time, Step 2.3c) with the number of records actually present in the export file. Small discrepancies are common (e.g., interface says 1,159; the RIS holds 1,157 — records withdrawn or deduplicated by the platform between search and export). Log both numbers and the delta. If the delta is small, record it and proceed; if it is large or unexplained, ask the researcher to re-run the export. The PRISMA "records identified" count uses the **exported** count, with the discrepancy noted in the search documentation.

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

> **"Your network appears to intercept HTTPS connections (SSL inspection). This is common on university and hospital networks. Here are three ways to fix it. Option A changes nothing on your system; Options B and C are explained so you can decide whether you consent to them:**
>
> **Option A (recommended — non-invasive, script-scoped): Point this script at your institution's certificate via an environment variable**
> Obtain your institution's CA certificate file from your IT help desk (usually a `.pem` or `.crt`), or use your system's bundle if it already includes it. Then run the script with the `SSL_CERT_FILE` environment variable set — this affects **only the command you run**, and changes nothing permanently:
> - **Mac/Linux:** `SSL_CERT_FILE=/path/to/institution-ca.pem python3 retrieval_script.py`
>   (If your system bundle already trusts the institutional CA, try `/etc/ssl/certs/ca-certificates.crt` on Linux or `/etc/ssl/cert.pem` on Mac.)
> - **Windows:** `set SSL_CERT_FILE=C:\path\to\institution-ca.crt` then run the script.
>
> **Option B (persistent — requires your consent to modify a certificate bundle): Append your institution's CA certificate to Python's `certifi` bundle**
> **What this changes:** it edits the certificate bundle that *all Python programs using certifi in this environment* will trust from now on (it does not touch your operating system or browser trust store). Only do this if you understand and accept that. If you consent:
> 1. Get the institution's root CA certificate file from IT.
> 2. Find the bundle: `python3 -c "import certifi; print(certifi.where())"`
> 3. Paste the certificate's contents at the end of that file and save. (Note: reinstalling/upgrading `certifi` undoes this.)
> 4. Re-run `network_check.py` to verify.
> Using a virtual environment (as set up in Step 3 above) keeps this change contained to the review project.
>
> **Option C (last resort — less secure): Disable SSL verification for this script only**
> This skips certificate checking entirely. Only use this if Options A and B fail, and only for the retrieval script.
> The retrieval script includes a `--no-ssl-verify` flag for this purpose. Running with this flag will print a security warning.
> **Note:** This does not affect your browser or other applications.
>
> **I will never ask you to modify your operating-system or browser trust store. If IT documentation suggests that, it is your and your IT department's decision, not part of this workflow.**"

### Retrieval Script

Provide a Python script using `requests` for all HTTP-based API access, plus `pybliometrics` for Scopus. **Do not use `metapub`.** Direct NCBI E-utilities calls via `requests` give full control over SSL handling, pagination, query encoding, and error diagnostics.

- `requests` + `certifi` — All HTTP-based API access (PubMed E-utilities, Europe PMC, ClinicalTrials.gov, OpenAlex, Crossref)
- `pybliometrics` — Scopus (requires institutional API key)

**Note on deprecated/replaced libraries:** This skill does not use `metapub` (adds an abstraction layer with quirks including Borg singleton state, creation-date-based date filtering, and limited error visibility), `pytrials` (built for the retired ClinicalTrials.gov classic API), or `ebscopy` (unmaintained). For EBSCO databases (CINAHL, PsycINFO via EBSCO), use manual search and export (see below). For Web of Science, the `clarivate-wos-starter-python-client` is available from GitHub (not PyPI) — alternatively, use manual search and export.

**Before the script,** list the exact `pip install` command:
```
pip install requests certifi pybliometrics==4.4.1
```

### Environment-Fragility Fallbacks (NEVER assume the happy path)

Locked-down institutional machines routinely have broken or unavailable packaging: `pip install` may be blocked by proxy policy, `requests` may be present but broken (e.g., an incompatible `urllib3`/OpenSSL pairing), and admin rights may be absent. **Never assume `pip install` succeeds.** Apply this ladder:

1. **Try the preferred dependency** (`requests`, `bib-dedupe`, etc.) inside the virtual environment.
2. **If installation or import fails, fall back to the Python standard library** rather than sending the researcher on an environment-repair quest:
   - **HTTP:** every retrieval script must be written so its network layer can run on `urllib.request` alone (the Network Environment Check above already uses `urllib` for exactly this reason). Provide a `--stdlib-http` mode or an automatic fallback: `try: import requests ... except ImportError: use urllib`. The `--no-ssl-verify` flag must work in both modes (for `urllib`, via an unverified `ssl` context, with the same printed warning).
   - **Deduplication:** if `bib-dedupe` cannot be installed, use the pure-stdlib deterministic fallback specified in Phase 4.
3. **Diagnose before replacing.** If an import fails with an error other than `ModuleNotFoundError` (e.g., SSL/compiled-extension errors), show the researcher the exact error, explain in plain language, and offer the stdlib path immediately rather than iterating on installs.
4. **Log the fallback.** Record in the audit log which implementation actually ran (library + version, or "stdlib fallback"), since PRISMA-S asks for the tools used.

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

## Phase 4: Stable Record IDs & Deterministic Deduplication

### Step 4.0: Stable Record IDs (MANDATORY — assign before anything else)

Every record that survives into screening gets a **stable, content-derived ID** that survives dedup re-runs, source re-exports, and re-ordering. Positional IDs (row numbers, "record 1..N") **break** the mapping between decisions and records the first time anything is re-run — never use them as the ID of record-level decisions.

**ID rule:**
- If the record has a DOI: `record_id = SHA-256(normalised_DOI)` (lowercase; strip `https://doi.org/`, `doi:` prefixes, and surrounding whitespace), truncated to the first 16 hex characters for readability.
- If no DOI: `record_id = SHA-256(normalised_title + "|" + year)` — title lowercased, punctuation and extra whitespace stripped; year as 4 digits or empty string if unknown.
- Prefix with `R-` (e.g., `R-a3f19c02d4e88b71`).
- The normalisation functions are part of the review's code and are logged (hashed), so IDs are recomputable by anyone.

All audit entries, decisions files, checkpoints, worksheets, dual-screening records, and PRISMA counts reference records by this stable ID.

### Instructions

**Provide the Python setup instructions (from Phase 3) if not already completed. List the specific `pip install` command for this script's dependencies:**
```
pip install bib-dedupe
```

**If `bib-dedupe` cannot be installed** (blocked pip, dependency conflicts — see Environment-Fragility Fallbacks, Phase 3), use the **pure-stdlib deterministic fallback**, which preserves the "deterministic only, HITL for suspected" rule:
- **Auto-merge (confident duplicates):** exact normalised-DOI match, OR exact normalised-title + year match (same normalisation as Step 4.0).
- **Human-review queue (suspected duplicates):** `difflib.SequenceMatcher` ratio on normalised titles above a configurable threshold (default 0.90) where DOI/year do not confirm — presented to the researcher one by one, exactly like `bib-dedupe`'s suspected-duplicate flow. No probabilistic auto-merging.
- Log which implementation ran.

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

### Phase 4b (UPDATE MODE ONLY): Deduplication Against the Prior Corpus & Carry-Forward

After within-retrieval dedup, remove from the screening set every new record that is **already present in the prior review's screened corpus** — screening them again wastes the dominant cost centre of the review and corrupts the PRISMA update counts.

1. **Ingest the prior corpus** from `prior_corpus_paths` (RIS/BibTeX/CSV; EndNote libraries exported to RIS first — see Phase 0). Assign stable IDs (Step 4.0) to every prior-corpus record using the same normalisation code.
2. **Match** new records to prior-corpus records with the same deterministic rules as within-retrieval dedup (exact normalised DOI; exact normalised title+year; `difflib` fuzzy matches go to the human-review queue). **No probabilistic auto-removal.**
3. **Carry-forward:** for every matched record, look up the prior review's decision if the corpus export contains one, and record it in the audit log as `decision_source: "carried_forward_from_prior_review"`. Carried-forward records are **not re-screened** (per the Phase 0 carry-forward rule) unless the researcher explicitly requested re-screening as a logged amendment. If the prior corpus contains records but no decisions, log the match as "present in prior corpus — removed from update screening set" without inventing a decision.
4. **Log counts** (these feed the PRISMA update layout, Phase 9):
   - New records after within-retrieval dedup.
   - Records matched to the prior corpus and removed (auto vs human-confirmed).
   - Carried-forward decisions by type.
   - **Records to screen in this update** (the carry-forward screening set).
5. **Sanity report to the researcher:** present prior-corpus size, match counts, and the final screening-set size, and ask for confirmation before Phase 5a begins (e.g., "Prior corpus: 17,483 records. New retrieval after dedup: 4,515. Matched to prior corpus and removed: 2,261. **To screen in this update: 2,254.** Proceed?").

---

## Phase 5a: Screening Calibration Pilots (MANDATORY before the full screen)

### Rationale

Screening thousands of records under un-validated criteria wastes the human's audit effort and risks **systematic** error that a per-record audit will not surface as a pattern until far too late. This phase validates the screening — criteria, prompt, and rules — on small pilots with 100% human audit and an agreement gate, **before** committing to the full set. The Cochrane Handbook's requirement to pilot-test eligibility criteria and screening forms is implemented here for AI-assisted screening. In operational use this loop has taken agreement from κ ≈ 0.30 (raw PICO criteria) to κ ≥ 0.70 (after rule extraction) in two to three cycles; do not skip it.

### The loop

```
Pilot (50 records, stratified) → blind 100% human audit → compute
κ + % agreement + PABAK → κ ≥ 0.60 on this fresh pilot?
   NO  → extract disagreement-derived rules → researcher approves →
         update prompt + eligibility-rules registry (new prompt hash)
         → run a NEW pilot on FRESH records → repeat
   YES → convergence check passed? (see below)
            NO  → one more pilot (harder, include-enriched, no new rules)
            YES → LOCK criteria → GATE 2a → Phase 5 full screen
```

### Step 5a.1: Pilot sampling (stratified, not random)

Default pilot size: **50 records**, drawn from **fresh records only** (never records used in a previous pilot).

**Do not draw a purely random pilot.** With typical screening prevalence, a random sample is ~90% easy excludes and tells you almost nothing about the dangerous cells (missed includes, mishandled edge cases). Instead:

1. Have the AI screen a **seeded candidate slice** of the pool (3–5× the pilot size, drawn deterministically by stable-ID order or seeded sampling) using the current prompt and criteria.
2. From the AI's outputs on that slice, draw the 50-record pilot **stratified by AI decision × confidence**, oversampling the informative cells: include **all** INCLUDE and UNCERTAIN recommendations (up to ~half the pilot), then low-confidence EXCLUDEs, topping up with a random draw of high-confidence EXCLUDEs.
3. A deterministic keyword classifier **may** be used to enrich the candidate slice for likely-relevant records — but only as a clearly labelled **high-recall triage/stratification aid, never the authoritative screen** (see Boundaries; in operational use such classifiers over-include by 3–4×, which is fine for enrichment and invalid as a screen).
4. Log the sampling scheme, seed, slice, and final pilot composition.
5. **Pre-lock outputs do not count.** AI outputs on candidate-slice records that were *not* selected into a pilot were produced under un-locked criteria: mark them superseded and return those records to the pool for re-screening under the locked prompt in Phase 5. Only pilot records receive final (human) decisions in this phase.

### Step 5a.2: Blind 100% human audit of the pilot

The researcher screens **all 50 pilot records without seeing the AI's recommendations** (ground-truth style presentation, as in Phase 5's Human Ground-Truth Validation), recording a decision (INCLUDE / EXCLUDE / UNCERTAIN-defer) and a brief reason for each. Only after all 50 human decisions are recorded are the AI's outputs revealed and compared. Pilot decisions made by the human are **final human decisions** — they carry into the review's results and these records are not re-screened.

### Step 5a.3: Compute the agreement metrics (all of them, every pilot)

Report, for every pilot, **all** of the following — never κ alone (see the κ Interpretation Guidance in Phase 5 for why):

- **Cohen's κ, 3-category** (INCLUDE / EXCLUDE / UNCERTAIN).
- **Cohen's κ, binary retain/discard** (retain = INCLUDE or UNCERTAIN; discard = EXCLUDE). This is the **primary gate metric**, because retain/discard is what determines whether a study survives to full text.
- **Raw % agreement** (both forms).
- **PABAK** (prevalence-adjusted bias-adjusted kappa): binary `PABAK = 2·Pₒ − 1`; k-category `PABAK = (k·Pₒ − 1)/(k − 1)`, where Pₒ is observed agreement.
- **The disagreement table itself**, with direction: AI-discard/human-retain cells (potential missed includes) are the dangerous ones and warrant rule extraction **even when κ passes the gate**.
- Note the pilot's composition (stratified pilots deliberately shift prevalence, which moves κ between pilots even at identical % agreement — interpret accordingly).

### Step 5a.4: κ gate and calibration cycles

**Gate rule: proceed to the full screen only when binary retain/discard κ ≥ 0.60 on a fresh pilot.** The 0.60 threshold is a heuristic gate, read alongside % agreement, PABAK, and the direction of disagreements — not a mechanical pass/fail in isolation.

If the gate fails (or dangerous-direction disagreements demand it):

1. **Extract candidate rules from every disagreement.** For each pilot disagreement, identify what general rule would have produced the human's decision. Draft it as (a) a one-sentence rule for the **eligibility-rules registry** (below) and, where a concrete exemplar helps, (b) a few-shot calibration example in the existing Active Learning format (Phase 5) — the two mechanisms share the same review-and-approve flow.
2. **Researcher approves, modifies, or rejects each rule/example.** Log per the Active Learning calibration schema, with `trigger.gate: "Gate 2a"` and `trigger.milestone` naming the pilot.
3. **Update the prompt** (rules registry block + calibration examples), hash it as a new `prompt_version_hash`.
4. **Run a NEW pilot on fresh records** (Step 5a.1) under the updated prompt. Never re-score the same pilot with new rules and call it validation — rules derived from a pilot's disagreements will trivially "fix" that pilot.

### Step 5a.5: Convergence (stability) check and criteria lock

Before locking, require **at least one pilot that passes the κ gate without needing any new rules**, drawn as a *harder* sample (include-enriched / edge-case-enriched stratification). Passing only on pilots that each generated fresh rules means the criteria are still moving; convergence means a fresh, difficult sample was handled by the existing ruleset.

When convergence is demonstrated: **LOCK the criteria** — the PICO criteria, the eligibility-rules registry, and the calibration examples are frozen as the locked screening specification, with a final `prompt_version_hash`. Any later change is a logged protocol deviation requiring researcher approval, and triggers the question of whether already-screened batches must be re-screened under the new rules (present the trade-off; log the decision).

### The Eligibility-Rules Registry (created here; used everywhere)

Raw PICO cannot express the rules that actually decide borderline records. Maintain `{working_directory}/eligibility_rules_registry.json` as the machine-readable, versioned home for them. The calibration loop (5a and the per-batch Active Learning protocol in Phase 5) **writes into this registry**; the screening prompt **reads from it** (as the `{ELIGIBILITY_RULES_BLOCK}`).

Schema per rule:

```json
{
  "rule_id": "ER-001",
  "category": "publication_type | condition_boundary | informant_vs_subject | traits_vs_diagnosis | population_subgroup | proxy_outcome | other",
  "statement": "one-sentence operational rule, phrased so a screener (human or AI) can apply it directly",
  "disposition": "INCLUDE | EXCLUDE | UNCERTAIN (defer to full text)",
  "origin": "pilot/batch + record_id(s) of the disagreement(s) that produced it",
  "approved_by": "researcher id",
  "approved_at": "ISO-8601",
  "status": "ACTIVE | RETIRED | SUPERSEDED",
  "prompt_versions": ["hashes of prompt versions containing this rule"]
}
```

**The registry must be able to represent, at minimum, rules of these kinds** (illustrative phrasings — actual rules come from this review's disagreements and the researcher's judgment):

- **Condition boundaries:** e.g., studies of condition sub-types that a criterion's framework has reclassified count only when studied *alongside* the in-scope conditions, not alone.
- **Informant vs subject:** e.g., a parent/carer reporting *on the participant's* outcome is includable; the parent's *own* outcome as the endpoint is not.
- **Traits vs diagnosis:** e.g., samples defined by elevated traits are excluded where the population criterion requires formal diagnosis; a **distinct, formally diagnosed subgroup** within a broader sample may be UNCERTAIN (defer), whereas a sample where in-scope participants are merely *possibly present* is excluded.
- **Proxy/partial outcomes:** whether outcome-adjacent proxies, impact measures, or instrument subscales count as measuring the outcome.
- **Context-specific outcome variants:** e.g., transient situational forms of the outcome (such as procedural/perioperative states) may be UNCERTAIN rather than a clean include/exclude.
- **Publication-type nuance:** conference abstracts reporting a real study, letters, case reports, and book chapters are **not auto-excluded** (assess against criteria; often UNCERTAIN → full-text/adjudication); reviews, meta-analyses, editorials, and overview presentations are excluded (with citation-chasing of relevant reviews noted separately).

### ── GATE 2a: Calibration Complete — Criteria Locked ──

**MANDATORY.** Present to the researcher: every pilot's composition and metrics (κ ×2, % agreement, PABAK, disagreement tables), the full eligibility-rules registry, the active calibration examples, and the final locked `prompt_version_hash`. The researcher confirms the lock. Log confirmation with `created_at`.

**Do not begin the full Phase 5 screen until Gate 2a is passed.**

---

## Phase 5: Title-Abstract Screening (AI-Assisted)

### Screening at Scale (Execution Protocol)

Genuine per-record LLM reading of the screening pool is **the dominant cost centre of the entire review**. It is a multi-hundred-step, multi-session effort, not an atomic action. This protocol is how it is actually executed.

**1. Stable record IDs (mandatory).** All screening artefacts key on the stable IDs from Phase 4 (Step 4.0). Re-runs, re-exports, and dedup re-runs must never scramble the decision↔record mapping.

**2. Batching.** Screen in fixed batches (default **250** records; `screening_batch_size` in config), drawn **deterministically** — by stable-ID sort order, or by a documented stratified scheme carried over from Phase 5a. Every batch produces three files in `screening/title_abstract/batches/`:
   - `batch_{N}_records.json` — the raw metadata of the batch's records (frozen input);
   - `batch_{N}_decisions.jsonl` — **append-only**: one line per completed record with the AI's structured output, `prompt_version_hash`, `model_id_used`, and timestamp;
   - `batch_{N}_worksheet.csv` — the human-audit worksheet, ordered by audit priority (see Gate 2), with columns for the human's AGREE/OVERRIDE and reason.

**3. Checkpoint / resume.** The append-only decisions file **is** the checkpoint: it is flushed to disk record-by-record (or at worst per small sub-chunk), so any interruption — session end, crash, network loss — resumes from the last completed record, never restarts a batch. On resume: verify the audit-log hash chain, reconcile the decisions file against the audit log, log a `SCREENING_RESUMPTION` event (batch, last completed record ID, chain verification result), and confirm the `model_id` of the resuming session (if it differs from the previous session's, log it — this is expected across long screens and is why `model_id_used` is recorded per batch and per entry).

**4. Throughput honesty (set expectations upfront).** Before the full screen begins, give the researcher an explicit estimate: *records → batches → sessions*. State plainly that genuine reading of each record is what makes the screen valid and that thousands of records **do not screen instantly** — e.g., "2,254 records = 10 batches of 250; expect this to span multiple working sessions." Let the researcher choose the pacing agreed at kickoff (checklist item 11): **stage-and-audit** (screen batch → human audits it → calibration check → next batch; slower wall-clock, catches drift earliest) or **one consolidated pass** (screen all batches, then audit; faster to a full recommendation set, drift caught only by the automatic monitors). Log the choice. Never silently degrade to rushed, shallow reads to appear fast — a fast invalid screen is worthless.

**5. Classifier vs reader (hard rule).** Any deterministic keyword classifier, embedding ranker, or similar triage mechanism used for stratification or prioritisation must be labelled in all outputs and logs as a **high-recall triage aid, not the authoritative screen**. The authoritative recommendation for every record comes from genuine structured reading (the prompt below). Record in the audit log that this is so. (Operationally, keyword classifiers over-include several-fold; treating one as the screen would invalidate the review.)

**6. Per-batch model logging.** At the start of every batch (and after every resumption), record the model id + version in `model_ids_per_batch` and on each decision entry.

### Screening Prompt Template

For each record, use the following structured prompt at `temperature=0`, under the **locked** criteria and `prompt_version_hash` from Gate 2a. **Hash every LLM response and log the hash in `output_hash`.** (The researcher's seed is logged for traceability; per the Reproducibility Statement, do not describe screening outputs as seed-reproducible.)

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

{ELIGIBILITY_RULES_BLOCK — the ACTIVE rules from the eligibility-rules
registry (locked at Gate 2a), rendered as:
"ELIGIBILITY RULES (researcher-approved refinements of the criteria
above; apply them wherever they bear on a criterion):
 ER-001 [{category}]: {statement} → {disposition}
 ..."}

{CALIBRATION_EXAMPLES_BLOCK — populated during the Phase 5a pilots and
by the Active Learning Protocol (see below) between batches}

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

**When a registry rule bears on a criterion,** the structured rationale must name the rule ID applied (in `decision_rule_applied`), so every borderline decision is traceable to an approved rule rather than to ad-hoc judgment.

### UNCERTAIN routing and confidence levels (defined)

- **UNCERTAIN routing:** every record whose final (human-confirmed) status is UNCERTAIN is **retained** — it proceeds to full-text retrieval (Phase 6) and full-text screening/adjudication (Phase 7). UNCERTAIN is never a soft exclude.
- **Confidence levels** (the AI must apply these definitions, not vibes):
  - **High** — every applicable criterion was assessed on explicit abstract evidence (direct quotes); no UNCLEAR assessments.
  - **Medium** — the decision rests partly on reasonable inference (e.g., population strongly implied but not stated); at most one criterion inferred rather than quoted.
  - **Low** — one or more criteria assessed with "No information in abstract" or conflicting signals; the recommendation could plausibly flip at full text.
- Low-confidence decisions are ordered first within their category in the human-audit worksheet (see Gate 2).

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

#### κ Interpretation Guidance (applies everywhere κ is computed: Phase 5a pilots, Gate 2b, Phase 7)

Cohen's κ is mandatory but **base-rate sensitive**, and screening prevalence is heavily skewed (often ~90% exclude). This produces the well-known **"kappa paradox"**: at high, even identical, raw agreement, κ moves substantially with the prevalence mix of the sample. Operationally observed: two pilots with identical 92% raw agreement yielded κ = 0.79 and κ = 0.72 purely because the second sample was more EXCLUDE-dominated. Therefore:

1. **Always report the triple:** κ **and** raw % agreement **and** PABAK (prevalence-adjusted bias-adjusted kappa: binary `2·Pₒ − 1`; k-category `(k·Pₒ − 1)/(k − 1)`), in **both** the 3-category (INCLUDE/EXCLUDE/UNCERTAIN) and binary retain/discard forms. Never report or gate on κ alone.
2. **Interpret against the sample's prevalence.** A κ drop between pilots/batches with stable % agreement and PABAK usually reflects composition, not degraded screening. A drop in all three reflects real disagreement.
3. **The 0.60 gate is a heuristic**, read alongside % agreement, PABAK, and — most importantly — **the direction of disagreements**: AI-discard/human-retain disagreements (missed includes) are the dangerous ones and warrant rule extraction and action **even when κ is acceptable**.
4. Log the full 2×2 (and 3×3) agreement tables, not just the summary statistics, so the direction is always inspectable.

*(Internal design guidance: PABAK is used as a standard descriptive adjustment; no new external standard is being invoked.)*

#### Active Learning — Prompt Calibration Protocol

**Purpose:** As the human audits the AI's screening decisions, systematic error patterns emerge — the AI may consistently misjudge certain study types, populations, or interventions. This protocol uses the human's corrections as few-shot calibration examples to improve the screening prompt for subsequent batches. This is in-context learning (not fine-tuning): the model itself does not change, but the prompt is enriched with real examples from this review, making the AI's recommendations progressively closer to the researcher's ground truth.

**When it triggers:** After each completed batch cycle — specifically, after (a) the AI screens a batch, (b) the 20% ground-truth validation is computed, AND (c) the human audit of the batch is complete. The protocol runs before the next batch is screened. (Batch 1 of the full screen already carries the calibration examples and eligibility rules produced by the Phase 5a pilots; this protocol continues refining them, subject to the post-lock deviation rule below.) Note the monitoring cadence (every 50 records) is independent of the execution batch size (default 250): a 250-record execution batch contains five 50-record monitoring checks.

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
    "phase": "5a | 5 | 7 | 8",
    "gate": "string — which gate's audit produced the correction data, e.g., 'Gate 2a', 'Gate 2', or 'Gate 4'",
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

**Registry connection:** Where a correction generalises to an operational rule (not just an exemplar), it is also written to the **eligibility-rules registry** (Phase 5a) through the same approval flow, with the rule's `origin` pointing at the triggering records. Because the criteria were **locked at Gate 2a**, any post-lock rule addition or modification is a logged protocol deviation: present the trade-off (including whether already-screened batches should be re-screened under the amended rules) and log the researcher's decision.

**Reproducibility note:** Adding calibration examples changes the prompt, which changes what is asked of the model for records screened under the new prompt. This is by design — the prompt improvement is measured and documented. The audit log records which prompt version was used for each screening call (via `prompt_version_hash`), so any output can be traced to its exact prompt and to the logged model version. Per the Reproducibility Statement, this versioning-and-logging — not seed determinism — is the basis of the review's reproducibility.

**Guardrail: Maximum prompt growth.** The calibration block must not exceed 5 examples. If a 6th example is warranted, it must replace the least informative existing example (lowest hit rate over the last two batches). This prevents unbounded prompt growth that could degrade model performance by consuming context window space needed for the abstract itself.

### ── GATE 2: Human Audit of Title-Abstract Screening (100% by default) ──

**MANDATORY. No AI recommendation becomes a decision without human confirmation.** The default and gold standard is a 100% audit of every record; the opt-in risk-based alternative below changes only *which* records the researcher personally audits — every final decision remains a human decision (directly, or via the dual-screening and adjudication of Phase 5b).

Per the pacing chosen at kickoff (stage-and-audit per batch, or one consolidated pass after all batches), present the audited records to the researcher (Reviewer A) with the AI's recommendation, reasoning, and evidence:

```
RECORD: {record_id} — {title}
AI RECOMMENDATION: [INCLUDE / EXCLUDE / UNCERTAIN]
AI EXCLUSION REASON: [category or N/A]
AI CONFIDENCE: [High / Medium / Low]
AI REASONING: [one-sentence summary]

YOUR DECISION: [ ] AGREE  [ ] OVERRIDE → [INCLUDE / EXCLUDE]
OVERRIDE REASON (if applicable): _______________
```

**Workflow (100% audit — the default and gold standard):**
1. Present records in audit batches (batch size configurable by researcher; default 25, `audit_batch_size`), using the per-batch **worksheet CSVs** generated by the Screening at Scale protocol so the researcher can audit in a spreadsheet if preferred.
2. **Audit-priority ordering** within and across worksheets: **UNCERTAIN first → then INCLUDE → then EXCLUDE by ascending confidence** (Low-confidence excludes before High-confidence excludes). This puts the decisions most likely to matter — and most likely to hide missed includes — at the front of the researcher's attention.
3. For each record, the researcher must select AGREE or OVERRIDE.
4. If OVERRIDE, the researcher must provide a reason.
5. Log every decision with `created_at` timestamp, keyed by stable record ID.
6. Pilot records audited in Phase 5a are already human-decided and are not re-presented.

**Risk-based audit (opt-in alternative at large N — documented as a limitation, never the silent default):**

At large N, a strict 100% human audit of title-abstract decisions can be practically prohibitive. If — and only if — the researcher explicitly opts in (kickoff checklist item 10, confirmable here), a **risk-based audit** may substitute at Gate 2:

- **100% human audit is retained for:** all UNCERTAIN records, all INCLUDE recommendations, and all Low-confidence EXCLUDEs.
- **A random sample (researcher-set, default 20%, seeded and therefore reproducible) is audited from:** Medium/High-confidence EXCLUDEs.
- **Escalation rule:** if the sampled audit of any stratum finds a missed include (human overrides EXCLUDE → INCLUDE), the audit of that stratum escalates — double the sample; a second missed include escalates to 100% audit of that stratum.
- **The trade-off, stated plainly to the researcher before they opt in:** *"The Cochrane Handbook's standard is independent duplicate screening of all records; auditing a sample of high-confidence exclusions means some AI exclusion decisions receive dual human scrutiny only via Reviewer B (Phase 5b) rather than via your audit. This is a documented limitation of the review and will be reported as such (methods, AI Transparency Statement, and AMSTAR-2 self-assessment). The empirical justification is the screening performance validated in the Phase 5a pilots and monitored per batch — if that monitoring degrades, the audit escalates."*
- Log the opt-in, the sampling scheme and seed, all escalations, and include the limitation text in Phase 10 exports.

**Do not proceed to Phase 5b until Gate 2 (in the chosen, logged mode) is complete and logged.**

---

## Phase 5b: Independent Dual Screening & Conflict Resolution

### Rationale

Cochrane Handbook v6.5 (Chapter 4) requires independent duplicate screening to minimise selection bias. A single reviewer (even with AI assistance) does not meet this standard. Phase 5b implements a second independent screening pass.

### Instructions

1. **Reviewer B** must screen the same records independently. Reviewer B can be:
   - A second human reviewer (preferred for Cochrane compliance).
   - A second blinded AI pass with a **different prompt variant** — and, where available, a different model version (acceptable for non-Cochrane reviews, but must be documented as a limitation). Per the Reproducibility Statement, merely changing the seed does not create a meaningfully independent second reviewer for agentic screening; independence comes from a genuinely different prompt formulation and/or model, both logged.

2. **Reviewer B does not see Reviewer A's decisions.** Present records to Reviewer B in the same format as the ground-truth validation (no AI recommendation shown if Reviewer B is human; if Reviewer B is a second AI pass, use the documented different prompt variant/model, blind to Reviewer A's outputs).

3. **Conflict identification:** After both reviewers have completed screening, identify all records where Reviewer A and Reviewer B disagree.

4. **Conflict resolution:** Present each conflict to a third-party adjudicator (the principal investigator, or a designated senior reviewer):
   > "**Conflict — Record {record_id}:**
   > Title: {title}
   > Reviewer A decision: [INCLUDE / EXCLUDE] — Reason: [...]
   > Reviewer B decision: [INCLUDE / EXCLUDE] — Reason: [...]
   >
   > Please adjudicate: [INCLUDE / EXCLUDE]
   > Reason: _______________"

5. **Compute inter-rater reliability** per the κ Interpretation Guidance (Phase 5):
   - **Cohen's Kappa** (binary retain/discard, and 3-category where both reviewers used UNCERTAIN).
   - **Percentage agreement.**
   - **PABAK.**
   - Report and log all metrics plus the agreement table, and interpret κ against the sample's prevalence (kappa paradox), not in isolation.
   - If Kappa < 0.60, flag as `LOW_AGREEMENT_ALERT` and recommend reviewing the eligibility criteria and rules registry for ambiguity — attending first to the direction of disagreements (discard/retain conflicts).

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

1. Use the same structured screening prompt as Phase 5, adapted for full-text input. Include all criteria with the same N/A handling, and include the locked `{ELIGIBILITY_RULES_BLOCK}` — the registry applies at full text too (several rule categories, e.g., UNCERTAIN-deferral rules, are *resolved* here).
2. Apply the same `temperature=0`. Hash all responses; log `prompt_version_hash` and `model_id_used` per decision (the Reproducibility Statement applies here identically).
3. Apply the same **Screening at Scale execution protocol** as Phase 5 — stable IDs, batching (smaller default batches are sensible given full-text length; confirm with the researcher), append-only checkpointed decisions files, resume-after-interruption, and upfront throughput expectations. Full-text reading per record is slower than abstract reading; estimate accordingly.
4. Apply the same performance monitoring system as Phase 5 (drift detection, 20% ground-truth validation, full metrics, κ Interpretation Guidance).
5. Apply the same **Active Learning — Prompt Calibration Protocol** as Phase 5. Start with a fresh set of calibration *examples* (no carry-over from title-abstract screening), since full-text screening involves different evidence and different error patterns; the eligibility-rules *registry* carries over unchanged (post-lock changes remain logged deviations).
6. Apply the same dual screening protocol as Phase 5b (Reviewer A + Reviewer B + conflict resolution + the κ triple).

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

For each included study (after Gate 3), apply the parsed RoB framework using structured prompting at `temperature=0`. Hash all responses and log `prompt_version_hash` and `model_id_used` per assessment (the Reproducibility Statement applies here identically).

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

**Update mode — use the PRISMA 2020 layout for updated reviews.** PRISMA 2020 provides flow-diagram templates that distinguish studies from the previous version of the review from those newly identified. The update diagram must book-keep, from the Phase 3/4/4b logs:

- **Previous review column:** studies included in the previous version of the review (from the prior corpus decisions), reports of those studies.
- **New search column — Identification:** records identified in the new (date-restricted) search, per database, using the **exported** counts with the hit-count/export-count deltas noted (Phase 3 Export Integrity Check).
- **Duplicates removed** within the new retrieval (Phase 4).
- **Records already present in the prior review's corpus, removed before screening** (Phase 4b) — reported as its own line so the update's screening workload is transparent; carried-forward decisions are noted here.
- **New records screened / excluded / sought / assessed / included**, as in the standard flow (Phases 5–7), including pilot-screened records (their human decisions are final decisions and are counted in the screened totals).
- **Total studies included in the updated review** = prior included studies (± any removed by amendment, each logged) + newly included studies.

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
├── eligibility_rules_registry.json
├── screening_pilots/
│   ├── pilot_reports.md            ← per-pilot composition, κ + % agreement + PABAK, disagreement tables
│   └── criteria_lock_record.md     ← locked prompt_version_hash, Gate 2a confirmation
├── screening_results/
│   ├── title_abstract_screening.csv
│   ├── full_text_screening.csv
│   ├── dual_screening_conflicts.csv
│   └── audit_mode_statement.md     ← 100% or risk-based (with sampling scheme, escalations, limitation text)
├── update_review/                   ← update mode only
│   ├── prior_corpus_dedup_report.md
│   └── carried_forward_decisions.csv
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
│   ├── cohens_kappa_title_abstract.md   ← κ + % agreement + PABAK + tables
│   └── cohens_kappa_full_text.md        ← κ + % agreement + PABAK + tables
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

**`performance_monitoring_report.md`** summarises: all alerts, drift events, AI-human agreement rates, ground-truth performance metrics, inter-rater reliability (Cohen's κ + % agreement + PABAK, per the κ Interpretation Guidance), pilot-phase metrics and the criteria-lock record, override patterns, calibration effectiveness (per-batch accuracy trends, lesson hit rates, calibration regression events), calibration warnings, and the model id/version used per batch.

**`audit_chain_verification.py`** — provide with full beginner-friendly run instructions.

---

## Design Principles

1. **The human decides; the AI recommends.** Every inclusion, exclusion, and risk-of-bias judgment is a recommendation until the researcher confirms it.

2. **Independent dual screening.** Two independent reviewers (human and/or AI) screen all records, with conflict resolution by a third-party adjudicator. This meets the Cochrane Handbook v6.5 requirement for independent duplicate screening.

3. **Reproducibility through versioning and complete logging.** Temperature=0 minimises variability; reproducibility itself comes from versioned, hashed prompts and criteria, fully logged per-record inputs/outputs/rationales, deterministic seeded sampling, per-batch model-version logging, and SHA-256 audit chaining — not from claimed seed-level determinism of agentic reasoning (see the Reproducibility Statement).

4. **Transparency through structured logging and AI disclosure.** Every decision is logged with structured rationales (not raw CoT). The AI Transparency Block documents the AI's role, limitations, and configuration per PRISMA-trAIce and RAISE guidance.

5. **Performance monitoring with active notification.** Drift detection, ground-truth validation with full metrics, threshold alerts, and active learning calibration surface and correct problems in real time.

6. **PRISMA compliance by construction.** The flow diagram is generated from actual audit data, then verified and finalised by the researcher.

7. **Accessible to non-coders.** Every script comes with step-by-step setup instructions. No prior Python experience is assumed.

8. **Plan first, then act.** For any non-standard database or novel procedure, the skill creates a plan, presents it for approval, and only executes after confirmation.

9. **No fabricated references.** Every guideline, framework, and publication cited in this skill has been individually verified. URLs are provided where available but may change — always verify by searching for the framework by name.

10. **Active learning from human corrections.** The AI's screening and assessment prompts are progressively calibrated using real override examples from the researcher's audit. Each calibration is logged, version-hashed, researcher-approved, and measured for effectiveness. The model itself does not change — only the prompt is enriched with few-shot examples and researcher-approved eligibility rules, every version of which is hashed so any decision is traceable to the exact instructions in force.

11. **Updates are first-class.** An update review reuses the prior protocol and search strings verbatim (date-restricted), dedups against the prior corpus with carried-forward decisions, and reports with the PRISMA update layout — none of it improvised.

12. **Pilot before scale.** No full screen begins until stratified calibration pilots with blind 100% human audit pass the κ gate (reported as κ + % agreement + PABAK, with disagreement direction) and the criteria — including the eligibility-rules registry — are locked at Gate 2a.

13. **Honest about cost and about determinism.** Screening at genuine reading depth is the dominant cost of the review: the researcher gets an upfront records→batches→sessions estimate and chooses the pacing, and progress is checkpointed so it survives interruption. Reproducibility claims never exceed what the logging actually guarantees.
