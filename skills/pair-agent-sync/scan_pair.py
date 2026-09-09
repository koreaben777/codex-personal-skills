#!/usr/bin/env python3
"""Read-only digest of the *pair* coding agent's sessions for one project.

Claude Code sessions: ~/.claude/projects/<escaped-cwd>/<session>.jsonl
Codex sessions:       ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl (+ archived_sessions)

Usage:
  scan_pair.py --pair codex  --project "/path/to/repo" --days 7
  scan_pair.py --pair claude --project "/path/to/repo" --since 2026-09-05T00:00:00Z
  scan_pair.py --pair codex  --project "/path/to/repo" --full 01a0716a   # one thread, verbatim
  scan_pair.py --selftest
"""
import argparse, glob, json, os, re, sys
from datetime import datetime, timedelta, timezone

HOME = os.path.expanduser("~")
MUTATE = re.compile(
    r"(apply_patch|git\s+(commit|apply|add|checkout|merge|reset|revert|push|tag|stash)"
    r"|sed -i|tee\s|>>|\s>\s|mkdir|touch\s|mv\s|cp\s|rm\s|chmod|pip install|npm\s+(i|install)"
    r"|make\s|pytest|python[0-9.]*\s+-m)")


def parse_ts(s):
    if not isinstance(s, str):
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def squash(s, n):
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s[:n] + ("…" if len(s) > n else "")


def blocks_text(content):
    if isinstance(content, str):
        return content
    out = []
    for b in content or []:
        if isinstance(b, dict) and isinstance(b.get("text"), str):
            out.append(b["text"])
    return "\n".join(out)


def noise(text):
    """Injected wrappers, not something a human typed."""
    t = (text or "").lstrip()
    return not t or t.startswith("<") or t.startswith("Caveat:")


def iter_lines(path):
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def new_session(path, sid):
    return {"file": path, "id": sid, "title": None, "cwd": None, "origin": None,
            "turns": [], "cmds": [], "ncalls": 0, "start": None, "end": None,
            "before": 0}


def keep(s, since, ts):
    """In-window items only: a thread open for months must not report July turns."""
    if ts and ts < since:
        s["before"] += 1
        return False
    if ts:
        s["start"] = s["start"] or ts
        s["end"] = ts
    return True


def read_codex(path, since):
    s = new_session(path, os.path.basename(path))
    for d in iter_lines(path):
        ts = parse_ts(d.get("timestamp"))
        p = d.get("payload") if isinstance(d.get("payload"), dict) else {}
        if d.get("type") == "session_meta":
            s["id"] = p.get("id") or s["id"]
            s["cwd"] = p.get("cwd")
            s["origin"] = "%s/%s" % (p.get("originator"), p.get("thread_source"))
        elif d.get("type") == "turn_context":
            s["cwd"] = s["cwd"] or p.get("cwd")
        elif d.get("type") == "response_item":
            pt = p.get("type")
            if pt == "message":
                text = blocks_text(p.get("content"))
                role = p.get("role")
                if role not in ("user", "assistant") or not text.strip():
                    continue
                if role == "user" and noise(text):
                    continue
                if keep(s, since, ts):
                    s["turns"].append((ts, role, text))
            elif pt in ("custom_tool_call", "function_call", "local_shell_call"):
                if not keep(s, since, ts):
                    continue
                s["ncalls"] += 1
                raw = p.get("input") or p.get("arguments") or json.dumps(p.get("action") or {})
                cmd = "%s %s" % (p.get("name") or pt, raw)
                if MUTATE.search(cmd):
                    s["cmds"].append(cmd)
    return s


def read_claude(path, since):
    s = new_session(path, os.path.basename(path)[:-6])
    for d in iter_lines(path):
        if d.get("type") == "custom-title":
            s["title"] = d.get("customTitle")
        s["cwd"] = s["cwd"] or d.get("cwd")
        s["origin"] = s["origin"] or d.get("gitBranch")
        if d.get("isSidechain"):
            continue
        ts = parse_ts(d.get("timestamp"))
        msg = d.get("message") if isinstance(d.get("message"), dict) else {}
        if d.get("type") == "user":
            text = blocks_text(msg.get("content"))
            if not noise(text) and keep(s, since, ts):
                s["turns"].append((ts, "user", text))
        elif d.get("type") == "assistant":
            if not keep(s, since, ts):
                continue
            for b in msg.get("content") or []:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    s["turns"].append((ts, "assistant", b["text"]))
                elif b.get("type") == "tool_use":
                    s["ncalls"] += 1
                    inp = b.get("input") or {}
                    tgt = inp.get("file_path") or inp.get("command") or ""
                    cmd = "%s %s" % (b.get("name"), tgt)
                    if b.get("name") in ("Edit", "Write", "NotebookEdit") or MUTATE.search(cmd):
                        s["cmds"].append(cmd)
    return s


def in_scope(cwd, project):
    """Sessions opened in the project or in any subdirectory of it."""
    if not cwd:
        return False
    real, root = os.path.realpath(cwd), os.path.realpath(project)
    return real == root or real.startswith(root + os.sep)


def candidates(pair, since):
    if pair == "codex":
        pats = [os.path.join(HOME, ".codex/sessions/**/rollout-*.jsonl"),
                os.path.join(HOME, ".codex/archived_sessions/**/*.jsonl")]
    else:
        pats = [os.path.join(HOME, ".claude/projects/*/*.jsonl")]
    files = []
    for pat in pats:
        for f in glob.glob(pat, recursive=True):
            try:
                if datetime.fromtimestamp(os.path.getmtime(f), timezone.utc) >= since:
                    files.append(f)
            except OSError:
                continue
    return files


def collect(pair, project, since):
    project = os.path.realpath(project)
    reader = read_codex if pair == "codex" else read_claude
    out = []
    for f in candidates(pair, since):
        s = reader(f, since)
        if not in_scope(s["cwd"], project):
            continue
        if not s["turns"] and not s["cmds"]:
            continue
        out.append(s)
    out.sort(key=lambda s: s["end"] or datetime.min.replace(tzinfo=timezone.utc))
    return out


def codex_titles():
    idx = os.path.join(HOME, ".codex/session_index.jsonl")
    titles = {}
    if os.path.exists(idx):
        for d in iter_lines(idx):
            if d.get("id"):
                titles[d["id"]] = d.get("thread_name")
    return titles


def fmt_time(ts):
    return ts.astimezone().strftime("%Y-%m-%d %H:%M") if ts else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", choices=["codex", "claude"], help="agent whose sessions to read")
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--since", help="ISO8601, e.g. 2026-09-05T00:00:00Z")
    ap.add_argument("--days", type=float, default=7.0)
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--chars", type=int, default=600)
    ap.add_argument("--full", help="session id (or prefix): print its turns verbatim")
    ap.add_argument("--max-total", type=int, default=60000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.pair:
        ap.error("--pair is required")

    since = parse_ts(a.since) if a.since else datetime.now(timezone.utc) - timedelta(days=a.days)
    if a.since and not since:
        ap.error("--since is not ISO8601")
    sessions = collect(a.pair, a.project, since)
    titles = codex_titles() if a.pair == "codex" else {}
    for s in sessions:
        s["title"] = s["title"] or titles.get(s["id"])

    now = datetime.now(timezone.utc)
    print("# pair digest — %s | project: %s" % (a.pair, os.path.realpath(a.project)))
    print("since %s → until %s (UTC)" % (since.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                         now.strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("sessions: %d\n" % len(sessions))

    if a.full:
        hit = [s for s in sessions if a.full in s["id"] or a.full in s["file"]]
        if not hit:
            print("no session matches %s in this window" % a.full)
            return 1
        total = 0
        for s in hit:
            print("## %s | %s | %s" % (s["id"], s["title"] or "(no title)", s["file"]))
            for ts, role, text in s["turns"]:
                body = squash(text, 4000)
                total += len(body)
                if total > a.max_total:
                    print("\n[truncated at --max-total; narrow --since or raise --max-total]")
                    return 0
                print("\n[%s %s] %s" % (fmt_time(ts), role, body))
        return 0

    for s in sessions[-a.limit:]:
        print("## %s → %s | %s" % (fmt_time(s["start"]), fmt_time(s["end"]),
                                   s["title"] or "(no title)"))
        print("id: %s" % s["id"])
        if os.path.realpath(s["cwd"]) != os.path.realpath(a.project):
            print("cwd: %s   <- subdirectory, not the project root" % s["cwd"])
        print("file: %s" % s["file"])
        if s["origin"]:
            print("origin: %s" % s["origin"])
        asks = [t for t in s["turns"] if t[1] == "user"]
        says = [t for t in s["turns"] if t[1] == "assistant"]
        for t in asks[:3]:
            print("- ask: %s" % squash(t[2], a.chars))
        if len(asks) > 3:
            print("- (+%d more asks in window)" % (len(asks) - 3))
        if says:
            print("- said(last): %s" % squash(says[-1][2], a.chars))
        print("- tool calls: %d, write-ish: %d, items before window: %d"
              % (s["ncalls"], len(s["cmds"]), s["before"]))
        for c in s["cmds"][:12]:
            print("  * %s" % squash(c, 160))
        print()
    if len(sessions) > a.limit:
        print("[%d older sessions in window not shown; raise --limit]" % (len(sessions) - a.limit))
    return 0


def selftest():
    codex = [
        {"timestamp": "2026-09-05T11:53:09.076Z", "type": "session_meta",
         "payload": {"id": "abc", "cwd": "/tmp", "originator": "Codex Desktop",
                     "thread_source": "user"}},
        {"timestamp": "2026-09-05T11:54:00Z", "type": "response_item",
         "payload": {"type": "message", "role": "user",
                     "content": [{"type": "input_text", "text": "<app-context>skip me</app-context>"}]}},
        {"timestamp": "2026-09-05T11:54:01Z", "type": "response_item",
         "payload": {"type": "message", "role": "user",
                     "content": [{"type": "input_text", "text": "fix the upscaler"}]}},
        {"timestamp": "2026-09-05T11:55:00Z", "type": "response_item",
         "payload": {"type": "custom_tool_call", "name": "exec",
                     "input": "tools.exec_command({cmd: \"git commit -m x\"})"}},
        {"timestamp": "2026-09-05T11:56:00Z", "type": "response_item",
         "payload": {"type": "custom_tool_call", "name": "exec",
                     "input": "tools.exec_command({cmd: \"cat README.md\"})"}},
        {"timestamp": "2026-09-05T11:57:00Z", "type": "response_item",
         "payload": {"type": "message", "role": "assistant",
                     "content": [{"type": "output_text", "text": "done"}]}},
    ]
    claude = [
        {"type": "custom-title", "customTitle": "T", "sessionId": "s"},
        {"type": "user", "cwd": "/tmp", "timestamp": "2026-09-06T01:00:00Z",
         "message": {"role": "user", "content": "please review"}},
        {"type": "user", "cwd": "/tmp", "isSidechain": True, "timestamp": "2026-09-06T01:00:30Z",
         "message": {"role": "user", "content": "subagent noise"}},
        {"type": "assistant", "cwd": "/tmp", "timestamp": "2026-09-06T01:01:00Z",
         "message": {"role": "assistant", "content": [
             {"type": "text", "text": "ok"},
             {"type": "tool_use", "name": "Edit", "input": {"file_path": "/tmp/a.py"}},
             {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}},
    ]
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        cp, lp = os.path.join(d, "c.jsonl"), os.path.join(d, "l.jsonl")
        for path, rows in ((cp, codex), (lp, claude)):
            with open(path, "w") as fh:
                fh.write("\n".join(json.dumps(r) for r in rows))
        old = datetime(2026, 1, 1, tzinfo=timezone.utc)
        c = read_codex(cp, old)
        assert c["cwd"] == "/tmp" and c["id"] == "abc", c
        assert [t[2] for t in c["turns"] if t[1] == "user"] == ["fix the upscaler"], c["turns"]
        assert c["ncalls"] == 2 and len(c["cmds"]) == 1, c["cmds"]
        assert c["turns"][-1][1:] == ("assistant", "done"), c["turns"]
        cut = read_codex(cp, datetime(2026, 9, 5, 11, 56, tzinfo=timezone.utc))
        assert [t[1] for t in cut["turns"]] == ["assistant"], cut["turns"]
        assert cut["before"] == 2 and cut["ncalls"] == 1 and not cut["cmds"], cut
        l = read_claude(lp, old)
        assert l["title"] == "T" and l["cwd"] == "/tmp"
        assert [t[2] for t in l["turns"] if t[1] == "user"] == ["please review"], l["turns"]
        assert l["ncalls"] == 2 and len(l["cmds"]) == 1 and "/tmp/a.py" in l["cmds"][0], l["cmds"]
    assert in_scope("/tmp/repo", "/tmp/repo")
    assert in_scope("/tmp/repo/pkg/api", "/tmp/repo")
    assert not in_scope("/tmp/repo-2", "/tmp/repo")
    assert not in_scope("/tmp", "/tmp/repo")
    print("selftest ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
