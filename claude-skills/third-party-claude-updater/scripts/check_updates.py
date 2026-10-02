#!/usr/bin/env python3
"""Check and optionally apply updates for third-party Claude Code plugins and skills.

Safe updates are applied only with --apply-safe. Everything else is reported for
manual review. Never pushes, never deletes a dirty worktree.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path.home()
SKILLS = HOME / ".claude" / "skills"
CODEX_SKILLS = HOME / ".codex" / "skills"
CLONE_ROOT = Path(
    os.environ.get("CLAUDE_THIRD_PARTY_CLONE_ROOT")
    or (HOME / "Documents" / "Codex")
).expanduser()
CLAUDE = shutil.which("claude") or str(HOME / ".local" / "bin" / "claude")


def run(cmd, cwd=None, timeout=180):
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as exc:
        return {"cmd": " ".join(cmd), "code": 127, "out": "", "err": str(exc)}
    return {
        "cmd": " ".join(cmd),
        "code": p.returncode,
        "out": p.stdout.strip(),
        "err": p.stderr.strip(),
    }


def git(repo, *args, timeout=180):
    return run(["git", "-C", str(repo), *args], timeout=timeout)


def clean(repo):
    r = git(repo, "status", "--short")
    return r["code"] == 0 and not r["out"]


def semver(tag):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)", str(tag))
    return tuple(map(int, m.groups())) if m else None


def latest_tag(url):
    r = run(["git", "ls-remote", "--tags", "--refs", url], timeout=120)
    if r["code"] != 0:
        return None, r["err"] or "ls-remote failed"
    tags = [ln.split("refs/tags/")[-1] for ln in r["out"].splitlines() if "refs/tags/" in ln]
    ranked = sorted(((semver(t), t) for t in tags if semver(t)), reverse=True)
    return (ranked[0][1] if ranked else None), None


def fetch_json(url, timeout=30):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return None, str(exc)


def pypi_latest(package):
    data, err = fetch_json(f"https://pypi.org/pypi/{package}/json")
    if err:
        return None, err
    return data.get("info", {}).get("version"), None


def npm_latest(package):
    r = run(["npm", "view", package, "version"], timeout=120)
    if r["code"] != 0:
        return None, r["err"] or "npm view failed"
    return r["out"], None


def add(results, name, status, detail="", **extra):
    item = {"name": name, "status": status}
    if detail:
        item["detail"] = detail
    item.update({k: v for k, v in extra.items() if v is not None})
    results.append(item)


def version_status(current, latest):
    if not current or not latest:
        return "unknown"
    c, l = semver(current), semver(latest)
    if c and l:
        return "current" if c >= l else "update-available"
    return "current" if str(current).lstrip("v") == str(latest).lstrip("v") else "update-available"


# --- marketplace plugins -----------------------------------------------------

def installed_plugin_version(plugin):
    r = run([CLAUDE, "plugin", "details", plugin], timeout=120)
    if r["code"] != 0:
        return None
    m = re.search(rf"^{re.escape(plugin)}\s+(\S+)", r["out"], re.M)
    return m.group(1) if m else None


def update_marketplace_plugin(results, plugin, marketplace, apply_safe):
    before = installed_plugin_version(plugin)
    if before is None:
        add(results, plugin, "not-installed",
            f"install with: claude plugin install {plugin}@{marketplace}")
        return
    if not apply_safe:
        add(results, plugin, "check-only",
            "run with --apply-safe to refresh the marketplace and update", current=before)
        return
    mr = run([CLAUDE, "plugin", "marketplace", "update", marketplace], timeout=300)
    if mr["code"] != 0:
        add(results, plugin, "blocked", f"marketplace update failed: {mr['err'][:200]}", current=before)
        return
    ur = run([CLAUDE, "plugin", "update", plugin], timeout=300)
    after = installed_plugin_version(plugin)
    if ur["code"] != 0:
        add(results, plugin, "blocked", f"plugin update failed: {ur['err'][:200]}", current=before)
        return
    if after and before and after != before:
        add(results, plugin, "updated", "restart Claude Code to load the new version",
            current=after, previous=before)
    else:
        add(results, plugin, "current", "", current=after or before)


# --- individual checks -------------------------------------------------------

def check_ocr(results):
    if not shutil.which("ocr"):
        add(results, "ocr", "not-installed",
            "install with: npm install -g @alibaba-group/open-code-review")
        return
    r = run(["ocr", "--version"], timeout=60)
    m = re.search(r"v?(\d+\.\d+\.\d+)", r["out"])
    current = m.group(1) if m else None
    latest, err = npm_latest("@alibaba-group/open-code-review")
    if err:
        add(results, "ocr", "unknown", f"registry lookup failed: {err[:120]}", current=current)
        return
    add(results, "ocr", version_status(current, latest),
        "update with: npm install -g @alibaba-group/open-code-review",
        current=current, latest=latest)


def check_archify(results):
    path = SKILLS / "archify"
    release = path / "skill-release.json"
    if not release.exists():
        add(results, "archify", "not-installed",
            "install with: npx -y skills add tt-a1i/archify --skill archify "
            "--agent claude-code --global --copy --yes")
        return
    try:
        meta = json.loads(release.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        add(results, "archify", "unknown", f"unreadable skill-release.json: {exc}", path=str(path))
        return
    current = meta.get("version")
    manifest_url = meta.get("updateManifestUrl")
    latest = None
    if manifest_url:
        data, err = fetch_json(manifest_url)
        if err:
            add(results, "archify", "unknown", f"manifest fetch failed: {err[:120]}",
                current=current, path=str(path))
            return
        latest = data.get("version") or (data.get("latest") or {}).get("version")
    add(results, "archify", version_status(current, latest),
        "manual: re-running the vendor installer overwrites ~/.claude/skills/archify; "
        "confirm no local edits first",
        current=current, latest=latest, path=str(path))


def check_graphify(results, apply_safe):
    if not shutil.which("graphify"):
        add(results, "graphify", "not-installed", "install with: uv tool install graphifyy")
        return
    lst = run(["uv", "tool", "list"], timeout=60)
    m = re.search(r"^graphifyy v([\d.]+)", lst["out"], re.M)
    current = m.group(1) if m else None
    latest, err = pypi_latest("graphifyy")
    if err:
        add(results, "graphify", "unknown", f"pypi lookup failed: {err[:120]}", current=current)
        return
    status = version_status(current, latest)
    if status != "update-available" or not apply_safe:
        add(results, "graphify", status,
            "" if status == "current" else "run with --apply-safe to upgrade and reinstall the skill",
            current=current, latest=latest)
        return
    up = run(["uv", "tool", "upgrade", "graphifyy"], timeout=600)
    if up["code"] != 0:
        add(results, "graphify", "blocked", f"uv upgrade failed: {up['err'][:200]}",
            current=current, latest=latest)
        return
    inst = run(["graphify", "install", "--platform", "claude"], timeout=300)
    if inst["code"] != 0:
        add(results, "graphify", "blocked", f"skill reinstall failed: {inst['err'][:200]}",
            current=latest, latest=latest)
        return
    add(results, "graphify", "updated",
        "vendor installer rewrote ~/.claude/skills/graphify and its CLAUDE.md registration",
        current=latest, previous=current)


def check_aside(results):
    if not shutil.which("aside"):
        add(results, "aside", "not-installed", "Aside CLI is not on PATH")
        return
    r = run(["aside", "--version"], timeout=60)
    current = r["out"].splitlines()[0] if r["out"] else None
    mcp = run([CLAUDE, "mcp", "get", "aside"], timeout=120)
    registered = "Connected" in mcp["out"] or "Scope" in mcp["out"]
    add(results, "aside", "manual-review",
        "update with `aside --update`; the same binary serves the running `aside mcp` server, "
        "so leave the update to the user",
        current=current, mcp_registered=registered)


def ensure_tag_clone(results, name, url, apply_safe):
    latest, err = latest_tag(url)
    if err or not latest:
        add(results, name, "unknown", f"tag lookup failed: {(err or 'no semver tags')[:120]}")
        return
    existing = sorted(CLONE_ROOT.glob(f"{name}-{latest}-*"))
    dest = existing[0] if existing else CLONE_ROOT / f"{name}-{latest}-upstream"
    if dest.exists():
        add(results, name, "current" if clean(dest) else "manual-review",
            "clean tag clone present" if clean(dest) else "clone has local modifications; left untouched",
            latest=latest, path=str(dest))
        return
    if not apply_safe:
        add(results, name, "update-available",
            "run with --apply-safe to create a clean tag clone for comparison", latest=latest)
        return
    CLONE_ROOT.mkdir(parents=True, exist_ok=True)
    r = run(["git", "clone", "--branch", latest, "--depth", "1", url, str(dest)], timeout=600)
    add(results, name, "clone-created" if r["code"] == 0 else "clone-failed",
        r["err"][:200] if r["code"] != 0 else "comparison clone only; nothing installed",
        latest=latest, path=str(dest))


def check_ported_skills(results):
    for name in ("aside-workflow", "general-review-loop", "route-developer-review",
                 "third-party-claude-updater"):
        mine = SKILLS / name / "SKILL.md"
        if not mine.exists():
            add(results, name, "not-installed", f"expected at {mine}")
            continue
        origin_name = "third-party-codex-updater" if name == "third-party-claude-updater" else name
        origin = CODEX_SKILLS / origin_name / "SKILL.md"
        if not origin.exists():
            add(results, name, "manual-review",
                "locally authored; no upstream and no codex counterpart", path=str(mine.parent))
            continue
        drifted = mine.read_text() != origin.read_text()
        add(results, name, "manual-review",
            f"port of ~/.codex/skills/{origin_name}; "
            + ("content differs, as expected for a port — review both sides before syncing"
               if drifted else "content is identical to the codex original; the port may be unadapted"),
            path=str(mine.parent))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-safe", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = []
    update_marketplace_plugin(results, "ponytail", "ponytail", args.apply_safe)
    update_marketplace_plugin(results, "open-code-review", "open-code-review", args.apply_safe)
    update_marketplace_plugin(results, "i-have-adhd", "i-have-adhd", args.apply_safe)
    check_ocr(results)
    check_archify(results)
    check_graphify(results, args.apply_safe)
    check_aside(results)
    ensure_tag_clone(results, "codebase-memory-mcp",
                     "https://github.com/DeusData/codebase-memory-mcp.git", args.apply_safe)
    ensure_tag_clone(results, "superpowers",
                     "https://github.com/obra/superpowers.git", args.apply_safe)
    check_ported_skills(results)

    if args.json:
        print(json.dumps({"apply_safe": args.apply_safe, "results": results},
                         ensure_ascii=False, indent=2))
        return
    for item in results:
        detail = f" - {item['detail']}" if item.get("detail") else ""
        ver = ""
        if item.get("current") or item.get("latest"):
            ver = f" [{item.get('current', '?')} -> {item.get('latest', '?')}]"
        print(f"{item['name']}: {item['status']}{ver}{detail}")


if __name__ == "__main__":
    main()
