# Installing the Systematic Review & Meta-Analysis Coordinator Skill (v7.0)

This guide covers every way to install this skill, step by step. **No coding experience is required** for the Claude.ai route (Option 1) — it is a matter of downloading one ZIP file and uploading it.

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

## Option 1 — Claude.ai (web, desktop, and mobile apps) · *recommended for researchers*

### Step 1: Turn on the required capability

1. Open [claude.ai](https://claude.ai) and sign in.
2. Go to **Settings → Capabilities**.
3. Make sure **Code execution and file creation** is turned **on**. Skills do not run without it.
   - **Team/Enterprise plans:** an organization Owner must first enable both **Code execution and file creation** and **Skills** under **Organization settings → Skills**. If skills appear greyed out for you, this is why — contact your Owner.

### Step 2: Get the skill ZIP

**Either** download the release ZIP from this repository (if one is attached under *Releases*), **or** build it yourself in four commands:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
mkdir -p systematic-review-coordinator && cp SKILL.md README.md LICENSE systematic-review-coordinator/
zip -r systematic-review-coordinator.zip systematic-review-coordinator
```

> ⚠️ **The one gotcha:** the ZIP must contain the **skill folder itself at its root** (a folder named `systematic-review-coordinator/` containing `SKILL.md`), **not** the bare files. Uploading a ZIP whose root is `SKILL.md` directly will fail validation. The commands above produce the correct structure:
>
> ```
> systematic-review-coordinator.zip
> └── systematic-review-coordinator/
>     ├── SKILL.md      ← required
>     ├── README.md
>     └── LICENSE
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
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git ~/.claude/skills/systematic-review-coordinator
```

Or, if you already cloned the repo elsewhere:

```bash
mkdir -p ~/.claude/skills/systematic-review-coordinator
cp /path/to/repo/SKILL.md /path/to/repo/README.md /path/to/repo/LICENSE ~/.claude/skills/systematic-review-coordinator/
```

### Personal install (Windows, PowerShell)

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills" | Out-Null
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git "$HOME\.claude\skills\systematic-review-coordinator"
```

### Project install

```bash
mkdir -p .claude/skills
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git .claude/skills/systematic-review-coordinator
# commit .claude/skills/ so collaborators get the skill when they clone
```

### Verify

Start a **new** Claude Code session in any directory (project scope: inside that repo), then either:

- run `/skills` and confirm `systematic-review-coordinator` is listed, or
- ask: *"Help me plan a systematic review update"* — Claude should read the skill and open with the Phase 0 mode selector.

> **Folder name matters.** The directory must be named `systematic-review-coordinator` (matching the `name` field in the SKILL.md frontmatter) and contain `SKILL.md` at its top level — not nested inside another folder such as `YOUR-REPO-NAME-main/`.

---

## Option 3 — Claude API (developers)

Custom skills can be uploaded and used programmatically via the Skills API. Two constraints to know: all Python dependencies must be pre-installed in the execution container (API skills cannot `pip install` at runtime), and the skill's human-in-the-loop gates mean your application must surface every approval step to a human reviewer — this skill is **not** designed to run unattended. See the [Skills API documentation](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) and quickstart for current endpoints and packaging requirements.

---

## Updating to a new version

- **Claude.ai:** delete the old skill from **Settings → Customize → Skills**, then upload the new ZIP (Steps 2–3 above). Re-verify with a new conversation.
- **Claude Code:** `cd ~/.claude/skills/systematic-review-coordinator && git pull` (or replace the folder), then start a new session.
- **Mid-review warning:** the skill's audit log records `prompt_version` (e.g., v7.0) on every entry. If you upgrade the skill in the middle of a live review, this is a protocol-relevant change — log it as a deviation in your audit log, exactly as the skill requires for any other change to the screening instructions.

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

---

## Sources for the installation procedures above

- Using skills in Claude (Claude.ai upload, plan requirements, org settings): https://support.claude.com/en/articles/12512180-use-skills-in-claude
- How to create custom skills (skill/ZIP structure): https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
- Claude Code skills (personal and project directories): https://code.claude.com/docs/en/skills
- Anthropic skills repository and Agent Skills standard: https://github.com/anthropics/skills · https://agentskills.io

Product interfaces change; if a menu name here has moved, the support articles above are the authoritative, current reference.
