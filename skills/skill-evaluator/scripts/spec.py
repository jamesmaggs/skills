"""Shared eval-spec definitions: schema, loading, validation. Stdlib only.

Single source of truth for the eval spec format documented in
references/eval-spec.md. Imported by validate_spec.py, run_evals.py and
grade_trace.py so the schema lives in exactly one place.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

TRIGGERING_CSV = "triggering.csv"
OUTCOME_JSON = "outcome.json"

# check type -> required field names (besides "type")
CHECK_TYPES = {
    "file_exists": ["path"],
    "file_absent": ["path"],
    "file_contains": ["path", "pattern"],
    "file_lacks": ["path", "pattern"],
    "command_ran": ["pattern"],
    "output_matches": ["pattern"],
    "rubric": ["criterion"],
}
DETERMINISTIC = {
    "file_exists", "file_absent", "file_contains", "file_lacks",
    "command_ran", "output_matches",
}


def evals_dir(skill_dir):
    return Path(skill_dir) / "evals"


def is_safe_relpath(rel):
    """True if `rel` is a relative path with no leading slash and no '..' escape.

    Fixture and check paths come from the (untrusted) evaluated skill's spec, so
    they must not point outside their sandbox via traversal or absolute paths.
    """
    if not isinstance(rel, str) or not rel:
        return False
    p = Path(rel)
    return not p.is_absolute() and ".." not in p.parts


def is_contained(base, rel):
    """True if `rel` is a safe relative path that resolves inside `base`
    (also catches a symlinked entry pointing outside)."""
    if not is_safe_relpath(rel):
        return False
    base_r = Path(base).resolve()
    try:
        (base_r / rel).resolve().relative_to(base_r)
        return True
    except (ValueError, OSError):
        return False


def parse_bool(s):
    return str(s).strip().lower() == "true"


def _is_bool_str(s):
    return isinstance(s, str) and s.strip().lower() in ("true", "false")


def _nonempty_str(v):
    return isinstance(v, str) and bool(v.strip())


def load_triggering(skill_dir):
    """Return a list of dicts {id, should_trigger(bool), prompt}."""
    path = evals_dir(skill_dir) / TRIGGERING_CSV
    rows = []
    with path.open(newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "id": (r.get("id") or "").strip(),
                "should_trigger": parse_bool(r.get("should_trigger") or "false"),
                "prompt": (r.get("prompt") or "").strip(),
            })
    return rows


def load_outcome(skill_dir):
    """Return the parsed outcome.json list."""
    path = evals_dir(skill_dir) / OUTCOME_JSON
    return json.loads(path.read_text())


def _validate_triggering(tcsv):
    """Validate triggering.csv; return (errors, warnings)."""
    errors, warnings = [], []
    if not tcsv.exists():
        errors.append(f"missing {TRIGGERING_CSV}")
        return errors, warnings
    try:
        with tcsv.open(newline="") as f:
            reader = csv.DictReader(f)
            cols = [c.strip() for c in (reader.fieldnames or [])]
            if cols[:3] != ["id", "should_trigger", "prompt"]:
                errors.append(
                    f"{TRIGGERING_CSV}: header must start with id,should_trigger,prompt (got {cols})")
            seen, npos, nneg, nrow = set(), 0, 0, 0
            for ln, row in enumerate(reader, start=2):
                nrow += 1
                rid = (row.get("id") or "").strip()
                st = (row.get("should_trigger") or "").strip()
                pr = (row.get("prompt") or "").strip()
                if not rid:
                    errors.append(f"{TRIGGERING_CSV} line {ln}: empty id")
                elif rid in seen:
                    errors.append(f"{TRIGGERING_CSV} line {ln}: duplicate id '{rid}'")
                else:
                    seen.add(rid)
                if not _is_bool_str(st):
                    errors.append(f"{TRIGGERING_CSV} line {ln}: should_trigger must be true|false (got '{st}')")
                elif parse_bool(st):
                    npos += 1
                else:
                    nneg += 1
                if not pr:
                    errors.append(f"{TRIGGERING_CSV} line {ln}: empty prompt")
            if nrow == 0:
                errors.append(f"{TRIGGERING_CSV}: no data rows")
            if npos == 0:
                warnings.append(f"{TRIGGERING_CSV}: no positive (should_trigger=true) rows")
            if nneg == 0:
                warnings.append(f"{TRIGGERING_CSV}: no negative controls (should_trigger=false) — can't detect over-triggering")
    except Exception as e:  # noqa: BLE001 - report any parse failure
        errors.append(f"{TRIGGERING_CSV}: parse error: {e}")
    return errors, warnings


def _validate_check(chk, clabel):
    """Validate one outcome check; return a list of error strings."""
    if not isinstance(chk, dict):
        return [f"{clabel}: not an object"]
    ct = chk.get("type")
    if ct not in CHECK_TYPES:
        return [f"{clabel}: unknown type '{ct}' (valid: {', '.join(sorted(CHECK_TYPES))})"]
    errors = []
    for field in CHECK_TYPES[ct]:
        if not _nonempty_str(chk.get(field)):
            errors.append(f"{clabel}: type '{ct}' requires non-empty '{field}'")
    if "path" in CHECK_TYPES[ct] and isinstance(chk.get("path"), str) \
            and not is_safe_relpath(chk["path"]):
        errors.append(f"{clabel}: path '{chk['path']}' must be relative with no '..' or leading slash")
    if "pattern" in CHECK_TYPES[ct] and isinstance(chk.get("pattern"), str):
        try:
            re.compile(chk["pattern"])
        except re.error as e:
            errors.append(f"{clabel}: invalid regex pattern: {e}")
    return errors


def _validate_outcome(ojson, ed):
    """Validate outcome.json; return a list of error strings."""
    errors = []
    if not ojson.exists():
        errors.append(f"missing {OUTCOME_JSON}")
        return errors
    try:
        data = json.loads(ojson.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"{OUTCOME_JSON}: invalid JSON: {e}")
        return errors
    if not isinstance(data, list) or not data:
        errors.append(f"{OUTCOME_JSON}: must be a non-empty JSON array")
        return errors
    seen = set()
    for idx, case in enumerate(data):
        label = f"{OUTCOME_JSON}[{idx}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: not an object")
            continue
        cid = case.get("id")
        if not _nonempty_str(cid):
            errors.append(f"{label}: missing/empty id")
        elif cid in seen:
            errors.append(f"{label}: duplicate id '{cid}'")
        else:
            seen.add(cid)
        if not _nonempty_str(case.get("prompt")):
            errors.append(f"{label}: missing/empty prompt")
        fx = case.get("fixture")
        if fx is not None:
            if not is_contained(ed, fx):
                errors.append(f"{label}: fixture '{fx}' must be a relative path inside evals/ (no '..', no absolute, no symlink escape)")
            elif not (ed / fx).is_dir():
                errors.append(f"{label}: fixture '{fx}' is not a directory")
        checks = case.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"{label}: checks must be a non-empty array")
            continue
        for cj, chk in enumerate(checks):
            errors.extend(_validate_check(chk, f"{label}.checks[{cj}]"))
    return errors


def validate(skill_dir):
    """Return (errors, warnings): lists of human-readable strings."""
    ed = evals_dir(skill_dir)
    trig_errors, trig_warnings = _validate_triggering(ed / TRIGGERING_CSV)
    outcome_errors = _validate_outcome(ed / OUTCOME_JSON, ed)
    return trig_errors + outcome_errors, trig_warnings
