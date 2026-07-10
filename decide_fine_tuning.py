#!/usr/bin/env python3
"""decide_fine_tuning.py — Phase 5c, GATE 2c (SKILL.md v8.0).

Presents the full informed-choice notice (time, API/compute cost, research
data, efficiency, effectiveness, drawbacks of BOTH options, reversibility)
and records the researcher's typed OPT-IN or OPT-OUT as a hash-chained audit
entry (action: fine_tuning_decision). No Phase 5c training step will run —
build_training_set.py and train_adapter.py both check — unless the most
recent decision here is an OPT_IN. An opt-out is a first-class, fully valid,
logged outcome; it is re-presented only on a fresh plateau trigger or your
explicit request, never nagged.

HOW TO RUN (no coding experience needed)
  python3 scripts/decide_fine_tuning.py --config learned_alignment/adapter_training.json \
      --reviewer-id "HC" --context plateau_trigger
Read the notice, then type exactly OPT-IN or OPT-OUT when asked.
Add --show-notice to print the notice and exit without deciding.
Non-interactive (e.g., logging a kickoff decision):
  ... --decision opt-out --ack "I have read the Gate 2c notice in full"
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from srlib import audit  # noqa: E402

ACK_PHRASE = "I have read the Gate 2c notice in full"

NOTICE = """
================================ GATE 2c NOTICE =================================
FINE-TUNING DECISION — read both columns before choosing. Base model: {base}
(quantization: {quant}). Reviewer B mode on record: {revb}.

1. TIME
   Opt-in : one-time model download ~{dl}; each training cycle ~{train_t}
            (typically 1-3 cycles per review); holdout evaluation minutes (GPU)
            to 1-2 h (CPU); your time ~10 min now + 15-30 min per Gate 5c
            promotion review.
   Opt-out: zero additional time.

2. API AND COMPUTE COST
   The local screener trains and runs ON YOUR MACHINE: no per-token API fees
   for it — its costs are disk (~{dl}), compute time, and electricity.
   Orchestrator API usage for the authoritative screen is UNCHANGED either
   way: the adapter never replaces per-record reading.
   Where it can change: if Reviewer B is a second orchestrator AI pass,
   opting in moves that entire pass (one full read of every dual-screened
   record) off the API onto your machine; if Reviewer B is a second human,
   expect no API-cost difference. No currency figures are quoted — provider
   pricing varies; the honest unit is passes-over-your-records.

3. YOUR RESEARCH DATA
   Training uses ONLY this review's own audited decisions, read locally from
   audit_log.json. Nothing is uploaded anywhere (the base model is
   downloaded, not the reverse). Ground-truth validation records are NEVER
   trained on (manifest-enforced; violations abort the run).
   Two governance flags if you opt in: (a) titles/abstracts are embedded in
   local training files and can, at small scale, be memorised into adapter
   weights — relevant only if you later share the adapter (already flagged
   non-transferable; database licence terms may also restrict redistributing
   abstracts); (b) training sets, adapters and reports are added to your
   working directory and export package.

4. EFFICIENCY
   Opt-in may gain: a calibrated second reviewer at zero marginal API cost;
   faster Reviewer-B throughput at large N; a labelled triage aid; possibly
   a lower override workload for the remaining batches — ONLY if a candidate
   passes the promotion gate.
   Opt-in costs: environment setup (Python packages, ~{dl} disk, ideally a
   GPU), training cycles, one more gate to review, ongoing version/rollback
   bookkeeping (automated, but real).
   Opt-out: the prompt-calibration fast path continues unchanged; the
   plateau that raised this question persists — your current override rate,
   and correction effort per batch, stays roughly where it is.

5. EFFECTIVENESS — stated without promises
   No performance gain is claimed in advance (this skill makes no unverified
   performance claims). Effectiveness is measured empirically on YOUR
   never-trained ground-truth records at the recall-safe gate; an adapter
   deploys only if it beats the incumbent there. A real possible outcome is
   that NO candidate ever passes — time spent, nothing deployed. At
   pilot-scale holdouts the gate effectively demands zero missed includes.

6. DRAWBACKS OF OPTING IN
   Correlated-error Reviewer B (weaker error-independence than a second
   human — a documented limitation you must disclose per PRISMA-trAIce/RAISE
   and may need to defend at peer review); risk of overfitting your own
   early errors (controls: 100% audit, never-trained holdout gate, drift
   auto-rollback); bit-identical retraining across hardware is not claimed;
   compute, disk and energy use; added operational complexity.

7. DRAWBACKS OF OPTING OUT
   The systematic error pattern that fired the trigger persists under the
   five-example prompt cap, so your audit burden stays elevated for the
   remaining batches; if Reviewer B is a second orchestrator pass, it keeps
   consuming API tokens; you forgo a possible measured sensitivity/
   specificity gain. What opting out does NOT cost: methodological validity
   — a review without Phase 5c is fully sound, Cochrane compliance is
   unaffected (a second human Reviewer B is in fact the stronger option),
   and no decision already made changes.

8. REVERSIBILITY — both ways
   OPT-IN is reversible at any time (one-command rollback to prompt-only,
   or a later logged opt-out). OPT-OUT is durable but not final: this gate
   is re-presented only on a fresh plateau trigger or your explicit request.
Either decision is logged, hash-chained, and reported in the AI Transparency
Statement — "offered and declined" is a reportable outcome, not a hidden one.
==================================================================================
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--reviewer-id")
    ap.add_argument("--context", choices=["kickoff", "plateau_trigger",
                                          "researcher_request"],
                    default="researcher_request")
    ap.add_argument("--reviewer-b", choices=["second_human", "second_ai_pass",
                                             "undecided"], default="undecided",
                    help="your kickoff item 9 answer, so the cost notice is exact")
    ap.add_argument("--decision", choices=["opt-in", "opt-out"],
                    help="non-interactive mode; requires --ack")
    ap.add_argument("--ack", help=f'non-interactive: must equal "{ACK_PHRASE}"')
    ap.add_argument("--show-notice", action="store_true")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    la = cfg["learned_alignment"]
    base = la.get("base_model_id", "Qwen/Qwen2.5-1.5B-Instruct")
    size = "3 GB" if "1.5B" in base else "6 GB" if "3B" in base else \
           "15 GB" if ("7B" in base or "8B" in base) else "3-15 GB"
    tt = ("2-8 h on CPU" if la.get("quantization", "none") == "none"
          and "1.5B" in base else "5-90 min on a GPU (2-8 h if CPU-only)")
    notice = NOTICE.format(base=base, quant=la.get("quantization", "none"),
                           revb=args.reviewer_b, dl=size, train_t=tt)
    print(notice)
    if args.show_notice:
        return 0
    if not args.reviewer_id:
        ap.error("--reviewer-id is required to record a decision")

    if args.decision:
        if args.ack != ACK_PHRASE:
            raise SystemExit(f'Non-interactive mode requires --ack "{ACK_PHRASE}" '
                             "— the acknowledgement is the point of this gate.")
        decision = "OPT_IN" if args.decision == "opt-in" else "OPT_OUT"
    else:
        typed = input("GATE 2c — type exactly OPT-IN or OPT-OUT: ").strip()
        if typed not in ("OPT-IN", "OPT-OUT"):
            print("No valid decision typed. Nothing recorded.")
            return 1
        decision = typed.replace("-", "_")

    entry = audit.append_entry(
        cfg["audit_log_path"], phase="5c", action="fine_tuning_decision",
        actor="HUMAN", decision=None,
        output={"decision": decision, "context": args.context,
                "reviewer_b_mode": args.reviewer_b,
                "base_model_id": base,
                "disclosure_sha256": audit.sha256_hex(notice.encode("utf-8")),
                "note": ("training authorised until a logged opt-out or "
                         "rollback" if decision == "OPT_IN" else
                         "training blocked; re-present only on a fresh "
                         "plateau trigger or researcher request")},
        human_review={"reviewed": True, "reviewer_id": args.reviewer_id,
                      "agreed_with_ai": None, "override_reason": None,
                      "reviewed_at": audit.now_iso()})
    print(f"Gate 2c logged: {decision} (entry {entry['entry_id'][:8]}…). "
          + ("You may now run build_training_set.py."
             if decision == "OPT_IN" else
             "Fine-tuning stays off; the review continues on the fast path."))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
