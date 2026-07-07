#!/usr/bin/env python3
"""Compute the three component metrics + composite, and persist run history.

Component metrics are reported separately (a blend hides regressions); the
composite is a single tunable headline. History is appended one line per run to
<skill>/evals/results/history.jsonl, keyed by timestamp, git SHA, skill version
and model, so different models trend separately (and feed a future dashboard).
"""
from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path

# Composite weights — value dominates. Tunable; must sum to 1.0.
W_TRIGGER = 0.25
W_OUTCOME = 0.35
W_VALUE = 0.40


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _pass_rate(check_results):
    """Fraction of decided checks (pass in True/False) that passed."""
    decided = [c for c in check_results if isinstance(c.get("pass"), bool)]
    if not decided:
        return 0.0
    return sum(c["pass"] for c in decided) / len(decided)


def compute_metrics(trigger_results, outcome_with, outcome_baseline, has_triggering=True):
    """trigger_results: [{pass}]. outcome_*: flat lists of check-result dicts.

    Two recipes for the composite:
    - model-invoked (`has_triggering=True`): weight all three components.
    - user-invoked (`has_triggering=False`): nothing fires on its own, so drop
      the triggering term and renormalise the remaining weights to sum to 1.
      `trigger_accuracy` is reported as None.
    """
    outcome_pass_rate = _pass_rate(outcome_with)
    baseline_pass_rate = _pass_rate(outcome_baseline)
    value_delta = outcome_pass_rate - baseline_pass_rate
    if has_triggering:
        trig_total = len(trigger_results)
        trigger_accuracy = (sum(1 for r in trigger_results if r.get("pass")) / trig_total
                            if trig_total else 0.0)
        composite = 100.0 * (
            W_TRIGGER * trigger_accuracy
            + W_OUTCOME * outcome_pass_rate
            + W_VALUE * _clamp(value_delta)
        )
        trig_out = round(trigger_accuracy, 4)
    else:
        denom = W_OUTCOME + W_VALUE
        composite = 100.0 * (
            (W_OUTCOME / denom) * outcome_pass_rate
            + (W_VALUE / denom) * _clamp(value_delta)
        )
        trig_out = None
    return {
        "trigger_accuracy": trig_out,
        "outcome_pass_rate": round(outcome_pass_rate, 4),
        "baseline_pass_rate": round(baseline_pass_rate, 4),
        "value_delta": round(value_delta, 4),
        "composite": round(composite, 1),
    }


def skill_version(skill_dir):
    manifest = Path(skill_dir) / ".claude-plugin" / "plugin.json"
    try:
        return json.loads(manifest.read_text()).get("version", "unknown")
    except (OSError, json.JSONDecodeError):
        return "unknown"


def git_sha(repo_dir):
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def build_record(skill_dir, skill_name, model, metrics, cases, timestamp=None):
    ts = timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "ts": ts,
        "skill": skill_name,
        "skill_version": skill_version(skill_dir),
        "model": model,
        "git_sha": git_sha(skill_dir),
        **metrics,
        "cases": cases,
    }


def append_history(skill_dir, record):
    results_dir = Path(skill_dir) / "evals" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / "history.jsonl"
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")
    return path


if __name__ == "__main__":
    # Self-test with synthetic inputs: both recipes.
    trig = [{"pass": True}, {"pass": True}, {"pass": False}]
    with_skill = [{"pass": True}, {"pass": True}, {"pass": True}]
    baseline = [{"pass": True}, {"pass": False}, {"pass": False}]
    print("model-invoked:",
          json.dumps(compute_metrics(trig, with_skill, baseline), indent=2))
    print("user-invoked :",
          json.dumps(compute_metrics([], with_skill, baseline, has_triggering=False),
                     indent=2))
