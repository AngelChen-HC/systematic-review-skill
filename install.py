#!/usr/bin/env python3
"""install.py — automatic installer for the systematic-review-coordinator
skill (v8.0), including every script the skill needs.

ONE COMMAND, NO EXPERIENCE NEEDED. From a terminal:

    python3 install.py

and answer the questions. Or fully non-interactive, e.g.:

    python3 install.py --target claude-code --workspace ~/my_review --yes
    python3 install.py --target zip                    # builds the upload ZIP for claude.ai
    python3 install.py --workspace ~/my_review --with-finetune   # adds the Phase 5c stack

What it does (each step printed as it happens):
  1. Gets the skill files — from the folder you run it in (if you downloaded
     the repository) or, otherwise, by downloading the repository archive.
  2. Installs the SKILL to your chosen target:
       claude-code          → ~/.claude/skills/systematic-review-coordinator/
       claude-code-project  → ./.claude/skills/systematic-review-coordinator/
       zip                  → systematic-review-coordinator.zip (upload it in
                              claude.ai → Settings → Capabilities → Skills)
  3. (Optional) Sets up a REVIEW WORKSPACE: copies scripts/ + srlib/ there,
     creates the review_env virtual environment, installs the core Python
     libraries, and runs the built-in smoke test to prove everything works.
  4. (Optional, --with-finetune) Installs the Phase 5c fine-tuning stack
     (large download; only needed if you later OPT-IN at Gate 2c — you can
     always run this again later with --with-finetune).

Uses only Python's standard library. Python 3.9+ required.
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from datetime import datetime

REPO = "AngelChen-HC/systematic-review-skill"
TARBALL = f"https://codeload.github.com/{REPO}/tar.gz/refs/heads/main"
SKILL_NAME = "systematic-review-coordinator"
SKILL_FILES = ["SKILL.md", "README.md", "LICENSE", "INSTALL.md",
               "MIGRATION_v7_to_v8.md"]
SCRIPTS_DIR = "scripts"


def say(msg: str) -> None:
    print(f"\n==> {msg}")


def die(msg: str) -> None:
    sys.exit(f"\nERROR: {msg}\nNothing was left half-installed at this step. "
             "Paste this whole message to Claude and it will help you fix it.")


def find_source() -> str:
    """Local checkout if SKILL.md sits next to this script; else download."""
    here = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(here, "SKILL.md")):
        say(f"Using the skill files already next to this script: {here}")
        return here
    say(f"Downloading the skill repository ({REPO}) …")
    try:
        data = urllib.request.urlopen(TARBALL, timeout=120).read()
    except Exception as e:
        die(f"could not download {TARBALL} — are you online? ({e})")
    tmp = tempfile.mkdtemp(prefix="srsc_install_")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as t:
        t.extractall(tmp)  # trusted first-party archive
    root = next(os.path.join(tmp, d) for d in os.listdir(tmp)
                if os.path.isdir(os.path.join(tmp, d)))
    if not os.path.exists(os.path.join(root, "SKILL.md")):
        die("downloaded archive does not contain SKILL.md at its root")
    print(f"    downloaded and unpacked to {root}")
    return root


def assemble(src: str, dest_parent: str) -> str:
    """Build dest_parent/systematic-review-coordinator/ with skill + scripts."""
    dest = os.path.join(dest_parent, SKILL_NAME)
    if os.path.exists(dest):
        bak = dest + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        say(f"Existing install found — backing it up to {bak}")
        shutil.move(dest, bak)
    os.makedirs(dest)
    for f in SKILL_FILES:
        p = os.path.join(src, f)
        if os.path.exists(p):
            shutil.copy2(p, dest)
        elif f == "SKILL.md":
            die("SKILL.md missing from source")
        else:
            print(f"    (note: {f} not found in source — skipped)")
    sdir = os.path.join(src, SCRIPTS_DIR)
    if os.path.isdir(sdir):
        shutil.copytree(sdir, os.path.join(dest, SCRIPTS_DIR))
    else:
        print("    (note: scripts/ not found in source — the Phase 5c "
              "pipeline will not be available until it is)")
    return dest


def install_skill(src: str, target: str) -> None:
    if target == "zip":
        say("Building the claude.ai upload ZIP …")
        with tempfile.TemporaryDirectory() as tmp:
            folder = assemble(src, tmp)
            out = os.path.abspath(f"{SKILL_NAME}.zip")
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(folder):
                    for f in files:
                        full = os.path.join(root, f)
                        z.write(full, os.path.relpath(full, tmp))
        print(f"    created {out}")
        print("    NEXT: claude.ai → Settings → Capabilities (enable Code "
              "execution) → Skills → '+' → upload this ZIP → toggle ON.\n"
              "    The skill FOLDER must be at the ZIP root — this ZIP is "
              "built correctly.")
        return
    base = (os.path.join(os.path.expanduser("~"), ".claude", "skills")
            if target == "claude-code"
            else os.path.join(os.getcwd(), ".claude", "skills"))
    os.makedirs(base, exist_ok=True)
    dest = assemble(src, base)
    say(f"Skill installed for Claude Code at: {dest}")
    print("    NEXT: start a NEW Claude Code session and run /skills to "
          "confirm it is listed.")


def venv_python(ws: str) -> str:
    env = os.path.join(ws, "review_env")
    return os.path.join(env, "Scripts" if os.name == "nt" else "bin",
                        "python.exe" if os.name == "nt" else "python3")


def setup_workspace(src: str, ws: str, with_finetune: bool,
                    skip_deps: bool) -> None:
    ws = os.path.abspath(os.path.expanduser(ws))
    say(f"Setting up your review workspace at: {ws}")
    os.makedirs(ws, exist_ok=True)
    tgt_scripts = os.path.join(ws, SCRIPTS_DIR)
    if os.path.exists(tgt_scripts):
        shutil.rmtree(tgt_scripts)
    shutil.copytree(os.path.join(src, SCRIPTS_DIR), tgt_scripts)
    print(f"    scripts copied to {tgt_scripts}")

    env = os.path.join(ws, "review_env")
    if not os.path.exists(env):
        say("Creating the Python virtual environment (review_env) …")
        subprocess.run([sys.executable, "-m", "venv", env], check=True)
    py = venv_python(ws)

    def pip(args, fatal=False):
        r = subprocess.run([py, "-m", "pip"] + args)
        if r.returncode != 0:
            msg = ("    WARNING: that install did not finish. The skill has "
                   "built-in fallbacks (Phase 3) and will help you per phase "
                   "— you can continue.")
            if fatal:
                die(msg)
            print(msg)

    if not skip_deps:
        say("Installing the core libraries (a few minutes) …")
        pip(["install", "--upgrade", "pip"])
        pip(["install", "-r",
             os.path.join(tgt_scripts, "requirements-core.txt")])
        if with_finetune:
            say("Installing the OPTIONAL Phase 5c fine-tuning stack "
                "(large download — several GB, 10–30 min) …")
            print("    You only need this if you later OPT-IN at Gate 2c. "
                  "bitsandbytes is skipped automatically on Mac/CPU-only.")
            pip(["install", "-r",
                 os.path.join(tgt_scripts, "requirements-finetune.txt")])
    else:
        say("Skipping library installs (--skip-deps).")

    say("Verifying the pipeline with the built-in smoke test "
        "(no downloads, ~10 seconds) …")
    r = subprocess.run([py, os.path.join(tgt_scripts, "smoke_test.py")],
                       cwd=ws)
    if r.returncode == 0:
        print("    ✔ smoke test PASSED — audit chaining, Gate 2c "
              "enforcement, ground-truth leakage guard, and metrics all "
              "verified on this machine.")
    else:
        die("the smoke test failed — see the output above")

    say("Workspace ready. Your next steps:")
    act = ("review_env\\Scripts\\activate" if os.name == "nt"
           else "source review_env/bin/activate")
    print(f"""    1. cd {ws}
    2. {act}
    3. Open Claude and say: "Start a systematic review" — the skill takes
       over from there, gate by gate.
    Fine-tuning (Phase 5c) is OPTIONAL and OFF by default. If it is ever
    offered, Gate 2c will show you the full time/cost/data notice first:
       python3 scripts/decide_fine_tuning.py --config learned_alignment/adapter_training.json --show-notice""")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target",
                    choices=["claude-code", "claude-code-project", "zip",
                             "none"],
                    help="where to install the skill (default: ask)")
    ap.add_argument("--workspace",
                    help="also set up a review working directory here")
    ap.add_argument("--with-finetune", action="store_true",
                    help="also install the optional Phase 5c stack")
    ap.add_argument("--skip-deps", action="store_true",
                    help="workspace without installing libraries")
    ap.add_argument("--yes", action="store_true",
                    help="no prompts; defaults: --target claude-code")
    args = ap.parse_args()

    if sys.version_info < (3, 9):
        die("Python 3.9 or newer is required. See INSTALL.md for how to "
            "install Python.")

    src = find_source()
    target = args.target
    if target is None:
        if args.yes:
            target = "claude-code"
        else:
            print("\nWhere should the skill be installed?\n"
                  "  1) Claude Code, for me everywhere   (~/.claude/skills/)\n"
                  "  2) Claude Code, this project only   (./.claude/skills/)\n"
                  "  3) Build a ZIP to upload in claude.ai\n"
                  "  4) Skip — workspace only")
            target = {"1": "claude-code", "2": "claude-code-project",
                      "3": "zip", "4": "none"}.get(
                          input("Type 1, 2, 3 or 4: ").strip(), "claude-code")
    if target != "none":
        install_skill(src, target)

    ws = args.workspace
    if ws is None and not args.yes:
        a = input("\nSet up a review workspace (scripts + Python environment "
                  "+ self-test) now? [y/N]: ").strip().lower()
        if a == "y":
            ws = input("Workspace folder (e.g. ~/my_review): ").strip()
    if ws:
        setup_workspace(src, ws, args.with_finetune, args.skip_deps)

    say("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
