#!/usr/bin/env python3
"""Deterministic linter for Agent Skills.

Checks a SKILL.md (and its directory) against the mechanically-verifiable rules
in Anthropic's Agent Skills spec and best-practices checklist: frontmatter
limits, body length, reference nesting, path style, and a few high-signal
heuristics. It does NOT judge writing quality or effectiveness -- that is
skill-evaluator's job.

Usage:  lint_skill.py <path-to-skill-dir-or-SKILL.md> [--json]
Exit:   0 = no errors (warnings allowed), 1 = errors found, 2 = unreadable.

Stdlib only -- no network.
"""
from __future__ import annotations

import os
import re
import sys

GENERIC_RE = re.compile(r"^(utils?|helpers?|tools?|doc[0-9]*|file[0-9]+|untitled|temp|misc)\.md$", re.I)


def main():
    json_out = False
    target = ""
    for arg in sys.argv[1:]:
        if arg == "--json":
            json_out = True
        else:
            target = arg

    if not target:
        print("usage: lint_skill.py <path-to-skill-dir-or-SKILL.md> [--json]", file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(target):
        print(f"Path not found: {target}", file=sys.stderr)
        sys.exit(2)

    if os.path.isdir(target):
        skill_dir = target
        skill_md = os.path.join(target, "SKILL.md")
    else:
        skill_md = target
        skill_dir = os.path.dirname(target) or "."
    skill_name = os.path.basename(os.path.normpath(skill_dir))

    checks = []  # (id, severity, passed, message)

    def ok(cid, msg=""):
        checks.append((cid, "error", True, msg))

    def err(cid, msg):
        checks.append((cid, "error", False, msg))

    def warn(cid, msg):
        checks.append((cid, "warning", False, msg))

    def emit_and_exit():
        errors = sum(1 for _, s, p, _ in checks if not p and s == "error")
        warns = sum(1 for _, s, p, _ in checks if not p and s == "warning")
        passed = sum(1 for _, _, p, _ in checks if p)
        total = len(checks)
        verdict = "clean"
        if errors + warns > 0:
            verdict = "pass-with-warnings"
        if errors > 0:
            verdict = "fail"

        if json_out:
            def esc(s):
                return s.replace("\\", "\\\\").replace('"', '\\"')
            out = ['{', f'  "skill": "{esc(skill_name)}",', '  "checks": [']
            for i, (cid, sev, p, msg) in enumerate(checks):
                sep = "" if i == total - 1 else ","
                pj = "true" if p else "false"
                out.append(f'    {{"id": "{esc(cid)}", "severity": "{sev}", "passed": {pj}, "message": "{esc(msg)}"}}{sep}')
            out.append('  ],')
            out.append(f'  "summary": {{"errors": {errors}, "warnings": {warns}, "passed": {passed}, "total": {total}}},')
            out.append(f'  "verdict": "{verdict}"')
            out.append('}')
            print("\n".join(out))
        else:
            print(f"Linting skill: {skill_name}")
            print("===============================")
            for cid, sev, p, msg in checks:
                tag = "ok  " if p else ("FAIL" if sev == "error" else "warn")
                if msg:
                    print(f"  [{tag}] {cid}: {msg}")
                else:
                    print(f"  [{tag}] {cid}")
            print("")
            print(f"Verdict: {verdict.upper()}  ({errors} errors, {warns} warnings, {passed}/{total} checks passed)")
        sys.exit(1 if errors > 0 else 0)

    def unquote(s):
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
            return s[1:-1]
        return s

    def resolve(base, p):
        d = os.path.dirname(p) if p.startswith("/") else os.path.join(base, os.path.dirname(p))
        b = os.path.basename(p)
        if not os.path.isdir(d):
            return ""
        return os.path.realpath(d) + "/" + b

    def extract_md_links(path):
        links = []
        try:
            content = open(path, errors="replace").read()
        except OSError:
            return links
        for m in re.finditer(r"\]\(([^)]+)\)", content):
            t = m.group(1).split("#", 1)[0]
            if not t:
                continue
            if "://" in t or t.startswith("mailto:"):
                continue
            if t.endswith(".md"):
                links.append(t)
        return links

    # ---- read file ----
    if not os.path.isfile(skill_md):
        err("skill-md-exists", f"No SKILL.md found at {skill_md}")
        emit_and_exit()

    text = open(skill_md, errors="replace").read()
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
    body = "".join(l + "\n" for l in body_lines).rstrip("\n")

    # ---- name ----
    name = ""
    for l in fm_lines:
        if l.startswith("name:"):
            name = re.sub(r"^name:[ \t]*", "", l)
            break
    name = unquote(name.strip())
    if not name:
        err("name-present", "Frontmatter is missing a non-empty name.")
    else:
        ok("name-present")
        if len(name) > 64:
            err("name-length", f"name is {len(name)} chars; max is 64.")
        else:
            ok("name-length")
        if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            ok("name-charset")
        else:
            err("name-charset", f"name must be lowercase a-z, 0-9 and single hyphens, no leading/trailing or consecutive hyphens: '{name}'.")
        if re.search(r"anthropic|claude", name, re.I):
            err("name-reserved", "name contains a reserved word (anthropic, claude).")
        else:
            ok("name-reserved")
        if re.search(r"<[^>]+>", name):
            err("name-no-xml", "name contains XML tags.")
        else:
            ok("name-no-xml")
        if name == skill_name:
            ok("name-dir-match")
        else:
            err("name-dir-match", f"name '{name}' must match the skill directory name '{skill_name}'.")

    # ---- description (with folded continuation lines) ----
    desc = ""
    ind = False
    for l in fm_lines:
        if not ind and l.startswith("description:"):
            desc = re.sub(r"^description:[ \t]*", "", l)
            ind = True
            continue
        if ind:
            if re.match(r"^[A-Za-z0-9_-]+:[ \t]", l):
                break
            desc = desc + " " + re.sub(r"^\s+", "", l)
    desc = unquote(desc.strip())
    if not desc:
        err("desc-present", "Frontmatter is missing a non-empty description.")
    else:
        ok("desc-present")
        if len(desc) > 1024:
            err("desc-length", f"description is {len(desc)} chars; max is 1024.")
        else:
            ok("desc-length")
        if re.search(r"<[^>]+>", desc):
            err("desc-no-xml", "description contains XML tags.")
        else:
            ok("desc-no-xml")
        if re.search(r"(^|[^a-z])(i can|i'll|i'm|i will|i help|i'd|i am|let me|you can use|you should use|use me to)([^a-z]|$)", desc, re.I):
            warn("desc-third-person", "description may be written in first/second person (e.g. 'I can help you'). It is injected into the system prompt and should read in third person.")
        else:
            ok("desc-third-person")
        if re.search(r"use when|use this|when the user|when working|use it when|use whenever", desc, re.I):
            ok("desc-when-cue")
        else:
            warn("desc-when-cue", "description may not say WHEN to use the skill (no 'use when / when the user' cue). It should carry both what it does and when to trigger.")

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
    if body_matches(r"[A-Za-z0-9_.-]+\\[A-Za-z0-9_.\\-]+"):
        warn("forward-slashes", "Body appears to contain Windows-style backslash paths. Use forward slashes everywhere.")
    else:
        ok("forward-slashes")

    # ---- time-sensitive info ----
    if body_matches(r"(as of\s+[0-9]{4}|before\s+[a-z]+\s+20[0-9][0-9]|after\s+[a-z]+\s+20[0-9][0-9]|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+20[0-9][0-9])"):
        warn("time-sensitive", "Body contains time-sensitive phrasing (a month/year or before/after a date). Move it into an 'old patterns' section so it does not go stale.")
    else:
        ok("time-sensitive")

    # ---- references: existence, one-level-deep, TOC ----
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False)
    tmp.write(body + "\n")
    tmp.close()
    body_link_list = extract_md_links(tmp.name)

    skill_md_resolved = resolve(skill_dir, os.path.basename(skill_md))
    body_refs = ""
    for link in body_link_list:
        body_refs += "\n" + resolve(skill_dir, link)

    missing, nested = "", ""
    for link in body_link_list:
        rp = resolve(skill_dir, link)
        if not os.path.isfile(rp):
            missing += " " + link
            continue
        rtext = open(rp, errors="replace").read()
        rlines = rtext.count("\n")
        if rlines > 100:
            head = rtext.splitlines()[:15]
            if not any("contents" in h.lower() for h in head):
                warn("ref-toc", f"Reference '{link}' is {rlines} lines but has no table of contents near the top. Long reference files should list their contents.")
        for nlink in extract_md_links(rp):
            nrp = resolve(os.path.dirname(rp), nlink)
            if nrp == skill_md_resolved:
                continue
            if nrp not in body_refs:
                nested += f" {link}->{nlink}"
    os.unlink(tmp.name)

    if missing:
        warn("ref-exists", f"SKILL.md links to file(s) that do not exist:{missing}")
    else:
        ok("ref-exists")
    if nested:
        warn("ref-one-level-deep", f"Found nested references (a reference file linking to a file not linked from SKILL.md):{nested}. Keep references one level deep.")
    else:
        ok("ref-one-level-deep")

    # ---- generic file names ----
    generic = ""
    for dirpath, _, filenames in os.walk(skill_dir):
        for fn in filenames:
            if fn.endswith(".md") and GENERIC_RE.match(fn):
                generic += fn + " "
    if generic:
        warn("file-names", f"Generic/uninformative file names found: {generic}. Name files by content so Claude can navigate by name.")
    else:
        ok("file-names")

    emit_and_exit()


if __name__ == "__main__":
    main()
