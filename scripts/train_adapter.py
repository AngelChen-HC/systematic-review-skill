#!/usr/bin/env python3
"""train_adapter.py — Phase 5c, Step 5c.2 (SKILL.md v8.0).

Fine-tunes the LOCAL open-weights screener (never the orchestrator) with
transformers + peft (LoRA/QLoRA) + trl. Stage 1: SFTTrainer on human-confirmed
structured decisions. Stage 2 (--stage dpo|kto, only when build_training_set
recommended it): preference optimisation on override pairs. Seeded,
checkpointed, resume-able; writes MANIFEST.json provenance and its own audit
entry (action: adapter_training_run).

HOW TO RUN (no coding experience needed)
  python3 scripts/train_adapter.py --config learned_alignment/adapter_training.json \
      --adapter-version v1.0.0
  Add --stage dpo only if the dataset card said so. Add --resume to continue
  an interrupted run from its last checkpoint.
Expected output ends with:  "Adapter saved: … weights sha256: …"
Honest cost: minutes on a recent GPU; hours on CPU (see the Phase 5c table).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from srlib import audit, data, modeling  # noqa: E402


def _dset(rows):
    from datasets import Dataset
    return Dataset.from_list(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--adapter-version", required=True,
                    help="semantic version for this adapter, e.g. v1.0.0")
    ap.add_argument("--stage", choices=["sft", "dpo", "kto"], default="sft")
    ap.add_argument("--resume", action="store_true",
                    help="resume from the last checkpoint of this run")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    la = cfg["learned_alignment"]
    audit.require_fine_tuning_opt_in(audit.load_audit(cfg["audit_log_path"]))  # GATE 2c
    seed = int(la["seed"])
    modeling.set_all_seeds(seed)

    ts_dir = la.get("training_set_dir", "learned_alignment/training_runs/current")
    card = json.load(open(os.path.join(ts_dir, "dataset_card.json"), encoding="utf-8"))

    # Re-assert ground-truth exclusion from the manifest (defence in depth).
    holdout = set(x.strip() for x in
                  open(card["ground_truth_exclusion_manifest"], encoding="utf-8")
                  if x.strip())
    data.assert_no_overlap(card["record_id_manifest"], holdout)

    run_dir = os.path.join("learned_alignment", "training_runs",
                           f"{args.adapter_version}_{args.stage}")
    os.makedirs(run_dir, exist_ok=True)

    base_id = la["base_model_id"]
    quant = la.get("quantization", "none")
    prior_adapter = (la.get("active_adapter")
                     if args.stage in ("dpo", "kto")
                     and la.get("active_adapter") not in (None, "prompt-only")
                     else None)
    if prior_adapter:  # Stage 2 refines the promoted Stage-1 adapter
        model, tok, resolved = modeling.load_with_adapter(
            base_id, la.get("base_model_revision"),
            os.path.join("learned_alignment", "adapters", prior_adapter), quant)
        model.train()
    else:
        model, tok, resolved = modeling.load_base(
            base_id, la.get("base_model_revision"), quant)
        model = modeling.attach_lora(model, la.get("lora", {}), quant)

    hp = {"seed": seed, "stage": args.stage,
          "lora": la.get("lora", {}), "quantization": quant,
          "learning_rate": 1e-4 if args.stage == "sft" else 5e-6,
          "num_train_epochs": 5 if args.stage == "sft" else 3,
          "per_device_train_batch_size": 1, "gradient_accumulation_steps": 8,
          "max_length": int(la.get("max_seq_len", 2048)),
          "early_stopping_patience": 2 if args.stage == "sft" else 1,
          "dpo_beta": 0.1}
    common = dict(output_dir=os.path.join(run_dir, "checkpoints"), seed=seed,
                  learning_rate=hp["learning_rate"],
                  num_train_epochs=hp["num_train_epochs"],
                  per_device_train_batch_size=hp["per_device_train_batch_size"],
                  gradient_accumulation_steps=hp["gradient_accumulation_steps"],
                  logging_steps=5, save_strategy="epoch", eval_strategy="epoch",
                  save_total_limit=2, load_best_model_at_end=True,
                  metric_for_best_model="eval_loss", greater_is_better=False,
                  report_to=[], lr_scheduler_type="cosine", warmup_ratio=0.1)

    from transformers import EarlyStoppingCallback
    cb = [EarlyStoppingCallback(early_stopping_patience=hp["early_stopping_patience"])]

    if args.stage == "sft":
        from trl import SFTConfig, SFTTrainer
        train = _dset(data.read_jsonl(os.path.join(ts_dir, "sft_train.jsonl")))
        dev = _dset(data.read_jsonl(os.path.join(ts_dir, "sft_dev.jsonl")))
        tcfg = modeling.safe_config(SFTConfig, **common,
                                    max_length=hp["max_length"],
                                    completion_only_loss=True, packing=False)
        trainer = modeling.safe_config(
            SFTTrainer, model=model, args=tcfg, train_dataset=train,
            eval_dataset=dev, processing_class=tok, callbacks=cb)
    else:
        pairs = data.read_jsonl(os.path.join(ts_dir, "dpo_pairs.jsonl"))
        st = la.get("stage2_thresholds", {})
        if args.stage == "dpo":
            n_d = sum(1 for p in pairs if p.get("dangerous_direction"))
            if len(pairs) < int(st.get("dpo_min_pairs", 40)) or \
                    n_d < int(st.get("dpo_min_dangerous_direction_pairs", 10)):
                raise SystemExit(f"STOP — DPO thresholds not met ({len(pairs)} "
                                 f"pairs, {n_d} dangerous-direction). Run SFT only.")
            from trl import DPOConfig, DPOTrainer
            ds = _dset([{"prompt": p["prompt"], "chosen": p["chosen"],
                         "rejected": p["rejected"]} for p in pairs])
            tcfg = modeling.safe_config(DPOConfig, **common, beta=hp["dpo_beta"],
                                        max_length=hp["max_length"])
            trainer = modeling.safe_config(
                DPOTrainer, model=model, args=tcfg, train_dataset=ds,
                eval_dataset=ds.select(range(min(16, len(ds)))),
                processing_class=tok, callbacks=cb)
        else:
            if len(pairs) < int(st.get("kto_min_examples", 60)):
                raise SystemExit("STOP — KTO threshold not met. Run SFT only.")
            from trl import KTOConfig, KTOTrainer
            rows = ([{"prompt": p["prompt"], "completion": p["chosen"], "label": True}
                     for p in pairs] +
                    [{"prompt": p["prompt"], "completion": p["rejected"], "label": False}
                     for p in pairs])
            ds = _dset(rows)
            tcfg = modeling.safe_config(KTOConfig, **common, beta=hp["dpo_beta"],
                                        max_length=hp["max_length"])
            trainer = modeling.safe_config(
                KTOTrainer, model=model, args=tcfg, train_dataset=ds,
                eval_dataset=ds.select(range(min(16, len(ds)))),
                processing_class=tok, callbacks=cb)

    ckpts = sorted(glob.glob(os.path.join(run_dir, "checkpoints", "checkpoint-*")))
    trainer.train(resume_from_checkpoint=(ckpts[-1] if (args.resume and ckpts) else None))

    adapter_dir = os.path.join("learned_alignment", "adapters", args.adapter_version)
    os.makedirs(adapter_dir, exist_ok=True)
    trainer.model.save_pretrained(adapter_dir)
    tok.save_pretrained(adapter_dir)
    weights = sorted(glob.glob(os.path.join(adapter_dir, "adapter_model.*")))
    whash = audit.sha256_file(weights[0]) if weights else "MISSING"

    manifest = {"adapter_version": args.adapter_version, "stage": args.stage,
                "weights_sha256": whash, "base_model_id": base_id,
                "base_model_revision": resolved,
                "built_on_adapter": prior_adapter,
                "training_dataset_hash": card["dataset_hash"],
                "record_id_manifest_path": os.path.join(ts_dir, "dataset_card.json"),
                "ground_truth_exclusion_manifest":
                    card["ground_truth_exclusion_manifest"],
                "hyperparameters": hp, "created_at": audit.now_iso(),
                "run_dir": run_dir}
    with open(os.path.join(adapter_dir, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    audit.append_entry(cfg["audit_log_path"], phase="5c",
                       action="adapter_training_run", actor="SYSTEM",
                       local_model_id_used=f"{base_id}@{resolved}",
                       adapter_version_used=args.adapter_version,
                       output=manifest)
    print(f"Adapter saved: {adapter_dir}  weights sha256: {whash}")
    print("NEXT: python3 scripts/evaluate_adapter.py — promotion is NEVER automatic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
