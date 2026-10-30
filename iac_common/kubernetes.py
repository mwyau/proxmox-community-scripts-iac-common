"""Read curated container, Helm, and operator references for Community Scripts.

References document deployment options; they do not establish installation
success, image/chart-version compatibility, or safe configuration migration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import urlparse

DATA = Path(__file__).resolve().parents[1] / "data" / "kubernetes-alternatives.json"
SHA = re.compile(r"^[0-9a-f]{40}$")
KEY = re.compile(r"^(?:lxc|vm)/[a-z0-9][a-z0-9-]*$")
IMAGE = re.compile(r"^[a-z0-9][a-z0-9./_-]+$")
CHART = re.compile(r"^[a-z0-9][a-z0-9./_-]+$")


def _https(url: object) -> bool:
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return (parsed.scheme == "https" and bool(parsed.hostname)
            and not parsed.username and not parsed.password
            and not parsed.fragment)


def load_catalog(path: Path = DATA) -> dict:
    """Validate curated source references and return the checked catalog."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("format_version") != 1
            or not isinstance(data.get("scripts_revision"), str)
            or not SHA.fullmatch(data["scripts_revision"])
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data.get("reviewed_on", ""))):
        raise ValueError("invalid catalog metadata")
    entries = data.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise ValueError("missing curated entries")
    for key, record in entries.items():
        if not isinstance(key, str) or not KEY.fullmatch(key) or not isinstance(record, dict):
            raise ValueError("invalid recipe record: " + str(key))
        kind, slug = key.split("/")
        path = "ct" if kind == "lxc" else "vm"
        expected = ("https://github.com/community-scripts/ProxmoxVE/blob/"
                    + data["scripts_revision"] + "/" + path + "/" + slug + ".sh")
        if record.get("recipe_source") != expected:
            raise ValueError("recipe source must name the reviewed script SHA: " + key)
        if not isinstance(record.get("application"), str) or not record["application"].strip():
            raise ValueError("missing application: " + key)
        for category, required in (
            ("images", ("reference", "documentation", "publisher")),
            ("helm_charts", ("name", "reference", "documentation", "publisher")),
            ("operators", ("name", "documentation", "publisher")),
        ):
            rows = record.get(category)
            # Null is unknown/unreviewed, not evidence that the option does not exist.
            if rows is None:
                continue
            if not isinstance(rows, list) or not rows:
                raise ValueError("non-null categories must contain reviewed references: " + key)
            for row in rows:
                if not isinstance(row, dict) or any(
                    not isinstance(row.get(field), str) or not row[field].strip()
                    for field in required
                ):
                    raise ValueError("incomplete reference: " + key + "/" + category)
                if not _https(row["documentation"]):
                    raise ValueError("invalid reference URL: " + key)
                if row["publisher"] not in ("application", "community"):
                    raise ValueError("unknown publisher: " + key)
                if category == "images" and not IMAGE.fullmatch(row["reference"]):
                    raise ValueError("invalid container image reference: " + key)
                if category == "helm_charts":
                    ref = row["reference"]
                    if not (CHART.fullmatch(ref)
                            or (ref.startswith("oci://") and
                                CHART.fullmatch(ref.removeprefix("oci://")))):
                        raise ValueError("invalid Helm chart reference: " + key)
        notes = record.get("notes")
        if not isinstance(notes, list) or any(
            not isinstance(note, str) or not note.strip() for note in notes
        ):
            raise ValueError("invalid recipe notes: " + key)
    return data


def validate_against_status(catalog: dict, status: dict) -> list[str]:
    """Check membership at the reviewed script revision in a full scan.

    This is a catalog consistency check, not evidence of Kubernetes support.
    """
    if (not isinstance(status, dict) or status.get("format_version") != 1
            or status.get("validation") != "static_only"
            or status.get("scripts_revision") != catalog["scripts_revision"]):
        raise ValueError("scan must have the same immutable scripts revision")
    recipes = status.get("recipes")
    if not isinstance(recipes, dict):
        raise ValueError("scan has no recipes index")
    missing = sorted(set(catalog["entries"]) - set(recipes))
    return missing


def _count(values: object) -> str:
    return "unknown" if values is None else str(len(values))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DATA)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list", help="List reviewed recipe alternatives")
    show = sub.add_parser("show", help="Show a recipe's references")
    show.add_argument("recipe", help="Kind/slug, e.g. lxc/immich")
    validate = sub.add_parser("validate", help="Check entries against a full pinned scan")
    validate.add_argument("--recipes", required=True, type=Path)
    args = parser.parse_args()
    catalog = load_catalog(args.catalog)
    if args.action == "list":
        print("Review date: " + catalog["reviewed_on"])
        print("Recipe\tImages\tHelm\tOperators")
        for name, row in sorted(catalog["entries"].items()):
            print("\t".join((name, _count(row["images"]), _count(row["helm_charts"]),
                             _count(row["operators"]))))
    elif args.action == "show":
        record = catalog["entries"].get(args.recipe)
        if record is None:
            parser.error("no reviewed entry for " + args.recipe)
        print(json.dumps({"reviewed_on": catalog["reviewed_on"],
                          "scripts_revision": catalog["scripts_revision"],
                          "recipe": args.recipe, **record}, indent=2))
    else:
        status = json.loads(args.recipes.read_text(encoding="utf-8"))
        missing = validate_against_status(catalog, status)
        if missing:
            parser.error("recipes absent from pinned scan: " + ", ".join(missing))
        print("All %d reviewed entries occur in the pinned recipe scan." %
              len(catalog["entries"]))


if __name__ == "__main__":
    main()
