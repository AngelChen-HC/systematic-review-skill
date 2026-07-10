#!/usr/bin/env python3
"""promote_adapter.py — Phase 5c, GATE 5c (SKILL.md v8.0).

Activates a candidate adapter ONLY IF (a) its promotion report verdict is
PASS and (b) the researcher types an explicit confirmation here (Gate 5c).
Automatic promotion never happens. Also provides rollback:
  --rollback            revert to the previously promoted adapter/prompt-only
                        (researcher-initiated)
  --auto-rollback --trigger "SENSITIVITY_ALERT batch 9"
                        the conservative automatic path invoked by drift
                        monitoring; logs ADAPTER_AUTO_ROLLBACK and notifies.
Rollback needs no gate because it only returns to a previously human-approved
state (or prompt-only); re-promotion always requires a fresh Gate 5c.

HOW TO RUN (no coding experience needed)
  python3 scripts/promote_adapter.py --config learned_alignment/adapter_training.json \
      --candidate v1.0.0 --reviewer-id "HC"
Expected: the script shows the gate verdict, asks you to type
PROMOTE v1.0.0 exactly, then prints "Gate 5c logged. Active adapter: v1.0.0".
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from srlib import audit  # noqa: E402

PTR = os.path.join("learned_alignment", "active_adapter.json")


def read_ptr():
    if os.path.exists(PTR):
        return json.load(open(PTR, encoding="utf-8"))
    return {"active": "prompt-only", "history": []}


def write_ptr(state):
    os.makedirs(os.path.dirname(PTR), exist_ok=True)
    json.dump(state, open(PTR, "w", encoding="utf-8"), indent=2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--candidate", help="adapter version to promote")
    ap.add_argument("--reviewer-id", default=None)
    ap.add_argument("--rollback", action="store_true")
    ap.add_argument("--auto-rollback", action="store_true",
                    help="drift-monitor path (conservative, logged, notifies)")
    ap.add_argument("--trigger", default=None,
                    help="with --auto-rollback: the alert that fired")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    state = read_ptr()

    if args.rollback or args.auto_rollback:
        prev = state["history"][-1]["previous"] if state["history"] else "prompt-only"
        old = state["active"]
        state["history"].append({"event": "AUTO_ROLLBACK" if args.auto_rollback
                                 else "ROLLBACK", "from": old, "to": prev,
                                 "trigger": args.trigger,
                                 "at": audit.now_iso()})
        state["active"] = prev
        write_ptr(state)
        audit.append_entry(cfg["audit_log_path"], phase="5c",
                           action=("ADAPTER_AUTO_ROLLBACK" if args.auto_rollback
                                   else "adapter_rollback"),
                           actor="SYSTEM",
                           adapter_version_used=prev,
                           output={"rolled_back_from": old, "now_active": prev,
                                   "trigger": args.trigger,
                                   "note": "conservative reversion to a "
                                           "previously human-approved state; "
                                           "re-promotion requires a fresh "
                                           "Gate 5c"})
        print(f"Rolled back: {old} → {prev}. NOTIFY THE RESEARCHER "
              f"(trigger: {args.trigger}). Re-promotion requires Gate 5c.")
        return 0

    if not args.candidate or not args.reviewer_id:
        ap.error("--candidate and --reviewer-id are required for promotion")

    rpath = os.path.join("learned_alignment", "promotion_reports",
                         f"{args.candidate}_promotion_report.json")
    if not os.path.exists(rpath):
        raise SystemExit(f"No promotion report at {rpath}. Run "
                         "evaluate_adapter.py first — promotion without the "
                         "recall-safe gate is forbidden.")
    report = json.load(open(rpath, encoding="utf-8"))
    verdict = report["gate"]["verdict"]
    print(f"Gate verdict for {args.candidate}: {verdict}")
    print(json.dumps(report["gate"]["checks"], indent=2))
    if report.get("small_n_note"):
        print("\n" + report["small_n_note"])
    if verdict != "PASS":
        man = os.path.join("learned_alignment", "adapters", args.candidate)
        arch = os.path.join("learned_alignment", "adapters", "archived")
        os.makedirs(arch, exist_ok=True)
        dest = os.path.join(arch, args.candidate)
        if os.path.exists(man) and not os.path.exists(dest):
            os.rename(man, dest)
        audit.append_entry(cfg["audit_log_path"], phase="5c",
                           action="adapter_promotion", actor="SYSTEM",
                           adapter_version_used=args.candidate,
                           output={"result": "REJECTED_BY_GATE",
                                   "archived_to": dest,
                                   "report_sha256": audit.sha256_file(rpath)})
        print(f"FAILED the recall-safe gate → archived to {dest}. "
              "Failed adapters are never deployed.")
        return 1

    expected = f"PROMOTE {args.candidate}"
    print(f"\nGATE 5c — researcher confirmation required.\nType exactly: {expected}")
    typed = input("> ").strip()
    if typed != expected:
        print("Confirmation not given. Nothing promoted.")
        return 1

    old = state["active"]
    state["history"].append({"event": "PROMOTION", "previous": old,
                             "to": args.candidate,
                             "reviewer_id": args.reviewer_id,
                             "at": audit.now_iso()})
    state["active"] = args.candidate
    write_ptr(state)
    audit.append_entry(cfg["audit_log_path"], phase="5c",
                       action="adapter_promotion", actor="HUMAN",
                       adapter_version_used=args.candidate,
                       output={"result": "PROMOTED", "previous_active": old,
                               "report_sha256": audit.sha256_file(rpath),
                               "report_path": rpath,
                               "weights_sha256":
                                   report["candidate_weights_sha256"]},
                       human_review={"reviewed": True,
                                     "reviewer_id": args.reviewer_id,
                                     "agreed_with_ai": None,
                                     "override_reason": None,
                                     "reviewed_at": audit.now_iso()})
    print(f"Gate 5c logged. Active adapter: {args.candidate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
