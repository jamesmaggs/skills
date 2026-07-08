#!/usr/bin/env python3
"""Deterministic linter for Agent Skills.

Checks a SKILL.md (and its directory) against the mechanically-verifiable rules
in Anthropic's Agent Skills spec and best-practices checklist: frontmatter
limits, body length, reference nesting, path style, and a few high-signal
heuristics. It does NOT judge writing quality or effectiveness -- those take
human judgement, not this tool.

Usage:  lint_skill.py <path-to-skill-dir-or-SKILL.md> [--json]
Exit:   0 = no errors (warnings allowed), 1 = errors found, 2 = unreadable.

Stdlib only -- no network.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import namedtuple
from pathlib import Path
from typing import NoReturn

GENERIC_RE = re.compile(r"^(utils?|helpers?|tools?|doc[0-9]*|file[0-9]+|untitled|temp|misc)\.md$", re.I)

Check = namedtuple("Check", "id severity passed message")


def unquote(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def resolve(base, link):
    """Resolve link against base to a canonical <realpath-of-dir>/<basename>.

    Returns None when the link's directory does not exist (mirrors the old
    empty-string sentinel, which never matched a real file).
    """
    link = Path(link)
    d = link.parent if link.is_absolute() else Path(base) / link.parent
    if not d.is_dir():
        return None
    return d.resolve() / link.name


def md_links(content):
    links = []
    for m in re.finditer(r"\]\(([^)]+)\)", content):
        t = m.group(1).split("#", 1)[0]
        if not t or "://" in t or t.startswith("mailto:") or not t.endswith(".md"):
            continue
        links.append(t)
    return links


def extract_md_links(path):
    try:
        with open(path, errors="replace") as f:
            content = f.read()
    except OSError:
        return []
    return md_links(content)


def main():
    ap = argparse.ArgumentParser(description="Deterministic linter for Agent Skills.")
    ap.add_argument("target", help="path to a skill directory or a SKILL.md")
    ap.add_argument("--json", dest="json_out", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    json_out = args.json_out
    target = Path(args.target)

    if not target.exists():
        print(f"Path not found: {target}", file=sys.stderr)
        sys.exit(2)

    if target.is_dir():
        skill_dir = target
        skill_md = target / "SKILL.md"
    else:
        skill_md = target
        skill_dir = skill_md.parent
    skill_name = skill_dir.resolve().name

    checks = []  # Check(id, severity, passed, message)

    def ok(cid, msg=""):
        checks.append(Check(cid, "error", True, msg))

    def err(cid, msg):
        checks.append(Check(cid, "error", False, msg))

    def warn(cid, msg):
        checks.append(Check(cid, "warning", False, msg))

    def check(cid, passed, fail_msg="", *, warn_only=False):
        if passed:
            ok(cid)
        elif warn_only:
            warn(cid, fail_msg)
        else:
            err(cid, fail_msg)

    def emit_and_exit() -> NoReturn:
        errors = sum(1 for c in checks if not c.passed and c.severity == "error")
        warns = sum(1 for c in checks if not c.passed and c.severity == "warning")
        passed = sum(1 for c in checks if c.passed)
        total = len(checks)
        verdict = "clean"
        if errors + warns > 0:
            verdict = "pass-with-warnings"
        if errors > 0:
            verdict = "fail"

        if json_out:
            out = ["{", f'  "skill": {json.dumps(skill_name)},', '  "checks": [']
            for i, c in enumerate(checks):
                sep = "" if i == total - 1 else ","
                obj = json.dumps({"id": c.id, "severity": c.severity, "passed": c.passed, "message": c.message})
                out.append(f"    {obj}{sep}")
            out.append("  ],")
            out.append(f'  "summary": {json.dumps({"errors": errors, "warnings": warns, "passed": passed, "total": total})},')
            out.append(f'  "verdict": {json.dumps(verdict)}')
            out.append("}")
            print("\n".join(out))
        else:
            print(f"Linting skill: {skill_name}")
            print("===============================")
            for c in checks:
                tag = "ok  " if c.passed else ("FAIL" if c.severity == "error" else "warn")
                if c.message:
                    print(f"  [{tag}] {c.id}: {c.message}")
                else:
                    print(f"  [{tag}] {c.id}")
            print("")
            print(f"Verdict: {verdict.upper()}  ({errors} errors, {warns} warnings, {passed}/{total} checks passed)")
        sys.exit(1 if errors > 0 else 0)

    # ---- read file ----
    if not skill_md.is_file():
        err("skill-md-exists", f"No SKILL.md found at {skill_md}")
        emit_and_exit()

    with open(skill_md, errors="replace") as f:
        text = f.read()
    lines = text.splitlines()

    first_line = lines[0] if lines else ""
    if first_line != "---":
        err("frontmatter", "SKILL.md has no YAML frontmatter block (--- ... ---).")
        emit_and_exit()
    ok("frontmatter", "Frontmatter block present.")

    fc = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    if fc is None:
        err("frontmatter", "Frontmatter opening --- has no closing ---.")
        emit_and_exit()

    fm_lines = lines[1:fc]
    body_lines = lines[fc + 1:]
    # Mirror `$(awk 'NR>e')`: join with newlines, strip trailing newlines.
    body = "".join(ln + "\n" for ln in body_lines).rstrip("\n")

    # ---- name ----
    name = ""
    for ln in fm_lines:
        if ln.startswith("name:"):
            name = re.sub(r"^name:[ \t]*", "", ln)
            break
    name = unquote(name.strip())
    if not name:
        err("name-present", "Frontmatter is missing a non-empty name.")
    else:
        ok("name-present")
        check("name-length", len(name) <= 64, f"name is {len(name)} chars; max is 64.")
        check("name-charset", bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name)),
              f"name must be lowercase a-z, 0-9 and single hyphens, no leading/trailing or consecutive hyphens: '{name}'.")
        check("name-reserved", not re.search(r"anthropic|claude", name, re.I),
              "name contains a reserved word (anthropic, claude).")
        check("name-no-xml", not re.search(r"<[^>]+>", name), "name contains XML tags.")
        check("name-dir-match", name == skill_name,
              f"name '{name}' must match the skill directory name '{skill_name}'.")

    # ---- invocation mode ----
    # A user-invoked skill (disable-model-invocation: true) is never reached by
    # the model, so its description is human-facing and should have trigger cues
    # stripped — the opposite of what a model-invoked description needs.
    user_invoked = False
    for ln in fm_lines:
        m = re.match(r"disable-model-invocation:[ \t]*(\S+)", ln)
        if m:
            user_invoked = unquote(m.group(1).strip()).lower() == "true"
            break

    # ---- description (with folded continuation lines) ----
    desc = ""
    ind = False
    for ln in fm_lines:
        if not ind and ln.startswith("description:"):
            desc = re.sub(r"^description:[ \t]*", "", ln)
            ind = True
            continue
        if ind:
            if re.match(r"^[A-Za-z0-9_-]+:[ \t]", ln):
                break
            desc = desc + " " + re.sub(r"^\s+", "", ln)
    desc = unquote(desc.strip())
    if not desc:
        err("desc-present", "Frontmatter is missing a non-empty description.")
    else:
        ok("desc-present")
        check("desc-length", len(desc) <= 1024, f"description is {len(desc)} chars; max is 1024.")
        check("desc-no-xml", not re.search(r"<[^>]+>", desc), "description contains XML tags.")
        check("desc-third-person",
              not re.search(r"(^|[^a-z])(i can|i'll|i'm|i will|i help|i'd|i am|let me|you can use|you should use|use me to)([^a-z]|$)", desc, re.I),
              "description may be written in first/second person (e.g. 'I can help you'). It is injected into the system prompt and should read in third person.",
              warn_only=True)
        when_cue = bool(re.search(
            r"use when|use this|when the user|when working|use it when|use whenever", desc, re.I))
        if user_invoked:
            check("desc-when-cue", not when_cue,
                  "user-invoked skill: the description is human-facing, so strip trigger cues (found a 'use when / when the user' phrase).",
                  warn_only=True)
        else:
            check("desc-when-cue", when_cue,
                  "description may not say WHEN to use the skill (no 'use when / when the user' cue). It should carry both what it does and when to trigger.",
                  warn_only=True)

    # ---- body length ----
    body_line_count = body.count("\n") + 1 if body else 1
    if body_line_count > 500:
        warn("body-length", f"SKILL.md body is {body_line_count} lines; guidance is under 500. Split detail into reference files.")
    elif body_line_count >= 450:
        warn("body-length", f"SKILL.md body is {body_line_count} lines, approaching the 500-line guidance.")
    else:
        ok("body-length", f"Body is {body_line_count} lines.")

    body_greplines = body.split("\n")

    def body_matches(pattern):
        return any(re.search(pattern, ln, re.I) for ln in body_greplines)

    # ---- windows paths ----
    check("forward-slashes", not body_matches(r"[A-Za-z0-9_.-]+\\[A-Za-z0-9_.\\-]+"),
          "Body appears to contain Windows-style backslash paths. Use forward slashes everywhere.",
          warn_only=True)

    # ---- time-sensitive info ----
    check("time-sensitive",
          not body_matches(r"(as of\s+[0-9]{4}|before\s+[a-z]+\s+20[0-9][0-9]|after\s+[a-z]+\s+20[0-9][0-9]|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+20[0-9][0-9])"),
          "Body contains time-sensitive phrasing (a month/year or before/after a date). Move it into an 'old patterns' section so it does not go stale.",
          warn_only=True)

    # ---- references: existence, one-level-deep, TOC ----
    body_link_list = md_links(body + "\n")

    skill_md_resolved = resolve(skill_dir, skill_md.name)
    body_refs = {resolve(skill_dir, link) for link in body_link_list}

    missing, nested = "", ""
    for link in body_link_list:
        rp = resolve(skill_dir, link)
        if rp is None or not rp.is_file():
            missing += " " + link
            continue
        with open(rp, errors="replace") as f:
            rtext = f.read()
        rlines = rtext.count("\n")
        if rlines > 100:
            head = rtext.splitlines()[:15]
            if not any("contents" in h.lower() for h in head):
                warn("ref-toc", f"Reference '{link}' is {rlines} lines but has no table of contents near the top. Long reference files should list their contents.")
        for nlink in extract_md_links(rp):
            nrp = resolve(rp.parent, nlink)
            if nrp is None or nrp == skill_md_resolved:
                continue
            if nrp not in body_refs:
                nested += f" {link}->{nlink}"

    check("ref-exists", not missing,
          f"SKILL.md links to file(s) that do not exist:{missing}", warn_only=True)
    check("ref-one-level-deep", not nested,
          f"Found nested references (a reference file linking to a file not linked from SKILL.md):{nested}. Keep references one level deep.",
          warn_only=True)

    # ---- generic file names ----
    generic = ""
    for p in sorted(skill_dir.rglob("*.md"), key=lambda p: str(p)):
        if GENERIC_RE.match(p.name):
            generic += p.name + " "
    check("file-names", not generic,
          f"Generic/uninformative file names found: {generic}. Name files by content so Claude can navigate by name.",
          warn_only=True)

    emit_and_exit()


if __name__ == "__main__":
    main()
