"""Status index is reproducible and never claims install success."""
import unittest

from iac_common.status import build_status


class StatusTests(unittest.TestCase):
    def scan(self):
        return {
            "validation": "static_only",
            "scripts_revision": "a" * 40,
            "core_revision": "b" * 40,
            "scripts": [
                {"kind": "lxc", "slug": "adguard", "assessment": "shared_engine_no_app_prompts_detected",
                 "retirement": None, "flags": [], "syntax_ok": True}
            ],
            "excluded_retired": [
                {"kind": "lxc", "slug": "old", "assessment": "retired", "retirement": {
                    "status": "retired", "reason": "removed", "successor": None}}
            ],
            "core": [],
        }

    def test_index_and_precise_warning(self):
        out = build_status(self.scan())
        self.assertEqual(list(out["recipes"]), ["lxc/adguard", "lxc/old"])
        self.assertEqual(out["counts"]["retired"], 1)
        self.assertEqual(out["recipes"]["lxc/old"]["assessment"], "retired")
        self.assertEqual(out["validation"], "static_only")
        self.assertIn("not installation", out["warning"])

    def test_rejects_mutable_revisions(self):
        x = self.scan()
        x["scripts_revision"] = "main"
        with self.assertRaises(ValueError):
            build_status(x)

    def test_rejects_duplicate_identity(self):
        x = self.scan()
        x["scripts"].append(dict(x["scripts"][0]))
        with self.assertRaises(ValueError):
            build_status(x)

    def test_rejects_unverified_status(self):
        x = self.scan()
        x["scripts"][0]["assessment"] = "supported"
        with self.assertRaises(ValueError):
            build_status(x)

    def test_rejects_nonstatic_scans(self):
        x = self.scan()
        x["validation"] = "live"
        with self.assertRaises(ValueError):
            build_status(x)
