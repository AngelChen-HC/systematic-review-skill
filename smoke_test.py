#!/usr/bin/env python3
"""Self-verification smoke test for the v8 Phase 5c scripts (no model needed)."""
import json, os, subprocess, sys, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "tests", "work")
shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from srlib import audit, metrics  # noqa: E402

# ---- 1. metrics sanity (deterministic known values) ----
assert abs(metrics.cohen_kappa(["INCLUDE","EXCLUDE"]*5, ["INCLUDE","EXCLUDE"]*5,
                               metrics.LABELS3) - 1.0) < 1e-9, "kappa perfect != 1"
assert abs(metrics.pabak(["A"]*8+["B"]*2, ["A"]*8+["B"]*2, 2) - 1.0) < 1e-9
p = metrics.mcnemar_exact(1, 5)
assert abs(p - 0.21875) < 1e-9, f"exact McNemar b=1,c=5 expected 0.21875 got {p}"
lo, hi = metrics.wilson_ci(9, 10)
assert 0.55 < lo < 0.72 and 0.97 < hi <= 1.0, f"Wilson CI 9/10 odd: {lo},{hi}"
pan = metrics.full_panel(["INCLUDE","EXCLUDE","UNCERTAIN","EXCLUDE"],
                         ["INCLUDE","EXCLUDE","EXCLUDE","EXCLUDE"])
assert pan["directional"]["model_discard_human_retain__DANGEROUS"] == 1
print("metrics sanity: OK")

# ---- 2. synthetic audit log ----
log = {"schema_version": "8.0", "review_metadata": {},
       "chain_integrity": {"algorithm": "SHA-256",
                           "genesis_hash": audit.sha256_hex(b"GENESIS")},
       "entries": []}
alog = os.path.join(WORK, "audit_log.json")
json.dump(log, open(alog, "w"))

def screen_entry(rid, ai_dec, agree, human_dec=None, reason=None, crit=None):
    audit.append_entry(alog, phase="5a", action="screening_recommendation",
        actor="AI", record_id=rid, decision=ai_dec, model_id_used="orch-x",
        output={"exclusion_reason": "Wrong Outcome" if ai_dec=="EXCLUDE" else None,
                "confidence": "Medium", "human_decision": human_dec,
                "criterion_misjudged": crit},
        human_review={"reviewed": True, "reviewer_id": "HC",
                      "agreed_with_ai": agree, "override_reason": reason,
                      "reviewed_at": audit.now_iso()})
    # patch structured rationale in-place for realism
    l = json.load(open(alog)); l["entries"][-1]["structured_rationale"] = {
        "criteria_assessments": [{"criterion": "Outcome", "evidence": "q",
                                  "assessment": "NOT MET" if ai_dec=="EXCLUDE" else "MET"}],
        "evidence_quotes": ["q"], "decision_rule_applied": "", "summary": "s"}
    # keep chain valid: recompute nothing needed (edit before next append? no —
    # previous hash covers full entry). So rebuild chain:
    prev = l["chain_integrity"]["genesis_hash"]
    for e in l["entries"]:
        e["previous_entry_hash"] = prev
        prev = audit.sha256_obj(e)
    json.dump(l, open(alog, "w"))

for i in range(9):
    screen_entry(f"R-{i:03d}", "EXCLUDE" if i % 3 else "INCLUDE", True)
screen_entry("R-100", "EXCLUDE", False, "INCLUDE", "subscale counts", "Outcome")
screen_entry("R-101", "EXCLUDE", False, "UNCERTAIN", "defer to full text", "Outcome")
screen_entry("R-102", "INCLUDE", False, "EXCLUDE", "wrong population", "Population")
for rid in ("R-900", "R-901", "R-902"):  # ground-truth validation records
    audit.append_entry(alog, phase="5", action="ground_truth_validation",
                       actor="HUMAN", record_id=rid, decision="INCLUDE",
                       output={"human_decision": "INCLUDE"})
assert audit.verify_chain(alog), "chain broken after synthesis"
print("synthetic audit log: OK (chain verifies)")

# ---- 3. run build_training_set with floors lowered ----
recs = os.path.join(WORK, "records.csv")
with open(recs, "w") as f:
    f.write("record_id,title,abstract\n")
    for i in range(9):
        f.write(f"R-{i:03d},Title {i},Abstract {i}\n")
    f.write("R-100,T,A\nR-101,T,A\nR-102,T,A\nR-900,T,A\n")
cfgp = os.path.join(WORK, "cfg.json")
json.dump({"audit_log_path": alog, "records_metadata_csvs": [recs],
           "criteria_block_text": "P/I/C/O criteria here",
           "rules_block_text": "ER-001 rule",
           "learned_alignment": {"seed": 42,
                                 "training_set_dir": os.path.join(WORK, "ts"),
                                 "data_floors": {"min_training_records": 5,
                                                 "min_includes": 2},
                                 "dev_fraction": 0.2}}, open(cfgp, "w"))
# ---- 3a. GATE 2c enforcement: blocked with no decision, blocked on OPT_OUT ----
r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                    "build_training_set.py"), "--config", cfgp],
                   capture_output=True, text=True)
assert r.returncode != 0 and "Gate 2c" in (r.stderr + r.stdout), \
    f"builder ran without Gate 2c decision: {r.stdout} {r.stderr}"
r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                    "decide_fine_tuning.py"), "--config", cfgp,
                    "--reviewer-id", "HC", "--context", "kickoff",
                    "--decision", "opt-out",
                    "--ack", "I have read the Gate 2c notice in full"],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr
r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                    "build_training_set.py"), "--config", cfgp],
                   capture_output=True, text=True)
assert r.returncode != 0 and "OPT_OUT" in (r.stderr + r.stdout), \
    "builder ran despite logged OPT_OUT"
r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                    "decide_fine_tuning.py"), "--config", cfgp,
                    "--reviewer-id", "HC", "--context", "plateau_trigger",
                    "--decision", "opt-in",
                    "--ack", "I have read the Gate 2c notice in full"],
                   capture_output=True, text=True)
assert r.returncode == 0, r.stderr
assert audit.verify_chain(alog), "chain broken after Gate 2c entries"
print("Gate 2c enforcement: OK (blocked → OPT_OUT blocked → OPT_IN authorises)")

r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts",
                    "build_training_set.py"), "--config", cfgp],
                   capture_output=True, text=True)
print(r.stdout[-600:]); assert r.returncode == 0, r.stderr
card = json.load(open(os.path.join(WORK, "ts", "dataset_card.json")))
assert card["ground_truth_exclusion_count"] == 3
assert not set(card["record_id_manifest"]) & {"R-900", "R-901", "R-902"}, "LEAK"
assert card["counts"]["dpo_pairs"] == 3
assert card["counts"]["dpo_dangerous_direction"] == 2
assert audit.verify_chain(alog), "chain broken after builder entry"
last = json.load(open(alog))["entries"][-1]
assert last["action"] == "adapter_training_set_built"
print("build_training_set: OK (exclusion enforced, card emitted, chain intact)")

# ---- 4. leakage guard actually aborts ----
json.dump({"audit_log_path": alog, "records_metadata_csvs": [recs],
           "criteria_block_text": "x", "rules_block_text": "",
           "learned_alignment": {"seed": 1,
                                 "training_set_dir": os.path.join(WORK, "ts2"),
                                 "extra_holdout_manifests": [],
                                 "data_floors": {"min_training_records": 5,
                                                 "min_includes": 2}}},
          open(cfgp, "w"))
mani = os.path.join(WORK, "force_holdout.txt")
open(mani, "w").write("")  # direct API check of the guard:
from srlib import data as d
try:
    d.assert_no_overlap(["R-100", "R-900"], {"R-900"})
    raise AssertionError("guard failed to fire")
except SystemExit as e:
    assert "R-900" in str(e)
print("leakage guard: OK (SystemExit on ground-truth overlap)")
print("\nALL SMOKE TESTS PASSED")
