"""Compare evidence recorded by two recipe-status scans.

The result describes changes in recorded assessments, not changes to every
byte of upstream recipe source.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from .status import KNOWN

SOURCE_SHA = re.compile(r"^[0-9a-f]{40}$")
EVIDENCE_FIELDS = (
    "assessment", "engine", "retirement", "syntax_ok",
    "shared_engine_unattended_contract", "flags", "prompt_sites",
    "vm_field_evidence", "install_payload",
)


def _check(report: dict) -> None:
    if not isinstance(report, dict) or report.get("format_version") != 1:
        raise ValueError("expected recipe-status format_version 1")
    if report.get("validation") != "static_only":
        raise ValueError("expected a static-only recipe status report")
    if any(not isinstance(report.get(k), str) or not SOURCE_SHA.fullmatch(report[k])
           for k in ("scripts_revision", "core_revision")):
        raise ValueError("report must record immutable scripts and Core SHAs")
    recipes = report.get("recipes")
    if not isinstance(recipes, dict):
        raise ValueError("missing recipes map")
    for key, row in recipes.items():
        if (not isinstance(key, str) or
            not re.fullmatch(r"(?:lxc|vm)/[a-z0-9][a-z0-9-]*", key) or
            not isinstance(row, dict) or row.get("assessment") not in KNOWN or
            row.get("kind") not in ("lxc", "vm") or
            not isinstance(row.get("slug"), str) or
            key != row["kind"] + "/" + row["slug"]):
            raise ValueError("invalid recipe record: " + str(key))


def compare(before: dict, after: dict) -> dict:
    """Return added, removed, and changed recorded recipe evidence."""
    _check(before)
    _check(after)
    previous, current = before["recipes"], after["recipes"]
    changed = {}
    for key in sorted(previous.keys() & current.keys()):
        fields = [name for name in EVIDENCE_FIELDS
                  if previous[key].get(name) != current[key].get(name)]
        if fields:
            changed[key] = {
                "assessment_before": previous[key]["assessment"],
                "assessment_after": current[key]["assessment"],
                "changed_fields": fields,
            }
    added = sorted(current.keys() - previous.keys())
    removed = sorted(previous.keys() - current.keys())
    return {
        "comparison": "recorded_static_evidence",
        "before": {
            "scripts_revision": before["scripts_revision"],
            "core_revision": before["core_revision"],
        },
        "after": {
            "scripts_revision": after["scripts_revision"],
            "core_revision": after["core_revision"],
        },
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {"added": len(added), "removed": len(removed), "changed": len(changed)},
        "warning": "Equal scan evidence does not establish identical source or successful installation.",
    }


def markdown(delta: dict) -> str:
    """Summarize evidence changes; no ordering by presumed risk."""
    lines = [
        "# Recipe scan comparison",
        "",
        "Before Scripts: `" + delta["before"]["scripts_revision"] + "`",
        "Before Core: `" + delta["before"]["core_revision"] + "`",
        "After Scripts: `" + delta["after"]["scripts_revision"] + "`",
        "After Core: `" + delta["after"]["core_revision"] + "`",
        "",
        "Compared recorded static evidence. No installers were executed.",
        "",
        "| Change | Number |",
        "| --- | ---: |",
        "| Added recipes | %d |" % delta["counts"]["added"],
        "| Removed recipes | %d |" % delta["counts"]["removed"],
        "| Changed evidence | %d |" % delta["counts"]["changed"],
        "",
    ]
    for key, values in (("added", delta["added"]), ("removed", delta["removed"])):
        if values:
            lines.extend(["## " + key.title(), ""])
            lines.extend("- `" + name + "`" for name in values)
            lines.append("")
    if delta["changed"]:
        lines += ["## Changed recorded evidence", "",
                  "| Recipe | Assessment before | Assessment after | Changed fields |",
                  "| --- | --- | --- | --- |"]
        for name, row in delta["changed"].items():
            lines.append("| `%s` | %s | %s | %s |" % (
                name, row["assessment_before"], row["assessment_after"],
                ", ".join(row["changed_fields"])))
        lines.append("")
    lines += [delta["warning"], ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("out/changes.json"))
    parser.add_argument("--markdown", type=Path, default=Path("out/changes.md"))
    args = parser.parse_args()
    delta = compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(delta, indent=2) + "\n")
    args.markdown.write_text(markdown(delta))
    print("Evidence changes: %d added, %d removed, %d changed" %
          (delta["counts"]["added"], delta["counts"]["removed"], delta["counts"]["changed"]))


if __name__ == "__main__":
    main()
