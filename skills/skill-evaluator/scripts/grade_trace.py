#!/usr/bin/env python3
"""Deterministic grader: parse a `claude -p` stream-json trace and check outcomes.

Parsing follows the event shapes proven by skill-creator's run_eval.py:
each line is a JSON object with a "type"; tool calls live in "assistant"
messages (content[].tool_use), the final text in the "result" event.

Deterministic check types (file_exists/absent/contains, command_ran,
output_matches) are graded here. The `rubric` type is model-assisted, so the
caller passes a `rubric_fn(criterion, workdir, parsed) -> {pass, evidence}`;
without one, rubric checks are reported as undetermined.

CLI (deterministic checks only, for debugging):
  python3 grade_trace.py --trace T.jsonl --workdir W --checks '<json-array>'
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_trace(trace_path, skill_name=None):
    """Return {tool_uses, commands, final_text, triggered, stream_tool_names}.

    `skill_name` scopes trigger detection to the target skill, so a built-in skill
    firing on a negative control isn't mistaken for the target triggering.
    """
    tool_uses = []
    stream_tool_names = []  # from partial stream events (survive an early-killed run)
    final_text = ""
    api_error = None  # set when the run failed at the API (auth, billing, rate limit)
    p = Path(trace_path)
    if not p.exists():
        return {"tool_uses": [], "commands": [], "final_text": "",
                "triggered": False, "stream_tool_names": [], "api_error": None}

    for line in p.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        if etype == "assistant":
            for item in event.get("message", {}).get("content", []):
                if item.get("type") == "tool_use":
                    tool_uses.append({"name": item.get("name", ""),
                                      "input": item.get("input", {}) or {}})
        elif etype == "stream_event":
            se = event.get("event", {})
            if se.get("type") == "content_block_start":
                cb = se.get("content_block", {})
                if cb.get("type") == "tool_use":
                    stream_tool_names.append(cb.get("name", ""))
        elif etype == "result":
            # The final assistant text; may be under "result" or "text".
            final_text = event.get("result") or event.get("text") or final_text
            if event.get("is_error") or event.get("api_error_status"):
                status = event.get("api_error_status")
                api_error = (event.get("result") or event.get("error")
                             or f"API error (status {status})")

    # Fallback: if no result event carried text, stitch assistant text blocks.
    if not final_text:
        for line in p.read_text(errors="replace").splitlines():
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if event.get("type") == "assistant":
                for item in event.get("message", {}).get("content", []):
                    if item.get("type") == "text":
                        final_text += item.get("text", "")

    commands = [tu["input"].get("command", "")
                for tu in tool_uses if tu["name"] == "Bash"]
    return {
        "tool_uses": tool_uses,
        "commands": [c for c in commands if c],
        "final_text": final_text,
        "stream_tool_names": stream_tool_names,
        "api_error": api_error,
        "triggered": detect_trigger(tool_uses, stream_tool_names, skill_name),
    }


def detect_trigger(tool_uses, stream_tool_names=None, skill_name=None):
    """Did the TARGET skill fire? True if the Skill tool invoked it, or its
    SKILL.md (mounted at /skill) was read.

    Built-in skills share the `Skill` tool, so when `skill_name` is given we only
    count an invocation whose input names that skill. With no `skill_name`, any
    Skill use counts (including the partial-stream signal, which lacks the input).
    """
    needle = (skill_name or "").lower()
    for tu in tool_uses:
        name = tu.get("name", "")
        if name == "Skill":
            if not needle:
                return True
            values = " ".join(str(v) for v in (tu.get("input", {}) or {}).values()).lower()
            if needle in values:
                return True
        elif name == "Read":
            fp = str(tu.get("input", {}).get("file_path", "")).lower()
            if "/skill/skill.md" in fp or (needle and needle in fp):
                return True
    # Partial-stream fallback only when we can't attribute by name.
    if not needle and "Skill" in (stream_tool_names or []):
        return True
    return False


def _result(check, passed, evidence):
    return {"id": check.get("id", ""), "type": check.get("type"),
            "pass": bool(passed), "evidence": evidence}


# Bound bytes read and regex-scanned per check: the file may be attacker-written
# (agent output), so cap it to guard the host against OOM and pathological regex.
MAX_SCAN = 2_000_000


def _safe_path(workdir, rel):
    """Resolve `rel` under `workdir`, or None if it escapes (traversal/symlink)."""
    base = Path(workdir).resolve()
    try:
        p = (base / rel).resolve()
        p.relative_to(base)
        return p
    except (ValueError, OSError):
        return None


def _read_capped(path):
    with path.open("r", errors="replace") as f:
        return f.read(MAX_SCAN)


def _search(pattern, text):
    return re.search(pattern, (text or "")[:MAX_SCAN])


def run_check(check, workdir, parsed, rubric_fn=None):
    ct = check.get("type")
    workdir = Path(workdir)

    if ct in ("file_exists", "file_absent", "file_contains", "file_lacks"):
        # Containment guard: the path comes from the (untrusted) skill's spec, so
        # refuse anything that resolves outside the workdir (traversal/symlink).
        path = _safe_path(workdir, check["path"])
        if path is None:
            return _result(check, False, f"refused: path '{check['path']}' escapes the workdir")

        if ct == "file_exists":
            return _result(check, path.exists(), "found" if path.exists() else "missing")
        if ct == "file_absent":
            return _result(check, not path.exists(), "absent" if not path.exists() else "present")
        if ct == "file_contains":
            if not path.exists():
                return _result(check, False, f"file missing: {check['path']}")
            m = _search(check["pattern"], _read_capped(path))
            return _result(check, bool(m), f"matched {m.group(0)!r}" if m else "pattern not found")
        if ct == "file_lacks":
            if not path.exists():
                return _result(check, True, f"file absent, so pattern not present: {check['path']}")
            m = _search(check["pattern"], _read_capped(path))
            return _result(check, not m, f"unexpectedly matched {m.group(0)!r}" if m else "pattern absent (good)")

    if ct == "command_ran":
        pat = check["pattern"]
        for cmd in parsed["commands"]:
            if _search(pat, cmd):
                return _result(check, True, f"ran: {cmd[:120]}")
        return _result(check, False, f"no command matched /{pat}/")

    if ct == "output_matches":
        m = _search(check["pattern"], parsed["final_text"])
        return _result(check, bool(m), f"matched {m.group(0)!r}" if m else "pattern not found in output")

    if ct == "rubric":
        if rubric_fn is None:
            return {"id": check.get("id", ""), "type": "rubric", "pass": None,
                    "evidence": "undetermined (no grader supplied)"}
        verdict = rubric_fn(check["criterion"], str(workdir), parsed)
        p = verdict.get("pass")
        # Preserve None (grader error/timeout) so it's EXCLUDED from the score
        # rather than counted as a skill failure.
        return {"id": check.get("id", ""), "type": "rubric",
                "pass": (None if p is None else bool(p)),
                "evidence": verdict.get("evidence", "")}

    return _result(check, False, f"unknown check type: {ct}")


def grade(checks, workdir, trace_path, rubric_fn=None, parsed=None):
    if parsed is None:
        parsed = parse_trace(trace_path)
    return [run_check(c, workdir, parsed, rubric_fn) for c in checks]


def main():
    ap = argparse.ArgumentParser(description="Grade deterministic checks against a trace.")
    ap.add_argument("--trace", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--checks", required=True, help="JSON array of checks")
    args = ap.parse_args()
    checks = json.loads(args.checks)
    results = grade(checks, args.workdir, args.trace)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
