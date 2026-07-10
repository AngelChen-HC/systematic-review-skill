#!/usr/bin/env python3
"""evaluate_adapter.py — Phase 5c, Step 5c.3 (SKILL.md v8.0).

Evaluates a CANDIDATE adapter against the INCUMBENT (the active adapter, or
the prompt-only local baseline) on the held-out, NEVER-TRAINED ground-truth
set, and applies the recall-safe promotion gate:
  PASS iff  binary retain/discard sensitivity ≥ max(incumbent, floor 0.95)
       AND  specificity ≥ incumbent − 0.05
       AND  parse-failure rate ≤ 2%.
Reports the full Phase 5a metric discipline (κ ×2, % agreement ×2, PABAK ×2,
confusion + directional tables — model-discard/human-retain is the dangerous
cell), Wilson 95% CIs, and a paired check honest about n: exact McNemar on
discordant pairs at pilot scale; seeded bootstrap CI otherwise, caveat stated.
Every statistic is computed by this code — never by any language model.
Emits promotion_reports/<version>_promotion_report.md (+ .json) and an audit
entry (action: adapter_evaluation). It NEVER promotes: see promote_adapter.py.

HOW TO RUN (no coding experience needed)
  python3 scripts/evaluate_adapter.py --config learned_alignment/adapter_training.json \
      --candidate v1.0.0 --holdout learned_alignment/holdout_ground_truth.csv
  (holdout CSV: record_id,title,abstract,human_decision — the ground-truth
   validation records; the script refuses any record found in training.)
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from srlib import audit, data, metrics, modeling  # noqa: E402


def run_model(la, cfg, adapter_version, rows, criteria_block, rules_block):
    adapter_dir = None
    if adapter_version and adapter_version != "prompt-only":
        adapter_dir = os.path.join("learned_alignment", "adapters", adapter_version)
    model, tok, resolved = modeling.load_with_adapter(
        la["base_model_id"], la.get("base_model_revision"), adapter_dir,
        la.get("quantization", "none"))
    preds, fails = [], 0
    for r in rows:
        prompt = (data.SYSTEM_SCREEN + "\n\n" + data.render_record_prompt(
            r, criteria_block, rules_block))
        raw = modeling.generate_greedy(model, tok, prompt)
        s, e = raw.find("{"), raw.rfind("}")
        dec = None
        if s != -1 and e > s:
            try:
                dec = json.loads(raw[s:e + 1]).get("decision")
            except json.JSONDecodeError:
                dec = None
        if dec not in data.DECISIONS:
            dec, fails = "UNCERTAIN", fails + 1  # fail-safe = retain + flagged
        preds.append(dec)
    del model
    return preds, fails, resolved


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--candidate", required=True, help="adapter version, e.g. v1.0.0")
    ap.add_argument("--holdout", required=True, help="ground-truth CSV (see --help)")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    la = cfg["learned_alignment"]
    seed = int(la["seed"])
    modeling.set_all_seeds(seed)
    gate = la.get("promotion_gate", {})
    floor = float(gate.get("sensitivity_floor", 0.95))
    spec_tol = float(gate.get("max_specificity_drop", 0.05))

    rows = list(csv.DictReader(open(args.holdout, newline="", encoding="utf-8")))
    y_true = [r["human_decision"].strip().upper() for r in rows]
    ids = [r["record_id"] for r in rows]

    # Leakage guard: holdout ∩ training manifest must be empty.
    ts_dir = la.get("training_set_dir", "learned_alignment/training_runs/current")
    card = json.load(open(os.path.join(ts_dir, "dataset_card.json"), encoding="utf-8"))
    data.assert_no_overlap(card["record_id_manifest"], set(ids))

    criteria_block = open(cfg["criteria_block_path"], encoding="utf-8").read() \
        if cfg.get("criteria_block_path") else cfg.get("criteria_block_text", "")
    rules_block = open(cfg["rules_block_path"], encoding="utf-8").read() \
        if cfg.get("rules_block_path") else cfg.get("rules_block_text", "")

    incumbent = la.get("active_adapter", "prompt-only") or "prompt-only"
    ptr = os.path.join("learned_alignment", "active_adapter.json")
    if os.path.exists(ptr):
        incumbent = json.load(open(ptr, encoding="utf-8")).get("active", incumbent)
    print(f"Incumbent: {incumbent}   Candidate: {args.candidate}   n={len(rows)}")

    pred_inc, fail_inc, _ = run_model(la, cfg, incumbent, rows,
                                      criteria_block, rules_block)
    pred_cand, fail_cand, resolved = run_model(la, cfg, args.candidate, rows,
                                               criteria_block, rules_block)

    pan_inc = metrics.full_panel(y_true, pred_inc)
    pan_cand = metrics.full_panel(y_true, pred_cand)
    pf_rate = fail_cand / len(rows) if rows else 0.0

    # Paired comparison on human-RETAIN records (sensitivity is the gate).
    tb = [metrics.to_retain(t) for t in y_true]
    ok_inc = [1 if (tb[i] == "RETAIN" and metrics.to_retain(pred_inc[i]) == "RETAIN")
              else 0 for i in range(len(rows))]
    ok_cand = [1 if (tb[i] == "RETAIN" and metrics.to_retain(pred_cand[i]) == "RETAIN")
               else 0 for i in range(len(rows))]
    mask = [1 if t == "RETAIN" else 0 for t in tb]
    b = sum(1 for i, m in enumerate(mask) if m and ok_inc[i] and not ok_cand[i])
    c = sum(1 for i, m in enumerate(mask) if m and not ok_inc[i] and ok_cand[i])
    n_retain = sum(mask)
    if len(rows) <= 100:
        sig = {"method": "exact McNemar (discordant pairs, binomial p=0.5)",
               "b_incumbent_only_correct": b, "c_candidate_only_correct": c,
               "p_two_sided": metrics.mcnemar_exact(b, c),
               "caveat": f"pilot-scale n ({n_retain} human-retain records); "
                         "exact test used; treat as descriptive"}
    else:
        lo, hi = metrics.bootstrap_diff_ci(ok_inc, ok_cand, mask, seed)
        sig = {"method": "seeded paired bootstrap (2000 reps) on Δsensitivity",
               "ci95": [lo, hi], "seed": seed,
               "caveat": "bootstrap CI is descriptive; small strata remain "
                         "imprecise even at this n"}

    sens_c, spec_c = pan_cand["sensitivity"], pan_cand["specificity"]
    sens_i, spec_i = pan_inc["sensitivity"], pan_inc["specificity"]
    checks = {
        "sensitivity_vs_floor": sens_c >= floor,
        "sensitivity_vs_incumbent": sens_c >= sens_i,
        "specificity_within_tolerance": spec_c >= spec_i - spec_tol,
        "parse_failure_rate_ok": pf_rate <= 0.02,
    }
    verdict = "PASS" if all(checks.values()) else "FAIL"
    small_n_note = ""
    if n_retain and n_retain < 20:
        small_n_note = (f"SMALL-n HONESTY: only {n_retain} human-retain records "
                        f"in the holdout — one missed include drops sensitivity "
                        f"to {(n_retain-1)/n_retain:.3f}, so the 0.95 floor here "
                        "operationally means ZERO missed includes. Read the "
                        "Wilson CI, not the point estimate. Gate 5c researcher "
                        "confirmation is required regardless of PASS.")

    man_path = os.path.join("learned_alignment", "adapters", args.candidate,
                            "MANIFEST.json")
    manifest = json.load(open(man_path, encoding="utf-8"))
    report = {"candidate": args.candidate,
              "candidate_weights_sha256": manifest["weights_sha256"],
              "incumbent": incumbent, "holdout_n": len(rows),
              "holdout_sha256": audit.sha256_file(args.holdout),
              "gate": {"sensitivity_floor": floor,
                       "max_specificity_drop": spec_tol,
                       "checks": checks, "verdict": verdict},
              "candidate_panel": pan_cand, "incumbent_panel": pan_inc,
              "candidate_parse_failure_rate": pf_rate,
              "paired_significance": sig, "small_n_note": small_n_note,
              "leakage_check": "PASS — holdout ∩ training manifest = ∅"}

    os.makedirs(os.path.join("learned_alignment", "promotion_reports"), exist_ok=True)
    jpath = os.path.join("learned_alignment", "promotion_reports",
                         f"{args.candidate}_promotion_report.json")
    json.dump(report, open(jpath, "w", encoding="utf-8"), indent=2)

    def fmt(p):
        return (f"| κ 3-cat {p['kappa_3cat']:.3f} | κ binary {p['kappa_binary']:.3f} "
                f"| %agr 3-cat {p['pct_agreement_3cat']:.3f} | %agr bin "
                f"{p['pct_agreement_binary']:.3f} | PABAK 3-cat {p['pabak_3cat']:.3f} "
                f"| PABAK bin {p['pabak_binary']:.3f} |\n"
                f"sensitivity {p['sensitivity']:.3f} (Wilson95 "
                f"{p['sensitivity_wilson95'][0]:.3f}–{p['sensitivity_wilson95'][1]:.3f}), "
                f"specificity {p['specificity']:.3f} (Wilson95 "
                f"{p['specificity_wilson95'][0]:.3f}–{p['specificity_wilson95'][1]:.3f})\n"
                f"directional: {json.dumps(p['directional'])}\n"
                f"confusion 3-cat (rows=human, cols=model, order "
                f"INCLUDE/EXCLUDE/UNCERTAIN): {p['confusion_3cat']}\n")

    mpath = jpath.replace(".json", ".md")
    with open(mpath, "w", encoding="utf-8") as f:
        f.write(f"# Promotion report — candidate {args.candidate}\n\n"
                f"**Verdict: {verdict}** (gate: sens ≥ max(incumbent, {floor}); "
                f"spec ≥ incumbent − {spec_tol}; parse-fail ≤ 2%)\n\n"
                f"Holdout: n={len(rows)} never-trained ground-truth records "
                f"(leakage check PASS).\n\n## Candidate ({args.candidate})\n"
                + fmt(pan_cand) +
                f"\nparse-failure rate: {pf_rate:.3f}\n\n## Incumbent ({incumbent})\n"
                + fmt(pan_inc) +
                f"\n## Paired check\n{json.dumps(sig, indent=2)}\n\n{small_n_note}\n\n"
                "All statistics computed by evaluate_adapter.py "
                "(srlib.metrics, stdlib) — never by a language model.\n")

    audit.append_entry(cfg["audit_log_path"], phase="5c",
                       action="adapter_evaluation", actor="SYSTEM",
                       adapter_version_used=args.candidate,
                       output={"verdict": verdict, "report_sha256":
                               audit.sha256_file(jpath), "report_path": jpath,
                               "gate_checks": checks,
                               "candidate_sensitivity": sens_c,
                               "incumbent_sensitivity": sens_i})
    print(open(mpath, encoding="utf-8").read())
    print(f"Report written: {mpath}\nVerdict: {verdict} — promotion still "
          "requires Gate 5c researcher confirmation (promote_adapter.py).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
