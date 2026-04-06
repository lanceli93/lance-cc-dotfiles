#!/usr/bin/env python3
"""Skill upgrade helper – registry-backed installer."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

REGISTRY_URL = (
    "https://raw.githubusercontent.com/lanceli93/my-claude-home"
    "/main/skill-upgrade-helper/registry.json"
)
LOCAL_REGISTRY = Path(__file__).resolve().parent.parent / "registry.json"

# Supported config directory names (Claude uses .claude, Kiro uses .kiro, etc.)
CONFIG_DIRS = [".claude", ".kiro"]


def _user_skills_dirs() -> list[Path]:
    """Return all existing user-level skills directories."""
    home = Path.home()
    return [home / d / "skills" for d in CONFIG_DIRS if (home / d / "skills").exists()]


def _project_skills_dirs(project_root: Path) -> list[Path]:
    """Return all existing project-level skills directories."""
    return [
        project_root / d / "skills"
        for d in CONFIG_DIRS
        if (project_root / d / "skills").exists()
    ]


def _all_targets(project_root: Path | None) -> list[dict]:
    """Return all available install targets with labels and paths."""
    targets = []
    home = Path.home()
    for d in CONFIG_DIRS:
        p = home / d / "skills"
        if p.exists():
            targets.append({"label": f"user ({d})", "path": str(p)})
    if project_root:
        for d in CONFIG_DIRS:
            p = project_root / d / "skills"
            if p.exists():
                targets.append({"label": f"project ({d})", "path": str(p)})
    return targets


def fetch_registry() -> dict:
    """Fetch skill catalog from remote, fall back to local bundled copy."""
    try:
        resp = urllib.request.urlopen(REGISTRY_URL, timeout=10)
        return json.loads(resp.read())
    except Exception:
        if LOCAL_REGISTRY.exists():
            return json.loads(LOCAL_REGISTRY.read_text())
        return {}


def find_project_root() -> Path | None:
    """Find project root by checking for .git, .claude, or .kiro directories."""
    # Try git first
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            return Path(r.stdout.strip())
    except Exception:
        pass

    # Walk up from cwd looking for config dirs
    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        for d in CONFIG_DIRS:
            if (parent / d).is_dir():
                return parent

    return None


def scan_installed() -> dict[str, list[str]]:
    """Scan user and project skill dirs across all config directories.

    Returns {name: [loc, ...]} where loc is "user" or a project root path.
    """
    found: dict[str, list[str]] = {}

    for sdir in _user_skills_dirs():
        for d in sdir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                if "user" not in found.get(d.name, []):
                    found.setdefault(d.name, []).append("user")

    proj = find_project_root()
    if proj:
        for sdir in _project_skills_dirs(proj):
            for d in sdir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists():
                    proj_str = str(proj)
                    if proj_str not in found.get(d.name, []):
                        found.setdefault(d.name, []).append(proj_str)

    return found


def pull_skill(name: str, info: dict, target_dir: Path) -> bool:
    """Clone repo into a temp dir and copy the skill subdirectory to target."""
    dest = target_dir / name
    with tempfile.TemporaryDirectory() as tmp:
        print(f"  Cloning {info['repo']} ...")
        r = subprocess.run(
            ["git", "clone", "--depth", "1", info["repo"], tmp],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            print(f"  FAILED: {r.stderr.strip()}")
            return False

        src = Path(tmp) / info["path"]
        if not src.exists():
            print(f"  FAILED: path '{info['path']}' not found in repo")
            return False

        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest)
        print(f"  ✓ {name} → {dest}")
        return True


def _loc_label(loc: str) -> str:
    return "user" if loc == "user" else f"project({Path(loc).name})"


def cmd_list(as_json: bool = False):
    """List all available skills and their install status."""
    registry = fetch_registry()
    installed = scan_installed()
    project_root = find_project_root()

    if as_json:
        result = {
            "project_root": str(project_root) if project_root else None,
            "available_targets": _all_targets(project_root),
            "skills": {},
        }
        for name in sorted(registry):
            result["skills"][name] = {
                "repo": registry[name]["repo"],
                "installed": installed.get(name, []),
            }
        print(json.dumps(result))
        return

    if not registry:
        print("Registry is empty.")
        return

    for name in sorted(registry):
        locs = installed.get(name, [])
        status = ", ".join(_loc_label(l) for l in locs) if locs else "not installed"
        print(f"  {name}  [{status}]")
        print(f"    repo: {registry[name]['repo']}")


def cmd_update(name: str | None, target: str, all_: bool):
    """Update one or all skills to the specified target.

    target can be an absolute path to a skills directory (from available_targets).
    """
    registry = fetch_registry()
    td = Path(target)

    if all_:
        names = list(registry)
    elif name:
        names = [name]
    else:
        sys.exit("Specify a skill name or --all.")

    ok = total = 0
    for n in names:
        if n not in registry:
            print(f"  Not in registry: {n}")
            continue
        total += 1
        ok += pull_skill(n, registry[n], td)

    print(f"\nDone — {ok}/{total} succeeded.")


def main():
    p = argparse.ArgumentParser(description="Skill upgrade helper")
    sub = p.add_subparsers(dest="command")

    ls = sub.add_parser("list", help="List available and installed skills")
    ls.add_argument("--json", action="store_true", dest="as_json",
                    help="Output as JSON for programmatic use")

    up = sub.add_parser("update", help="Update skill(s)")
    up.add_argument("name", nargs="?")
    up.add_argument("--all", action="store_true", dest="all_")
    up.add_argument(
        "--target",
        required=True,
        help="Absolute path to skills directory (from 'list --json' available_targets)",
    )

    args = p.parse_args()

    match args.command:
        case "list":
            cmd_list(as_json=args.as_json)
        case "update":
            cmd_update(args.name, args.target, args.all_)
        case _:
            p.print_help()


if __name__ == "__main__":
    main()
