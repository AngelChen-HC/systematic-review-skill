"""srlib.audit — hash-chained audit-log helpers (SKILL.md v8.0, Phase 5c).

Every v8 script writes its own entries into the review's `audit_log.json`
using the EXACT v7 entry format (entry_id, created_at, phase, action, actor,
record_id, batch_number, model_id_used, input_hash, output_hash, output,
decision, structured_rationale, human_review, performance_flag,
previous_entry_hash) so the chain verifies with the shipped
`audit_chain_verification.py` unchanged.

No statistics are computed here. No LLM is involved here.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import uuid
from typing import Any, Dict, Optional

SCHEMA_HINT = "8.0"


def canonical(obj: Any) -> bytes:
    """Canonical JSON serialisation (sorted keys, no whitespace drift)."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_obj(obj: Any) -> str:
    return sha256_hex(canonical(obj))


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()


def load_audit(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"audit_log.json not found at {path}. Point --audit-log at your "
            "review's audit log (created in Phase 1).")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_audit(path: str, log: Dict[str, Any]) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _previous_hash(log: Dict[str, Any]) -> str:
    entries = log.get("entries", [])
    if entries:
        return sha256_obj(entries[-1])
    gen = log.get("chain_integrity", {}).get("genesis_hash") or ""
    if not gen:
        gen = sha256_hex(b"GENESIS")
        log.setdefault("chain_integrity", {"algorithm": "SHA-256"})
        log["chain_integrity"]["genesis_hash"] = gen
    return gen


def append_entry(audit_path: str,
                 phase: str,
                 action: str,
                 actor: str,
                 output: Dict[str, Any],
                 decision: Optional[str] = None,
                 record_id: Optional[str] = None,
                 batch_number: Optional[int] = None,
                 model_id_used: Optional[str] = None,
                 local_model_id_used: Optional[str] = None,
                 adapter_version_used: Optional[str] = None,
                 input_obj: Optional[Any] = None,
                 human_review: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Append one hash-chained entry (v7 format + v8 optional local-model fields)."""
    log = load_audit(audit_path)
    entry = {
        "entry_id": str(uuid.uuid4()),
        "created_at": now_iso(),
        "phase": phase,
        "action": action,
        "actor": actor,
        "record_id": record_id,
        "batch_number": batch_number,
        "model_id_used": model_id_used,
        "local_model_id_used": local_model_id_used,
        "adapter_version_used": adapter_version_used,
        "input_hash": sha256_obj(input_obj) if input_obj is not None else None,
        "output_hash": sha256_obj(output),
        "output": output,
        "decision": decision,
        "structured_rationale": {"criteria_assessments": [], "evidence_quotes": [],
                                 "decision_rule_applied": "", "summary": ""},
        "human_review": human_review or {"reviewed": False, "reviewer_id": None,
                                         "agreed_with_ai": None,
                                         "override_reason": None,
                                         "reviewed_at": None},
        "performance_flag": None,
        "previous_entry_hash": _previous_hash(log),
    }
    log.setdefault("entries", []).append(entry)
    save_audit(audit_path, log)
    return entry


def require_activation(la_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """GATE 5c-A enforcement. Every Phase 5c script calls this before any
    base-model download, training-set build, or local inference. Returns the
    decision record on ACTIVATE; aborts otherwise. promote_adapter's rollback
    path is exempt by design — the conservative action is never blocked."""
    path = la_cfg.get("activation_decision_path",
                      "learned_alignment/activation_decision.json")
    if not os.path.exists(path):
        raise SystemExit(
            "GATE 5c-A not passed — no activation decision found at "
            f"{path}.\nRun:  python3 scripts/activate_learned_alignment.py "
            "--config <your config> --reviewer-id <you>\n"
            "Nothing in Phase 5c (no model download, no training, no local "
            "inference) runs before that informed decision is logged.")
    with open(path, encoding="utf-8") as f:
        rec = json.load(f)
    if rec.get("decision") != "activated":
        raise SystemExit(
            f"GATE 5c-A decision on record is '{rec.get('decision')}' "
            f"(by {rec.get('reviewer_id')}, {rec.get('at')}). Phase 5c stays "
            "inactive. Re-run activate_learned_alignment.py to change it.")
    return rec


def latest_action(log: Dict[str, Any], action: str) -> Optional[Dict[str, Any]]:
    """Most recent entry with the given action, or None."""
    for e in reversed(log.get("entries", [])):
        if e.get("action") == action:
            return e
    return None


def require_fine_tuning_opt_in(log: Dict[str, Any]) -> None:
    """Gate 2c enforcement: abort unless the latest fine_tuning_decision is
    an informed OPT_IN. Kickoff silence, config flags, or a prior opt-out do
    not authorise training."""
    e = latest_action(log, "fine_tuning_decision")
    dec = ((e or {}).get("output") or {}).get("decision")
    if dec != "OPT_IN":
        state = "no Gate 2c decision is on record" if e is None \
            else f"the most recent Gate 2c decision is {dec}"
        raise SystemExit(
            "BLOCKED — Gate 2c (fine-tuning decision) not passed: "
            f"{state}. Fine-tuning requires an informed opt-in. Run:\n"
            "    python3 scripts/decide_fine_tuning.py --config "
            "learned_alignment/adapter_training.json\n"
            "read the notice, and type your decision. An opt-out is a fully "
            "valid, logged outcome.")


def verify_chain(audit_path: str) -> bool:
    """True iff every previous_entry_hash matches the preceding entry's hash."""
    log = load_audit(audit_path)
    prev = log.get("chain_integrity", {}).get("genesis_hash") or sha256_hex(b"GENESIS")
    for i, e in enumerate(log.get("entries", [])):
        if e.get("previous_entry_hash") != prev:
            print(f"[audit] chain BROKEN at entry index {i} ({e.get('action')})")
            return False
        prev = sha256_obj(e)
    return True
