"""srlib.modeling — model/adapter plumbing for Phase 5c.

Targets the pinned stack in requirements-finetune.txt (versions verified on
PyPI at v8 authoring, 2026-07-10): transformers 5.13.0, peft 0.19.1,
trl 1.8.0, datasets 5.0.0, accelerate 1.14.0, bitsandbytes 0.49.2,
torch 2.13.0. `safe_config` filters kwargs by signature so minor API drift
degrades gracefully instead of crashing a non-coder's run.
"""
from __future__ import annotations

import inspect
import os
import random
from typing import Any, Dict, Optional, Tuple

from .audit import sha256_file  # re-export for scripts


def set_all_seeds(seed: int) -> None:
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass
    try:
        import transformers
        transformers.set_seed(seed)
    except Exception:
        pass


def safe_config(cls, **kwargs):
    """Instantiate cls with only the kwargs its signature accepts; report drops."""
    try:
        params = inspect.signature(cls.__init__).parameters
        accepts_var = any(p.kind is inspect.Parameter.VAR_KEYWORD
                          for p in params.values())
        if not accepts_var:
            dropped = [k for k in kwargs if k not in params]
            if dropped:
                print(f"[compat] {cls.__name__} ignoring unsupported kwargs: {dropped}")
            kwargs = {k: v for k, v in kwargs.items() if k in params}
    except (TypeError, ValueError):
        pass
    return cls(**kwargs)


def detect_device() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


def load_base(model_id: str, revision: Optional[str], quantization: str = "none"
              ) -> Tuple[Any, Any, str]:
    """Load tokenizer + base model. Returns (model, tokenizer, resolved_revision).

    quantization: "none" | "4bit" (QLoRA; bitsandbytes — CUDA GPUs only)."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = detect_device()
    kwargs: Dict[str, Any] = {"revision": revision} if revision else {}
    if quantization == "4bit":
        if device != "cuda":
            raise SystemExit("4-bit QLoRA needs a CUDA GPU (bitsandbytes is "
                             "CUDA-only). On CPU/Apple silicon use "
                             '"quantization": "none" with a 1.5–3B base model.')
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16)
    else:
        kwargs["torch_dtype"] = (torch.bfloat16 if device == "cuda" else torch.float32)

    tok = AutoTokenizer.from_pretrained(model_id, **({"revision": revision} if revision else {}))
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
    if quantization != "4bit":
        model.to(device)
    resolved = getattr(getattr(model, "config", None), "_commit_hash", None) \
        or revision or "unresolved"
    return model, tok, str(resolved)


def attach_lora(model, lora_cfg: Dict[str, Any], quantization: str):
    from peft import LoraConfig, get_peft_model
    if quantization == "4bit":
        try:
            from peft import prepare_model_for_kbit_training
            model = prepare_model_for_kbit_training(model)
        except Exception as e:
            print(f"[compat] prepare_model_for_kbit_training unavailable: {e}")
    cfg = safe_config(LoraConfig,
                      r=int(lora_cfg.get("r", 16)),
                      lora_alpha=int(lora_cfg.get("alpha", 32)),
                      lora_dropout=float(lora_cfg.get("dropout", 0.10)),
                      target_modules=lora_cfg.get(
                          "target_modules", ["q_proj", "k_proj", "v_proj", "o_proj"]),
                      bias="none", task_type="CAUSAL_LM")
    return get_peft_model(model, cfg)


def load_with_adapter(model_id: str, revision: Optional[str],
                      adapter_dir: Optional[str], quantization: str = "none"):
    """Base (+ optional promoted adapter) for inference/evaluation."""
    model, tok, resolved = load_base(model_id, revision, quantization)
    if adapter_dir:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter_dir)
    model.eval()
    return model, tok, resolved


def generate_greedy(model, tok, prompt: str, max_new_tokens: int = 700) -> str:
    """Deterministic greedy decoding (do_sample=False — the temperature-0
    analogue). Per the Reproducibility Statement: expected stable, but bit-
    identity across hardware/driver stacks is not claimed."""
    import torch
    messages = [{"role": "user", "content": prompt}]
    try:
        text = tok.apply_chat_template(messages, tokenize=False,
                                       add_generation_prompt=True)
    except Exception:
        text = prompt
    inputs = tok(text, return_tensors="pt", truncation=True,
                 max_length=4096).to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, do_sample=False,
                             max_new_tokens=max_new_tokens,
                             pad_token_id=tok.pad_token_id)
    return tok.decode(out[0][inputs["input_ids"].shape[1]:],
                      skip_special_tokens=True)
