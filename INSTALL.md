# Installing the Systematic Review & Meta-Analysis Coordinator Skill (v8.0)

This guide covers every way to install this skill, step by step. **No coding experience is required.** The fastest route is the new **automatic installer (Option 0)** — one command does everything, including copying the Phase 5c fine-tuning scripts and setting up your Python workspace with a built-in self-test. The Claude.ai route (Option 1) remains a matter of one ZIP file. **New in v8:** the repository now ships all runtime scripts under `scripts/` (six pipeline scripts + `srlib/` + pinned requirements); every install route below includes them, because Phase 5c and the self-verification depend on them.

> **What is a "skill"?** A skill is a folder containing a `SKILL.md` file — structured instructions that Claude loads automatically when your request matches the skill's description. Once this skill is installed, simply asking Claude to *"help me run a systematic review"* or *"update my existing systematic review"* activates the full workflow.

---

## What you need before installing

| Route | Requirements |
|---|---|
| **Claude.ai / Claude apps** (Option 1) | A paid Claude plan (Pro, Max, Team, or Enterprise). Custom skill upload is not available on the Free plan. |
| **Claude Code** (Option 2) | Claude Code installed on your machine ([code.claude.com/docs](https://code.claude.com/docs/en/overview)). |
| **Claude API** (Option 3) | An Anthropic API account. For developers only. |

The skill itself has no software dependencies at install time. During a review it will guide you through installing Python and a small number of libraries — with complete beginner instructions and standard-library fallbacks built in.

---

## Option 0 — Automatic installation (one command) · *new in v8, easiest*

`install.py` is a standard-library-only Python script that performs the whole installation for you and verifies it worked. It needs Python 3.9+ (see python.org/downloads, or the skill's own Phase 3 guidance).

**Interactive (recommended — it asks you everything):**

```bash
# macOS / Linux
curl -O https://raw.githubusercontent.com/AngelChen-HC/systematic-review-skill/main/install.py
python3 install.py
```

```powershell
# Windows (PowerShell)
Invoke-WebRequest https://raw.githubusercontent.com/AngelChen-HC/systematic-review-skill/main/install.py -OutFile install.py
python install.py
```

**Non-interactive examples:**

```bash
python3 install.py --target claude-code --workspace ~/my_review --yes   # Claude Code + workspace
python3 install.py --target zip                                         # just build the claude.ai ZIP
python3 install.py --workspace ~/my_review --with-finetune              # workspace incl. Phase 5c stack
```

**What it does, step by step (each printed as it runs):**

1. Downloads the repository (or uses local files if you already cloned/unzipped it).
2. Installs the **skill** — `SKILL.md`, docs, **and the full `scripts/` folder** — to your chosen target: `~/.claude/skills/systematic-review-coordinator/` (Claude Code, personal), `./.claude/skills/…` (project), or a correctly-structured `systematic-review-coordinator.zip` for claude.ai upload. Any existing install is backed up, never overwritten.
3. Optionally sets up your **review workspace**: copies `scripts/` there, creates the `review_env` virtual environment, and installs the core libraries (`scripts/requirements-core.txt`). Failed library installs are non-fatal — the skill has per-phase fallbacks.
4. Optionally (`--with-finetune`) installs the **Phase 5c fine-tuning stack** (`scripts/requirements-finetune.txt`, pinned; several GB). You do **not** need this now: it is only used if you later opt in at Gate 2c, and you can re-run `python3 install.py --workspace <same folder> --with-finetune` at that point.
5. **Self-verifies** by running the built-in smoke test in your new environment — proving on your machine that audit hash-chaining, the Gate 2c opt-in enforcement, the ground-truth leakage guard, and the metrics all work. It ends with `ALL SMOKE TESTS PASSED` and tells you exactly what to do next.

| Flag | Meaning |
|---|---|
| `--target claude-code / claude-code-project / zip / none` | where the skill itself goes |
| `--workspace PATH` | also set up a review working directory there |
| `--with-finetune` | additionally install the optional Phase 5c stack |
| `--skip-deps` | workspace without library installs |
| `--yes` | no questions (defaults to `--target claude-code`) |

> If anything fails, the script stops with a plain-language message and the instruction to paste it to Claude — which will walk you through the fix.

---

## Option 1 — Claude.ai (web, desktop, and mobile apps) · *recommended for researchers*

### Step 1: Turn on the required capability

1. Open [claude.ai](https://claude.ai) and sign in.
2. Go to **Settings → Capabilities**.
3. Make sure **Code execution and file creation** is turned **on**. Skills do not run without it.
   - **Team/Enterprise plans:** an organization Owner must first enable both **Code execution and file creation** and **Skills** under **Organization settings → Skills**. If skills appear greyed out for you, this is why — contact your Owner.

### Step 2: Get the skill ZIP

**Either** download the release ZIP from this repository (if one is attached under *Releases*), **or** build it yourself in four commands:

**Easiest:** let the installer build it — `python3 install.py --target zip` (Option 0) — or by hand:

```bash
git clone https://github.com/AngelChen-HC/systematic-review-skill.git
cd systematic-review-skill
mkdir -p systematic-review-coordinator
cp SKILL.md README.md LICENSE INSTALL.md MIGRATION_v7_to_v8.md systematic-review-coordinator/
cp -r scripts systematic-review-coordinator/
zip -r systematic-review-coordinator.zip systematic-review-coordinator
```

> ⚠️ **The one gotcha:** the ZIP must contain the **skill folder itself at its root** (a folder named `systematic-review-coordinator/` containing `SKILL.md`), **not** the bare files. Uploading a ZIP whose root is `SKILL.md` directly will fail validation. The commands above produce the correct structure:
>
> ```
> systematic-review-coordinator.zip
> └── systematic-review-coordinator/
>     ├── SKILL.md      ← required
>     ├── README.md
>     ├── LICENSE
>     ├── INSTALL.md
>     ├── MIGRATION_v7_to_v8.md
>     └── scripts/      ← v8: the six pipeline scripts + srlib/ + pinned
>                          requirements — include them, or Phase 5c and the
>                          self-test will be unavailable
> ```

**No terminal? No problem.** Download this repository as a ZIP (green **Code** button → **Download ZIP**), unzip it, rename the resulting folder to `systematic-review-coordinator`, and re-zip **that folder** (right-click → *Compress* on Mac, *Send to → Compressed folder* on Windows).

### Step 3: Upload

1. In Claude.ai, go to **Settings → Customize → Skills** (on some plans this appears as **Capabilities → Skills**).
2. Click the **“+”** button → **Create skill** → **Upload** the ZIP file.
3. The skill appears in your skills list. Make sure its toggle is **on**.

Custom skills you upload this way are **private to your account**. On Team/Enterprise plans, an Owner can additionally share or provision the skill organization-wide from the same Skills settings.

### Step 4: Verify it works

Start a **new** conversation and type:

> *"I want to conduct a systematic review on [your topic]."*

Claude should immediately begin with the skill's **Phase 0 Mode Selector**, asking whether this is a **NEW review or an UPDATE** of an existing one, followed by the kickoff decision checklist. If it does, the skill is installed and triggering correctly.

---

## Option 2 — Claude Code (terminal / VS Code / JetBrains)

Skills in Claude Code are plain folders on disk. Two locations:

| Scope | Location | Use when |
|---|---|---|
| **Personal** (all your projects) | `~/.claude/skills/systematic-review-coordinator/` | You want the skill available everywhere — the usual choice |
| **Project** (one repository, shared with collaborators who clone it) | `<repo>/.claude/skills/systematic-review-coordinator/` | A review team shares one project repo |

### Personal install (macOS / Linux)

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/AngelChen-HC/systematic-review-skill.git ~/.claude/skills/systematic-review-coordinator
```

Or, if you already cloned the repo elsewhere:

```bash
mkdir -p ~/.claude/skills/systematic-review-coordinator
cp /path/to/repo/SKILL.md /path/to/repo/README.md /path/to/repo/LICENSE ~/.claude/skills/systematic-review-coordinator/
```

### Personal install (Windows, PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
git clone https://github.com/AngelChen-HC/systematic-review-skill.git "$HOME\.claude\skills\systematic-review-coordinator"
```

### Project install

```bash
mkdir -p .claude/skills
git clone https://github.com/AngelChen-HC/systematic-review-skill.git .claude/skills/systematic-review-coordinator
# commit .claude/skills/ so collaborators get the skill when they clone
```

### Verify

Start a **new** Claude Code session in any directory (project scope: inside that repo), then either:

- run `/skills` and confirm `systematic-review-coordinator` is listed, or
- ask: *"Help me plan a systematic review update"* — Claude should read the skill and open with the Phase 0 mode selector.

> **Folder name matters.** The directory must be named `systematic-review-coordinator` (matching the `name` field in the SKILL.md frontmatter) and contain `SKILL.md` at its top level — not nested inside another folder such as `systematic-review-skill-main/`.

---

## Option 3 — Claude API (developers)

Custom skills can be uploaded and used programmatically via the Skills API. Two constraints to know: all Python dependencies must be pre-installed in the execution container (API skills cannot `pip install` at runtime), and the skill's human-in-the-loop gates mean your application must surface every approval step to a human reviewer — this skill is **not** designed to run unattended. See the [Skills API documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) and quickstart for current endpoints and packaging requirements.

---

## Setting up the fine-tuning pipeline (Phase 5c) — optional, and never required

Phase 5c is **off by default** and only ever starts after your informed opt-in at **Gate 2c** (the skill shows you the full time / cost / data / effectiveness notice first; opting out is a fully valid, logged answer). If and when you opt in, the pipeline needs three things, all of which Option 0 can do for you:

```bash
# in your review workspace, with review_env active
pip install -r scripts/requirements-finetune.txt      # pinned stack; several GB; bitsandbytes auto-skipped on Mac/CPU
python3 scripts/smoke_test.py                          # ~10 s self-test, no downloads — expect ALL SMOKE TESTS PASSED
python3 scripts/decide_fine_tuning.py --config learned_alignment/adapter_training.json --show-notice   # read the Gate 2c notice any time
```

The pipeline then runs in this fixed order, each script printing what to do next: `decide_fine_tuning.py` (Gate 2c) → `build_training_set.py` → `train_adapter.py` → `evaluate_adapter.py` → `promote_adapter.py` (Gate 5c) → `screen_with_adapter.py`. The first two training scripts **refuse to run** without your logged Gate 2c opt-in, and nothing an adapter produces bypasses any human gate. The base model (default Qwen2.5-1.5B-Instruct; larger tiers if you have a GPU) is downloaded once from Hugging Face on first use — it is not in this repository, and nothing of yours is ever uploaded anywhere.

---

## Updating to a new version

- **Claude.ai:** delete the old skill from **Settings → Customize → Skills**, then upload the new ZIP (Steps 2–3 above). Re-verify with a new conversation.
- **Claude Code:** `cd ~/.claude/skills/systematic-review-coordinator && git pull` (or replace the folder), then start a new session.
- **Mid-review warning:** the skill's audit log records `prompt_version` (e.g., v8.0) on every entry. Upgrading mid-review is now a defined procedure (v8, "Upgrading Mid-Review"): an in-flight, human-audited screen **stays on the version it began under**, new capabilities are adopted only at clean phase/batch boundaries, and you record one `skill_version_customisation` audit entry stating which phases run under which version. See `MIGRATION_v7_to_v8.md` for exactly what carries forward from v7 (short answer: everything; adapters start cold; no re-screening obligation is created).

---

## Uninstalling / disabling

- **Claude.ai:** toggle the skill off in **Settings → Customize → Skills**, or delete it from the list.
- **Claude Code:** delete the folder (`rm -rf ~/.claude/skills/systematic-review-coordinator`), or temporarily disable it by renaming (`mv systematic-review-coordinator _systematic-review-coordinator`).

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Skill upload rejected in Claude.ai | Check the ZIP structure: the skill **folder** (containing `SKILL.md`) must be at the ZIP root — see the gotcha in Option 1, Step 2. |
| Skills menu greyed out / missing | Enable **Code execution and file creation** in **Settings → Capabilities** (Free/Pro/Max) or ask your org Owner to enable Skills at **Organization settings → Skills** (Team/Enterprise). |
| Skill installed but never triggers | Start a **new** conversation (skills load per-conversation). Phrase the request in the skill's terms: "systematic review", "literature search", "update my review", "PRISMA". Confirm the toggle is on. |
| Claude Code doesn't list the skill | Confirm the path is exactly `~/.claude/skills/systematic-review-coordinator/SKILL.md` (no extra nesting), then start a fresh session. |
| Claude answers generically instead of starting Phase 0 | The skill may be competing with a very short prompt. Be explicit once: *"Use the systematic-review-coordinator skill to start my review."* |
| Errors while running the review itself (Python, SSL, database access) | These are handled **inside** the skill: see its Python Environment Setup, Network Environment Check, and Environment-Fragility Fallbacks (Phase 3). |
| `install.py` says Python 3.9+ required | Install a current Python from https://www.python.org/downloads/ (tick "Add Python to PATH" on Windows), reopen the terminal, retry. |
| `install.py` cannot download the repository | You may be behind an institutional proxy/SSL inspection. Download the repo ZIP in your browser instead (green **Code** button → Download ZIP), unzip it, and run `python3 install.py` from **inside** that folder — it uses the local files without downloading. |
| Smoke test fails during install | Paste the full output to Claude. It runs entirely offline on the standard library, so a failure usually means a truncated copy of `scripts/` — re-run the installer. |
| `bitsandbytes` fails during `--with-finetune` | Expected on Mac/CPU-only machines (it is CUDA-only and marked to auto-skip); if it still errors, delete its line from `scripts/requirements-finetune.txt` and keep `"quantization": "none"`. |

---

## Sources for the installation procedures above

- Using skills in Claude (Claude.ai upload, plan requirements, org settings): https://support.claude.com/en/articles/12512180-use-skills-in-claude
- How to create custom skills (skill/ZIP structure): https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
- Claude Code skills (personal and project directories): https://code.claude.com/docs/en/skills
- Anthropic skills repository and Agent Skills standard: https://github.com/anthropics/skills · https://agentskills.io

Product interfaces change; if a menu name here has moved, the support articles above are the authoritative, current reference.
