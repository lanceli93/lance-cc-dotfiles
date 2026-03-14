# Claude Toolkit

My Claude Code configurations and skills, for easy setup on new machines.

## Structure

```
config/
  CLAUDE.md                  # Global instructions (~/.claude/CLAUDE.md)
  settings.template.json     # Settings template — fill in secrets before use
skills/
  openclaw/                  # Custom skills (full source)
```

## Setup

1. Clone this repo
2. Copy `config/CLAUDE.md` to `~/.claude/CLAUDE.md`
3. Copy `config/settings.template.json` to `~/.claude/settings.json`, fill in API keys
4. Copy or symlink `skills/*` to `~/.claude/skills/`
5. Install community skills (see below)

## Community Skills

Third-party skills I use. Install via `git clone` into `~/.claude/skills/`.

### humanizer

- **Repo**: https://github.com/blader/humanizer
- **Install**: `git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer`
- Remove signs of AI-generated writing. Based on Wikipedia's "Signs of AI writing" guide
- Works great for English; less effective for Chinese

### skill-creator

- **Repo**: https://github.com/anthropics/skills/tree/main/skills/skill-creator
- **Install**: `git clone https://github.com/anthropics/skills.git /tmp/skills && cp -r /tmp/skills/skills/skill-creator ~/.claude/skills/skill-creator && rm -rf /tmp/skills`
- Create, test, and optimize skills with built-in eval framework
- The benchmark and variance analysis features are useful for measuring trigger accuracy

### ui-ux-pro-max

- **Repo**: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Install**: `npm install -g uipro-cli && cd <project> && uipro init --ai claude` (per-project) or move to `~/.claude/skills/` for global
- AI-driven UI/UX design intelligence: 67 styles, 161 industry reasoning rules, 57 font pairings
- Auto-generates complete design system (pattern + style + colors + typography) based on product type
- Supports React, Next.js, Vue, Svelte, SwiftUI, Flutter, Tailwind, etc.
