#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(
    os.environ.get("CODEX_PERSONAL_SKILLS_ROOT")
    or (Path.home() / "Documents" / "Codex")
).expanduser()
HOME = Path.home()


def run(cmd, cwd=None, timeout=120):
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    return {
        "cmd": " ".join(cmd),
        "code": p.returncode,
        "out": p.stdout.strip(),
        "err": p.stderr.strip(),
    }


def git(repo, *args, timeout=120):
    return run(["git", "-C", str(repo), *args], timeout=timeout)


def clean(repo):
    r = git(repo, "status", "--short")
    return r["code"] == 0 and not r["out"]


def head(repo):
    r = git(repo, "rev-parse", "--short", "HEAD")
    return r["out"] if r["code"] == 0 else None


def current_branch(repo):
    r = git(repo, "branch", "--show-current")
    return r["out"] if r["code"] == 0 else None


def semver(tag):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)$", tag)
    return tuple(map(int, m.groups())) if m else None


def latest_tag(url):
    r = run(["git", "ls-remote", "--tags", "--refs", url], timeout=120)
    if r["code"] != 0:
        return None, r["err"] or r["out"]
    tags = []
    for line in r["out"].splitlines():
        name = line.rsplit("/", 1)[-1]
        key = semver(name)
        if key:
            tags.append((key, name))
    if not tags:
        return None, "no semver tags"
    return max(tags)[1], None


def read_plugin_version(path):
    try:
        return json.loads(Path(path).read_text())["version"]
    except Exception:
        return None


def add_result(results, name, status, detail="", **extra):
    item = {"name": name, "status": status}
    if detail:
        item["detail"] = detail
    item.update(extra)
    results.append(item)


def needs_permission(*runs):
    text = "\n".join((r.get("err") or "") + "\n" + (r.get("out") or "") for r in runs)
    return "Operation not permitted" in text or "permission denied" in text.lower()


def update_fable(results, apply_safe):
    repo = ROOT / "FableCodex"
    manifest = repo / "plugins/codex-fable5/.codex-plugin/plugin.json"
    if not repo.exists():
        add_result(results, "codex-fable5", "missing", str(repo))
        return
    before = read_plugin_version(manifest)
    latest, err = latest_tag("https://github.com/baskduf/FableCodex.git")
    if err:
        add_result(results, "codex-fable5", "check-failed", err, current=before)
        return
    if not apply_safe:
        add_result(results, "codex-fable5", "checked", current=before, latest=latest, head=head(repo))
        return
    if not clean(repo):
        add_result(results, "codex-fable5", "blocked-dirty", "local repo has changes", current=before, latest=latest)
        return
    steps = [
        git(repo, "fetch", "--tags", "origin", timeout=180),
        git(repo, "merge", "--ff-only", "origin/main"),
    ]
    if any(s["code"] != 0 for s in steps):
        add_result(results, "codex-fable5", "blocked", steps[-1]["err"] or steps[-1]["out"], current=before, latest=latest)
        return
    test = run(["python", "-m", "pytest", "-q"], cwd=repo, timeout=180)
    if test["code"] != 0:
        add_result(results, "codex-fable5", "blocked-tests", test["err"] or test["out"], current=before, latest=latest)
        return
    install = run(["codex", "plugin", "add", "codex-fable5@fablecodex", "--json"], timeout=120)
    after = read_plugin_version(manifest)
    if install["code"] == 0:
        status = "applied"
    elif needs_permission(install):
        status = "needs-permission"
    else:
        status = "install-failed"
    add_result(results, "codex-fable5", status, install["err"], current=after, latest=latest, head=head(repo))


def update_ponytail(results, apply_safe):
    latest, err = latest_tag("https://github.com/DietrichGebert/ponytail.git")
    if err:
        add_result(results, "ponytail", "check-failed", err)
        return
    if not apply_safe:
        add_result(results, "ponytail", "checked", latest=latest)
        return
    upgrade = run(["codex", "plugin", "marketplace", "upgrade", "ponytail", "--json"], timeout=180)
    install = run(["codex", "plugin", "add", "ponytail@ponytail", "--json"], timeout=120)
    if upgrade["code"] == 0 and install["code"] == 0:
        status = "applied"
    elif needs_permission(upgrade, install):
        status = "needs-permission"
    else:
        status = "blocked"
    add_result(results, "ponytail", status, upgrade["err"] or install["err"], latest=latest)


def check_skillopt(results):
    repo = ROOT / "SkillOpt"
    latest, err = latest_tag("https://github.com/microsoft/SkillOpt.git")
    if not repo.exists():
        add_result(results, "skillopt-sleep", "missing", str(repo), latest=latest)
        return
    add_result(
        results,
        "skillopt-sleep",
        "manual-review",
        "custom Codex mining branch must be merged by hand",
        branch=current_branch(repo),
        head=head(repo),
        clean=clean(repo),
        latest=latest,
        check_error=err,
    )


def ensure_tag_clone(results, name, url, tag, path_prefix, apply_safe):
    if not tag:
        add_result(results, name, "check-failed", "no latest tag")
        return
    dest = ROOT / f"{path_prefix}-{tag}-clean"
    if dest.exists():
        add_result(results, name, "clone-present", str(dest), latest=tag)
        return
    if not apply_safe:
        add_result(results, name, "clone-missing", str(dest), latest=tag)
        return
    r = run(["git", "clone", "--branch", tag, "--depth", "1", url, str(dest)], timeout=300)
    add_result(results, name, "clone-created" if r["code"] == 0 else "clone-failed", r["err"], path=str(dest), latest=tag)


def check_codebase_memory(results, apply_safe):
    latest, err = latest_tag("https://github.com/DeusData/codebase-memory-mcp.git")
    if err:
        add_result(results, "codebase-memory-mcp", "check-failed", err)
        return
    ensure_tag_clone(
        results,
        "codebase-memory-mcp",
        "https://github.com/DeusData/codebase-memory-mcp.git",
        latest,
        "codebase-memory-mcp",
        apply_safe,
    )


def check_superpowers(results, apply_safe):
    latest, err = latest_tag("https://github.com/obra/superpowers.git")
    if err:
        add_result(results, "superpowers-upstream", "check-failed", err)
        return
    dest = ROOT / f"superpowers-{latest}-upstream"
    if dest.exists():
        add_result(results, "superpowers-upstream", "clone-present", str(dest), latest=latest)
        return
    if not apply_safe:
        add_result(results, "superpowers-upstream", "clone-missing", str(dest), latest=latest)
        return
    r = run(["git", "clone", "--branch", latest, "--depth", "1", "https://github.com/obra/superpowers.git", str(dest)], timeout=300)
    add_result(results, "superpowers-upstream", "clone-created" if r["code"] == 0 else "clone-failed", r["err"], path=str(dest), latest=latest)


def check_agency(results):
    baseline = "fc5a192e7e0f2fad0d74686d9165435e410869a8"
    paths = [
        "engineering/engineering-codebase-onboarding-engineer.md",
        "engineering/engineering-technical-writer.md",
        "testing/testing-reality-checker.md",
        "testing/testing-tool-evaluator.md",
        "engineering/engineering-email-intelligence-engineer.md",
        "security/security-senior-secops.md",
    ]
    with tempfile.TemporaryDirectory(prefix="agency-agents-") as tmp:
        clone = run(["git", "clone", "--depth", "1", "https://github.com/msitarzewski/agency-agents.git", tmp], timeout=180)
        if clone["code"] != 0:
            add_result(results, "agency-router", "check-failed", clone["err"])
            return
        fetch = git(tmp, "fetch", "--depth", "1", "origin", baseline, timeout=120)
        if fetch["code"] != 0:
            add_result(results, "agency-router", "baseline-fetch-failed", fetch["err"])
            return
        diff = git(tmp, "diff", "--name-only", f"{baseline}..HEAD", "--", *paths)
        if diff["out"]:
            add_result(results, "agency-router", "manual-review", "selected source roles changed", changed=diff["out"].splitlines())
        else:
            add_result(results, "agency-router", "current", "selected source roles unchanged")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-safe", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results = []
    update_fable(results, args.apply_safe)
    update_ponytail(results, args.apply_safe)
    check_skillopt(results)
    check_codebase_memory(results, args.apply_safe)
    check_superpowers(results, args.apply_safe)
    check_agency(results)

    if args.json:
        print(json.dumps({"apply_safe": args.apply_safe, "results": results}, ensure_ascii=False, indent=2))
        return
    for item in results:
        detail = f" - {item['detail']}" if item.get("detail") else ""
        print(f"{item['name']}: {item['status']}{detail}")


if __name__ == "__main__":
    main()
