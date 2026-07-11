#!/usr/bin/env python3
"""build_training_set.py — Phase 5c, Step 5c.1 (SKILL.md v8.0).

Deterministically extracts SFT (and, if thresholds are met, DPO) datasets
from the review's audit_log.json, honouring the ground-truth exclusion
manifest, and emits a dataset card + hash. Writes its own audit entry
(action: adapter_training_set_built).

HOW TO RUN (no coding experience needed)
  1) Open your terminal, activate the review environment (Phase 3):
        source review_env/bin/activate        (Mac/Linux)
        review_env\\Scripts\\activate          (Windows)
  2) pip install -r requirements-finetune.txt   (first time only; ~10 min)
  3) python3 scripts/build_training_set.py --config learned_alignment/adapter_training.json
Expected output ends with:  "Training set built. Dataset hash: <64 hex chars>"

The script ABORTS if any ground-truth (promotion-test) record would enter
the training or dev split. That is deliberate and non-negotiable.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from srlib import audit, data  # noqa: E402


def load_records_meta(paths):
    meta = {}
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rid = row.get("record_id") or row.get("id")
                if rid:
                    meta[rid] = {"record_id": rid,
                                 "title": row.get("title", ""),
                                 "abstract": row.get("abstract", "")}
    return meta


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True,
                    help="learned_alignment/adapter_training.json (see example)")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    la = cfg["learned_alignment"]
    seed = int(la["seed"])
    out_dir = la.get("training_set_dir", "learned_alignment/training_runs/current")
    os.makedirs(out_dir, exist_ok=True)

    log = audit.load_audit(cfg["audit_log_path"])
    audit.require_fine_tuning_opt_in(log)  # GATE 2c enforcement
    records_meta = load_records_meta(cfg.get("records_metadata_csvs", []))
    criteria_block = open(cfg["criteria_block_path"], encoding="utf-8").read() \
        if cfg.get("criteria_block_path") else cfg.get("criteria_block_text", "")
    rules_block = open(cfg["rules_block_path"], encoding="utf-8").read() \
        if cfg.get("rules_block_path") else cfg.get("rules_block_text", "")

    # 1. Promotion-test (ground-truth) exclusion manifest — built first.
    holdout = data.ground_truth_ids(log, la.get("extra_holdout_manifests", []))
    manifest_path = os.path.join(out_dir, "ground_truth_exclusion_manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(holdout)) + ("\n" if holdout else ""))
    print(f"Ground-truth exclusion manifest: {len(holdout)} record IDs "
          f"→ {manifest_path}")

    # 2. Harvest human-confirmed decisions from the audit log.
    sft, dpo, sft_x = data.harvest(log, records_meta, criteria_block, rules_block)
    sft = [e for e in sft + sft_x if e["record_id"] not in holdout]
    dpo = [e for e in dpo if e["record_id"] not in holdout]
    data.assert_no_overlap([e["record_id"] for e in sft], holdout)
    data.assert_no_overlap([e["record_id"] for e in dpo], holdout)

    floors = la.get("data_floors", {})
    n_retain = sum(1 for e in sft if e.get("label") in ("INCLUDE", "UNCERTAIN"))
    if len(sft) < int(floors.get("min_training_records", 100)) \
            or n_retain < int(floors.get("min_includes", 8)):
        print(f"STOP — data floors not met: {len(sft)} examples "
              f"({n_retain} retain-class). Phase 5c requires ≥"
              f"{floors.get('min_training_records',100)} examples and ≥"
              f"{floors.get('min_includes',8)} retain-class. Keep using the "
              "prompt-calibration fast path and return later.")
        return 2

    # 3. Record-level split (dev for early stopping ONLY), then oversample.
    train, dev = data.split_by_record(sft, float(la.get("dev_fraction", 0.15)), seed)
    train, factor = data.oversample_retain(
        train, seed, float(la.get("oversample_target_frac", 0.25)),
        int(la.get("oversample_cap", 3)))

    # 4. Stage-2 preference data, only above thresholds.
    st = la.get("stage2_thresholds", {})
    dangerous = sum(1 for e in dpo if e.get("dangerous_direction"))
    stage2 = "none"
    if len(dpo) >= int(st.get("dpo_min_pairs", 40)) \
            and dangerous >= int(st.get("dpo_min_dangerous_direction_pairs", 10)):
        stage2 = "dpo"
    elif len(dpo) >= int(st.get("kto_min_examples", 60)):
        stage2 = "kto"

    paths = {"sft_train": os.path.join(out_dir, "sft_train.jsonl"),
             "sft_dev": os.path.join(out_dir, "sft_dev.jsonl"),
             "dpo_pairs": os.path.join(out_dir, "dpo_pairs.jsonl")}
    data.write_jsonl(paths["sft_train"], train)
    data.write_jsonl(paths["sft_dev"], dev)
    data.write_jsonl(paths["dpo_pairs"], dpo)
    dhash = data.dataset_hash(train + dev + dpo)

    # 5. Dataset card (auto-generated per run — mandated).
    card = {
        "dataset_hash": dhash, "seed": seed,
        "counts": {"sft_train": len(train), "sft_dev": len(dev),
                   "dpo_pairs": len(dpo), "dpo_dangerous_direction": dangerous,
                   "extraction_examples": sum(1 for e in train + dev
                                              if e.get("task") == "extraction")},
        "label_prevalence_train": {
            lab: sum(1 for e in train if e.get("label") == lab)
            for lab in ("INCLUDE", "EXCLUDE", "UNCERTAIN", "LOCATED")},
        "oversample_factor_applied": factor,
        "stage2_recommendation": stage2,
        "record_id_manifest": sorted({e["record_id"] for e in train + dev + dpo}),
        "ground_truth_exclusion_manifest": manifest_path,
        "ground_truth_exclusion_count": len(holdout),
        "leakage_check": "PASS — intersection with promotion test set is empty",
        "sources": "audit_log.json phases 5a/5/5b/7 human-reviewed entries; "
                   "phase 7b transcription-class corrections only",
        "audit_log_sha256": audit.sha256_file(cfg["audit_log_path"]),
        "builder": "build_training_set.py (srlib 8.0.0)",
    }
    card_path = os.path.join(out_dir, "dataset_card.json")
    with open(card_path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "dataset_card.md"), "w", encoding="utf-8") as f:
        f.write("# Dataset card — Phase 5c training set\n\n```json\n"
                + json.dumps({k: v for k, v in card.items()
                              if k != "record_id_manifest"}, indent=2)
                + "\n```\n(record_id_manifest in dataset_card.json)\n")

    audit.append_entry(cfg["audit_log_path"], phase="5c",
                       action="adapter_training_set_built", actor="SYSTEM",
                       output={"dataset_hash": dhash, "counts": card["counts"],
                               "oversample_factor": factor,
                               "stage2_recommendation": stage2,
                               "exclusion_manifest_sha256":
                                   audit.sha256_file(manifest_path),
                               "dataset_card_sha256": audit.sha256_file(card_path)})
    print(f"Stage-2 recommendation: {stage2} "
          f"({len(dpo)} pairs, {dangerous} dangerous-direction)")
    print(f"Training set built. Dataset hash: {dhash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
