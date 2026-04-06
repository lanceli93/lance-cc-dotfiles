---
name: skill-upgrade-helper
description: Manage and upgrade locally installed Claude Code skills. Use when the user wants to update/upgrade skills, install new skills, list installed skills, or manage skill installations. Triggers on phrases like "update skill", "upgrade skill", "install skill", "refresh skills", "manage skills".
---

# Skill Upgrade Helper

Manage skills from a curated remote catalog. Supports user-level and project-level targets, and works with both `.claude` and `.kiro` config directories.

## When this skill is triggered

**Step 1: Locate the upgrade script.** The script is at `scripts/upgrade.py` relative to this skill's directory. Find it by running:

```bash
find ~/.claude/skills ~/.kiro/skills .claude/skills .kiro/skills -path "*/skill-upgrade-helper/scripts/upgrade.py" 2>/dev/null | head -1
```

Save the result as `SCRIPT_PATH` for subsequent steps. If nothing is found, tell the user the skill-upgrade-helper is not installed.

**Step 2: Fetch current state.** Run:

```bash
uv run <SCRIPT_PATH> list --json
```

**Step 3: Parse the JSON output.** The output looks like:

```json
{
  "project_root": "/path/to/project or null",
  "skills": {
    "skill-name": {
      "repo": "https://github.com/...",
      "installed": ["user", "/path/to/project"]
    }
  }
}
```

**Step 4: Present ALL skills from the JSON to the user.** You MUST list every single skill from the `skills` object — do not skip or filter any. Format as a table:

- If `installed` is empty → status is "not installed"
- If `installed` contains `"user"` → show "✓ user"
- If `installed` contains a path → show "✓ project"

Example:

```
| #  | Skill                  | Status            |
|----|------------------------|-------------------|
| 1  | aws-excalidraw-diagram | ✓ user            |
| 2  | aws-html-slides        | not installed      |
| 3  | humanizer              | ✓ user  ✓ project |
| 4  | skill-creator          | ✓ user            |
| 5  | ui-ux-pro-max          | not installed      |
```

**Step 5: Ask the user two questions:**

1. Which skills to install or update? (by number, name, or "all")
2. Where to install? Only offer targets that apply:
   - **User level** — always available
   - **Project level** — only if `project_root` is not null

**Step 6: Execute.** For each skill + target the user chose, run:

```bash
uv run <SCRIPT_PATH> update <name> --target <user|project>
```

Report results as each completes.

## Quick shortcut

If the user's intent is unambiguous (e.g. "update all my skills"), skip the selection and run:

```bash
uv run <SCRIPT_PATH> update --all --target user
```
