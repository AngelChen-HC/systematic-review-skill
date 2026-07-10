# Migration Note — reviews mid-flight on v7.0 → v8.0

**Governing rule (now codified in v8, "Upgrading Mid-Review"):** an in-flight,
human-audited screen **stays on the version it began under**. Adopt v8
capabilities only at clean phase or batch boundaries. On upgrade, log one
`skill_version_customisation` audit entry stating which phases run under which
version and why — this preserves the hash chain of the in-flight work.

## What carries forward unchanged
- **Audit log & hash chain.** v8 adds optional entry fields
  (`local_model_id_used`, `adapter_version_used`) and new action names; it
  changes nothing about existing entries. Do **not** rewrite
  `schema_version` in an existing log — keep appending; new fields appear
  only on new entries. The chain verifier runs unchanged.
- **Locked criteria, prompts, registries, hashes.** Gate 2a/3b/3c/3d locks,
  the eligibility-rules registry, the extraction-conventions registry, and
  every `prompt_version_hash` are untouched. No decision is re-opened.
- **Screening progress.** Batches, checkpoints, worksheets, dual-screening
  records: all valid as-is.

## What v8 adds, and when it first applies to you
- **Phase 5c (learned alignment): adapters start cold.** No pre-trained
  artifact ships and none is implied. If you opt in (kickoff item 14,
  retro-answerable at the next batch boundary), the first training set is
  built from the audited decisions you already have — once the floors
  (≥100 eligible records, ≥8 retain-class) are met.
- **Your promotion test set already exists.** Ground-truth validation
  records accumulated so far become the initial held-out set:
  `build_training_set.py` derives the exclusion manifest retroactively and
  deterministically from `audit_log.json` (action names containing
  `ground_truth`). Nothing to re-screen; nothing to re-label.
- **No re-screening obligation is created.** v8 changes no eligibility
  semantics. Step 2.3d (benchmark retrieval validation) applies to searches
  you run from now on (for updates: the optional regression variant, next
  time strings are executed). Per-batch agreement metrics
  (`batch_agreement_metrics`) start with your next audited batch. The
  rendered rulebook (`screening_criteria_locked.md`) is emitted at the next
  lock/deviation event, or on request. Boundary-policy templates (5a.6)
  apply to future pilots; already-locked criteria stay locked.
- **AI Transparency Block: amend forward.** Add the `learned_alignment`
  section ("not used", or the per-batch triple once used). The v7 line
  "model not fine-tuned" is replaced from your next generated statement
  onward; historical statements are historical.
- **Gate count.** Still 13 mandatory gates. Two conditional gates now exist:
  **Gate 2c** (the informed fine-tuning decision — fires only when the
  Phase 5c plateau trigger fires, the data floors are first met with a
  deferred kickoff answer, or you raise the question yourself) and
  **Gate 5c** (adapter promotion — exists only once something is trained).
  For a mid-flight review, nothing fires until one of those conditions is
  met; if Gate 2c does fire, you will see the full time / API-cost /
  research-data / efficiency / effectiveness notice with the drawbacks of
  both options, and **opting out is a first-class, logged, fully valid
  outcome** that mechanically blocks the training scripts and is only
  re-presented on a fresh trigger or your own request.

## One-time actions at upgrade (5 minutes)
1. Append the `skill_version_customisation` entry (which phases on v7 vs v8).
2. Copy `scripts/` (incl. `srlib/`, `requirements-finetune.txt`,
   `configs/adapter_training.example.json`) into your working directory.
3. If opting into Phase 5c later: nothing else now — the plateau trigger is
   computed from the per-batch metrics that begin at your next audited batch.
