"""srlib.data — deterministic training-data construction for Phase 5c.

Sources are v7's EXISTING artifacts only (audit_log.json entries). Rules:
- Ground-truth validation records (the promotion test set) are NEVER training
  data: enforced by an exclusion manifest asserted here and in train_adapter.
- SFT targets are human-confirmed decisions rendered in the structured
  criterion-by-criterion schema — never bare labels. AGREE ⇒ the AI's logged
  structured output (human-confirmed). OVERRIDE ⇒ a deterministic patch of the
  logged output on the misjudged criterion using only logged fields.
- DPO pairs: rejected = the AI's overridden output; chosen = the patched one.
- Phase 7b: ONLY root-cause class 1 (transcription/location error) corrections
  become extraction examples; classes 2–4 never do (router preserved).
"""
from __future__ import annotations

import json
import random
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from . import audit as _audit

GT_ACTION_MARKERS = ("ground_truth",)          # v7 ground-truth validation actions
SCREEN_PHASES = {"5a", "5", "5b", "7"}
DECISIONS = ("INCLUDE", "EXCLUDE", "UNCERTAIN")

SYSTEM_SCREEN = (
    "You are a systematic-review screening assistant. You produce structured "
    "recommendations only; a human makes every final decision. Evaluate the "
    "record against EACH criterion, quoting abstract evidence or stating "
    "\"No information in abstract\". Respond with ONLY a JSON object: "
    '{"criteria":[{"criterion":str,"evidence":str,"assessment":'
    '"MET|NOT MET|UNCLEAR|NOT APPLICABLE"}],"decision":'
    '"INCLUDE|EXCLUDE|UNCERTAIN","exclusion_reason":str|null,'
    '"confidence":"High|Medium|Low","summary":str}'
)

SYSTEM_EXTRACT = (
    "You are a data-extraction assistant. Propose the requested data point "
    "from the supplied text window, verbatim as reported, with an exact quote "
    "and location. Never compute or convert anything. If not present, use "
    'status NOT_LOCATED. Respond with ONLY JSON: {"dp_id":str,'
    '"value_as_reported":str|null,"quote":str|null,"page":int|null,'
    '"line_range":[int,int]|null,"status":"LOCATED|NOT_LOCATED"}'
)


# ---------------------------------------------------------------- manifests

def ground_truth_ids(log: Dict[str, Any], extra_manifests: Sequence[str] = ()
                     ) -> Set[str]:
    """Record IDs ever used for ground-truth validation (⇒ promotion test set).
    Union of (a) audit-log ground-truth actions and (b) researcher-supplied
    manifest files (one stable record ID per line)."""
    ids: Set[str] = set()
    for e in log.get("entries", []):
        act = (e.get("action") or "").lower()
        if any(m in act for m in GT_ACTION_MARKERS) and e.get("record_id"):
            ids.add(e["record_id"])
    for path in extra_manifests:
        with open(path, "r", encoding="utf-8") as f:
            ids.update(x.strip() for x in f if x.strip())
    return ids


def assert_no_overlap(train_ids: Iterable[str], holdout_ids: Set[str]) -> None:
    leak = sorted(set(train_ids) & holdout_ids)
    if leak:
        raise SystemExit(
            "FATAL — ground-truth leakage blocked: these record IDs are in the "
            f"promotion test set and may NEVER be trained on: {leak[:10]}"
            f"{' …' if len(leak) > 10 else ''}")


# ------------------------------------------------------------- rendering

def render_record_prompt(rec: Dict[str, Any], criteria_block: str,
                         rules_block: str) -> str:
    return (
        f"REVIEW CRITERIA:\n{criteria_block.strip()}\n\n"
        f"ELIGIBILITY RULES (researcher-approved; apply where they bear):\n"
        f"{rules_block.strip() or '(none)'}\n\n"
        f"RECORD ID: {rec.get('record_id','')}\n"
        f"Title: {rec.get('title','')}\n"
        f"Abstract: {rec.get('abstract','') or 'No abstract available.'}\n"
    )


def structured_from_entry(e: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    sr = e.get("structured_rationale") or {}
    crits = sr.get("criteria_assessments") or []
    dec = e.get("decision")
    if dec not in DECISIONS or not crits:
        return None
    out = {
        "criteria": [{"criterion": c.get("criterion", ""),
                      "evidence": c.get("evidence", c.get("evidence_quote", "")),
                      "assessment": c.get("assessment", "")} for c in crits],
        "decision": dec,
        "exclusion_reason": (e.get("output") or {}).get("exclusion_reason"),
        "confidence": (e.get("output") or {}).get("confidence", "Medium"),
        "summary": sr.get("summary", ""),
    }
    return out


def patch_override(ai_out: Dict[str, Any], human_decision: str,
                   override_reason: str,
                   criterion_misjudged: Optional[str]) -> Dict[str, Any]:
    """Deterministic construction of the human-confirmed target from an
    OVERRIDE, using only logged fields (no invented content)."""
    out = json.loads(json.dumps(ai_out))  # deep copy
    out["decision"] = human_decision
    out["summary"] = f"Human-audited decision: {human_decision}. Reason: {override_reason}"
    tgt = (criterion_misjudged or "").lower()
    for c in out["criteria"]:
        if tgt and tgt in c["criterion"].lower():
            c["assessment"] = ("MET" if human_decision == "INCLUDE"
                               else "NOT MET" if human_decision == "EXCLUDE"
                               else "UNCLEAR")
            c["evidence"] = (c.get("evidence", "") +
                             f" [Reviewer correction: {override_reason}]").strip()
    if human_decision != "EXCLUDE":
        out["exclusion_reason"] = None
    return out


def sft_example(prompt: str, target_obj: Dict[str, Any], task: str,
                record_id: str, provenance: str) -> Dict[str, Any]:
    return {"prompt": f"{SYSTEM_SCREEN}\n\n{prompt}",
            "completion": json.dumps(target_obj, ensure_ascii=False),
            "task": task, "record_id": record_id, "provenance": provenance,
            "label": target_obj.get("decision")}


def dpo_example(prompt: str, chosen: Dict[str, Any], rejected: Dict[str, Any],
                record_id: str, dangerous: bool) -> Dict[str, Any]:
    return {"prompt": f"{SYSTEM_SCREEN}\n\n{prompt}",
            "chosen": json.dumps(chosen, ensure_ascii=False),
            "rejected": json.dumps(rejected, ensure_ascii=False),
            "record_id": record_id, "dangerous_direction": dangerous}


# ----------------------------------------------------- harvest from audit log

def harvest(log: Dict[str, Any], records_meta: Dict[str, Dict[str, Any]],
            criteria_block: str, rules_block: str
            ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Return (sft_screen, dpo_pairs, sft_extraction) from audit entries.

    Eligible screening entries: actor AI, phase in SCREEN_PHASES,
    human_review.reviewed == True, decision in DECISIONS, structured
    rationale present. Adjudicated 5b conflicts use the adjudicated decision.
    Extraction: phase 7b entries whose logged root_cause class == transcription.
    """
    sft, dpo, sft_x = [], [], []
    for e in log.get("entries", []):
        phase = str(e.get("phase", ""))
        hr = e.get("human_review") or {}
        rid = e.get("record_id")
        if phase in SCREEN_PHASES and e.get("actor") == "AI" and rid \
                and hr.get("reviewed") is True:
            ai_out = structured_from_entry(e)
            if ai_out is None:
                continue
            rec = records_meta.get(rid, {"record_id": rid, "title": "", "abstract": ""})
            prompt = render_record_prompt(rec, criteria_block, rules_block)
            task = "full_text_screening" if phase == "7" else "title_abstract_screening"
            if hr.get("agreed_with_ai") is True:
                sft.append(sft_example(prompt, ai_out, task, rid,
                                       f"phase{phase}:AGREE"))
            else:
                human_dec = (e.get("output") or {}).get("human_decision") \
                    or hr.get("human_decision") or hr.get("final_decision")
                if human_dec not in DECISIONS:
                    continue  # cannot construct a confirmed target — skip, log upstream
                chosen = patch_override(ai_out, human_dec,
                                        hr.get("override_reason") or "",
                                        (e.get("output") or {}).get("criterion_misjudged"))
                sft.append(sft_example(prompt, chosen, task, rid,
                                       f"phase{phase}:OVERRIDE_patch"))
                dangerous = (ai_out["decision"] == "EXCLUDE"
                             and human_dec in ("INCLUDE", "UNCERTAIN"))
                dpo.append(dpo_example(prompt, chosen, ai_out, rid, dangerous))
        elif phase == "7b" and rid:
            oc = e.get("output") or {}
            rc = (oc.get("root_cause") or oc.get("root_cause_class") or "").lower()
            if "transcription" in rc and oc.get("corrected_value") and oc.get("quote"):
                sft_x.append({
                    "prompt": (f"{SYSTEM_EXTRACT}\n\nDATA POINT: {oc.get('dp_id','')} — "
                               f"{oc.get('dp_name','')}\nTEXT WINDOW:\n"
                               f"{oc.get('text_window','')}"),
                    "completion": json.dumps({
                        "dp_id": oc.get("dp_id", ""),
                        "value_as_reported": oc["corrected_value"],
                        "quote": oc["quote"], "page": oc.get("page"),
                        "line_range": oc.get("line_range"),
                        "status": "LOCATED"}, ensure_ascii=False),
                    "task": "extraction", "record_id": rid,
                    "provenance": "phase7b:transcription_correction",
                    "label": "LOCATED"})
    return sft, dpo, sft_x


# ------------------------------------------------------ split & oversample

def split_by_record(examples: List[Dict], eval_frac: float, seed: int
                    ) -> Tuple[List[Dict], List[Dict]]:
    """Record-level (never chunk-level) split, stratified by label, seeded."""
    rng = random.Random(seed)
    by_label: Dict[str, List[str]] = {}
    rec_label: Dict[str, str] = {}
    for ex in examples:
        rec_label.setdefault(ex["record_id"], ex.get("label") or "NA")
    for rid, lab in rec_label.items():
        by_label.setdefault(lab, []).append(rid)
    dev_ids: Set[str] = set()
    for lab, rids in sorted(by_label.items()):
        rids = sorted(rids)
        rng.shuffle(rids)
        k = max(1, round(eval_frac * len(rids))) if len(rids) > 1 else 0
        dev_ids.update(rids[:k])
    train = [e for e in examples if e["record_id"] not in dev_ids]
    dev = [e for e in examples if e["record_id"] in dev_ids]
    return train, dev


def oversample_retain(train: List[Dict], seed: int, target_frac: float = 0.25,
                      cap: int = 3) -> Tuple[List[Dict], float]:
    """Seeded duplication of retain-class (INCLUDE/UNCERTAIN) screening
    examples until retain ≥ target_frac of the set or the cap× is reached.
    Duplication (not loss weighting) because SFT loss is token-level over a
    generative target, where per-class loss weights are ill-defined;
    duplication is the transparent, loggable equivalent. Cap limits verbatim
    memorisation pressure."""
    rng = random.Random(seed + 1)
    retain = [e for e in train if e.get("label") in ("INCLUDE", "UNCERTAIN")
              and e.get("task") != "extraction"]
    if not retain:
        return train, 1.0
    out = list(train)
    factor = 1
    while factor < cap:
        frac = sum(1 for e in out if e.get("label") in ("INCLUDE", "UNCERTAIN")
                   and e.get("task") != "extraction") / max(1, len(out))
        if frac >= target_frac:
            break
        extra = [dict(e) for e in retain]
        rng.shuffle(extra)
        out.extend(extra)
        factor += 1
    rng.shuffle(out)
    return out, float(factor)


def dataset_hash(examples: List[Dict]) -> str:
    blob = "\n".join(sorted(json.dumps(e, sort_keys=True, ensure_ascii=False)
                            for e in examples)).encode("utf-8")
    return _audit.sha256_hex(blob)


def write_jsonl(path: str, rows: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]
