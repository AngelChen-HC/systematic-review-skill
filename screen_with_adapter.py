#!/usr/bin/env python3
"""screen_with_adapter.py — Phase 5c deployment surface (SKILL.md v8.0).

Runs the LOCAL screener (base model + the ACTIVE promoted adapter, or
prompt-only) over a batch, producing the structured criterion-by-criterion
output so results drop UNMODIFIED into the existing dual-screening comparison
(batch_{N}_decisions.jsonl shape). Greedy decoding (the temperature-0
analogue). RECOMMENDATIONS ONLY: nothing here finalises, auto-excludes, or
bypasses any human gate. Unparseable outputs become UNCERTAIN + a flag —
never a silent drop. Append-only checkpointing: rerun to resume.

--task extraction: propose one data point per row from a supplied text
window; the quote is machine-pre-verified against the window and anything
unverifiable is emitted as NOT_LOCATED (Phase 7b rule, unchanged).

HOW TO RUN (no coding experience needed)
  python3 scripts/screen_with_adapter.py --config learned_alignment/adapter_training.json \
      --records screening/title_abstract/batches/batch_7_records.csv \
      --out screening/dual_screening/batch_7_reviewerB_adapter.jsonl --batch 7
Expected output ends with:  "Batch complete: N records → <out>"
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from srlib import audit, data, modeling  # noqa: E402


def parse_json_obj(text: str):
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e <= s:
        return None
    try:
        return json.loads(text[s:e + 1])
    except json.JSONDecodeError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--records", required=True,
                    help="CSV: record_id,title,abstract  (extraction task: "
                         "record_id,dp_id,dp_name,text_window,page)")
    ap.add_argument("--out", required=True, help="append-only .jsonl output")
    ap.add_argument("--batch", type=int, default=None)
    ap.add_argument("--task", choices=["screening", "extraction"],
                    default="screening")
    args = ap.parse_args()

    cfg = json.load(open(args.config, encoding="utf-8"))
    la = cfg["learned_alignment"]
    modeling.set_all_seeds(int(la["seed"]))

    active = la.get("active_adapter", "prompt-only")
    ptr_path = os.path.join("learned_alignment", "active_adapter.json")
    if os.path.exists(ptr_path):
        active = json.load(open(ptr_path, encoding="utf-8")).get("active", active)
    adapter_dir, whash = None, None
    if active and active != "prompt-only":
        adapter_dir = os.path.join("learned_alignment", "adapters", active)
        man = json.load(open(os.path.join(adapter_dir, "MANIFEST.json"),
                             encoding="utf-8"))
        whash = man["weights_sha256"]
    model, tok, resolved = modeling.load_with_adapter(
        la["base_model_id"], la.get("base_model_revision"), adapter_dir,
        la.get("quantization", "none"))
    local_id = f"{la['base_model_id']}@{resolved}"

    criteria_block = open(cfg["criteria_block_path"], encoding="utf-8").read() \
        if cfg.get("criteria_block_path") else cfg.get("criteria_block_text", "")
    rules_block = open(cfg["rules_block_path"], encoding="utf-8").read() \
        if cfg.get("rules_block_path") else cfg.get("rules_block_text", "")
    prompt_version_hash = audit.sha256_obj(
        {"criteria": criteria_block, "rules": rules_block,
         "system": data.SYSTEM_SCREEN if args.task == "screening"
         else data.SYSTEM_EXTRACT})

    done = set()
    if os.path.exists(args.out):  # append-only checkpoint = resume mechanism
        for row in data.read_jsonl(args.out):
            done.add((row["record_id"], row.get("dp_id", "")))
        print(f"Resuming: {len(done)} rows already completed in {args.out}")

    n = 0
    with open(args.records, newline="", encoding="utf-8") as f, \
            open(args.out, "a", encoding="utf-8") as out:
        for row in csv.DictReader(f):
            rid = row.get("record_id") or row.get("id")
            key = (rid, row.get("dp_id", ""))
            if not rid or key in done:
                continue
            if args.task == "screening":
                prompt = (data.SYSTEM_SCREEN + "\n\n" +
                          data.render_record_prompt(
                              {"record_id": rid, "title": row.get("title", ""),
                               "abstract": row.get("abstract", "")},
                              criteria_block, rules_block))
                raw = modeling.generate_greedy(model, tok, prompt)
                obj = parse_json_obj(raw)
                flag = None
                if obj is None or obj.get("decision") not in data.DECISIONS:
                    obj = {"criteria": [], "decision": "UNCERTAIN",
                           "exclusion_reason": None, "confidence": "Low",
                           "summary": "PARSE_FAILURE — output did not conform; "
                                      "routed UNCERTAIN for human attention."}
                    flag = "PARSE_FAILURE"
                rec_out = {"record_id": rid, "batch_number": args.batch,
                           "reviewer": "local_adapter_screener",
                           "recommendation": obj["decision"],
                           "exclusion_reason": obj.get("exclusion_reason"),
                           "confidence": obj.get("confidence", "Low"),
                           "structured_rationale": obj,
                           "performance_flag": flag,
                           "local_model_id_used": local_id,
                           "adapter_version_used": active,
                           "adapter_weights_sha256": whash,
                           "prompt_version_hash": prompt_version_hash,
                           "output_hash": audit.sha256_obj(raw),
                           "created_at": audit.now_iso()}
            else:
                window = row.get("text_window", "")
                prompt = (f"{data.SYSTEM_EXTRACT}\n\nDATA POINT: "
                          f"{row.get('dp_id','')} — {row.get('dp_name','')}\n"
                          f"PAGE: {row.get('page','?')}\nTEXT WINDOW:\n{window}")
                raw = modeling.generate_greedy(model, tok, prompt, 300)
                obj = parse_json_obj(raw) or {}
                quote = obj.get("quote") or ""
                verified = bool(quote) and quote in window  # machine pre-check
                if not verified:  # unanchored proposal ⇒ NOT_LOCATED (v7 rule)
                    obj = {"dp_id": row.get("dp_id", ""),
                           "value_as_reported": None, "quote": None,
                           "page": None, "line_range": None,
                           "status": "NOT_LOCATED"}
                rec_out = {"record_id": rid, "dp_id": row.get("dp_id", ""),
                           "proposal": obj, "anchor_preverified": verified,
                           "local_model_id_used": local_id,
                           "adapter_version_used": active,
                           "adapter_weights_sha256": whash,
                           "prompt_version_hash": prompt_version_hash,
                           "output_hash": audit.sha256_obj(raw),
                           "created_at": audit.now_iso()}
            out.write(json.dumps(rec_out, ensure_ascii=False) + "\n")
            out.flush()
            n += 1
            if n % 10 == 0:
                print(f"  … {n} records done")

    audit.append_entry(cfg["audit_log_path"], phase="5c",
                       action="adapter_screening_batch", actor="AI",
                       batch_number=args.batch, local_model_id_used=local_id,
                       adapter_version_used=active,
                       output={"task": args.task, "records_processed": n,
                               "output_file": args.out,
                               "adapter_weights_sha256": whash,
                               "prompt_version_hash": prompt_version_hash,
                               "note": "recommendations only; all decisions "
                                       "remain subject to the human gates"})
    print(f"Batch complete: {n} records → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
