"""Curated deployment references are validated independently of live services."""
import json
import tempfile
import unittest
from pathlib import Path

from iac_common.kubernetes import load_catalog, validate_against_status


class KubernetesIndexTests(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()

    def test_real_entries_and_explicit_unknowns(self):
        entries = self.catalog["entries"]
        self.assertEqual(len(entries), 8)
        self.assertEqual(entries["lxc/immich"]["helm_charts"][0]["publisher"], "application")
        self.assertEqual(entries["lxc/prometheus"]["operators"][0]["publisher"], "community")
        self.assertIsNone(entries["lxc/adguard"]["helm_charts"])
        self.assertIsNone(entries["lxc/forgejo"]["operators"])

    def save(self, change):
        data = json.loads(json.dumps(self.catalog))
        change(data)
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "kubernetes.json"
            p.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                load_catalog(p)

    def test_reject_missing_sha_and_mismatched_path(self):
        self.save(lambda d: d.update(scripts_revision="main"))
        self.save(lambda d: d["entries"]["lxc/immich"].update(recipe_source="https://evil.test/script.sh"))

    def test_reject_unreviewed_or_untrusted_links(self):
        self.save(lambda d: d["entries"]["lxc/gitea"]["helm_charts"][0].update(
            documentation="http://example.org/chart"))
        self.save(lambda d: d["entries"]["lxc/gitea"]["helm_charts"][0].update(
            publisher="certified"))
        self.save(lambda d: d["entries"]["lxc/adguard"].update(helm_charts=[]))
        self.save(lambda d: d["entries"]["lxc/immich"]["images"][0].update(
            reference="example.org/image;sh -c evil"))

    def test_scan_membership_requires_matching_revision(self):
        report = {"format_version": 1, "validation": "static_only",
                  "scripts_revision": self.catalog["scripts_revision"],
                  "recipes": {k: {} for k in self.catalog["entries"]}}
        self.assertEqual(validate_against_status(self.catalog, report), [])
        del report["recipes"]["lxc/forgejo"]
        self.assertEqual(validate_against_status(self.catalog, report), ["lxc/forgejo"])
        report["scripts_revision"] = "b" * 40
        with self.assertRaises(ValueError):
            validate_against_status(self.catalog, report)

    def test_no_install_command_or_claim(self):
        import inspect
        from iac_common import kubernetes
        source = inspect.getsource(kubernetes)
        for forbidden in ("subprocess.run(", "helm install", "kubectl apply", "requests.get("):
            self.assertNotIn(forbidden, source)
