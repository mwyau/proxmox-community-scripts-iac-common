"""Create a deterministic read-only recipe status index from scanner evidence.

This is advisory scan data, not an API contract or authorization to run installers.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

KNOWN = {
    "shared_engine_no_app_prompts_detected",
    "shared_engine_update_prompts_only",
    "shared_engine_wizard_prompt_review",
    "shared_engine_install_input_review",
    "custom_entrypoint",
    "syntax_error",
    "retired",
}


def build_status(scan: dict) -> dict:
    if scan.get("validation") != "static_only":
        raise ValueError("only static-only scanner evidence is accepted")
    scripts_ref, core_ref = scan.get("scripts_revision"), scan.get("core_revision")
    if not all(isinstance(x, str) and len(x) == 40 and all(ch in "0123456789abcdef" for ch in x)
               for x in (scripts_ref, core_ref)):
        raise ValueError("both source revisions must be immutable SHA-40 values")
    records = {}
    for row in [*scan.get("scripts", []), *scan.get("excluded_retired", [])]:
        kind, slug = row.get("kind"), row.get("slug")
        if kind not in ("lxc", "vm") or not isinstance(slug, str) or not slug:
            raise ValueError("invalid kind/slug")
        name = kind + "/" + slug
        if name in records:
            raise ValueError("duplicate recipe: " + name)
        is_retired = row.get("retirement") is not None
        assessment = "retired" if is_retired else row.get("assessment")
        if assessment not in KNOWN:
            raise ValueError("unknown assessment for " + name)
        records[name] = {
            "assessment": assessment,
            "kind": kind,
            "slug": slug,
            "engine": row.get("engine"),
            "retirement": row.get("retirement"),
            "syntax_ok": row.get("syntax_ok"),
            "shared_engine_unattended_contract": row.get("shared_engine_unattended_contract", False),
            "flags": row.get("flags", []),
            "prompt_sites": row.get("prompt_sites", []),
            "vm_field_evidence": row.get("vm_field_evidence"),
            "install_payload": row.get("install_payload"),
        }
    core_failures = [r.get("path") for r in scan.get("core", []) if r.get("syntax_ok") is False]
    return {
        "format_version": 1,
        "validation": "static_only",
        "warning": "This is read-only source evidence, not installation or unattended-compatibility certification.",
        "scripts_revision": scripts_ref,
        "core_revision": core_ref,
        "counts": dict(sorted(Counter(r["assessment"] for r in records.values()).items())),
        "core_syntax_failures": core_failures,
        "recipes": dict(sorted(records.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan", type=Path, required=True, help="Scanner compatibility.json")
    parser.add_argument("--output", type=Path, required=True, help="Status index recipes.json")
    args = parser.parse_args()
    data = json.loads(args.scan.read_text())
    status = build_status(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n")
    print("Recipe status: %s entries, %s retired" % (
        len(status["recipes"]), status["counts"].get("retired", 0)))


if __name__ == "__main__":
    main()
