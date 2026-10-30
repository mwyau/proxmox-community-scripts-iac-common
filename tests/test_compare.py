"""Changes to static scan evidence are reported separately from installation results."""
import unittest

from iac_common.compare import compare, markdown


class CompareTests(unittest.TestCase):
    def report(self, recipes, scripts_sha="a", core_sha="b"):
        return {
            "format_version": 1,
            "validation": "static_only",
            "scripts_revision": scripts_sha * 40,
            "core_revision": core_sha * 40,
            "recipes": recipes,
        }

    def entry(self, kind, slug, assessment, **kwargs):
        return {"kind": kind, "slug": slug, "assessment": assessment, **kwargs}

    def test_add_remove_and_reclassification(self):
        before = self.report({
            "lxc/old": self.entry("lxc", "old", "retired"),
            "lxc/adguard": self.entry("lxc", "adguard", "shared_engine_no_app_prompts_detected"),
        })
        after = self.report({
            "lxc/adguard": self.entry("lxc", "adguard", "shared_engine_install_input_review",
                                      flags=["application_input_review"]),
            "vm/ubuntu-vm": self.entry("vm", "ubuntu-vm", "custom_entrypoint"),
        }, scripts_sha="c")
        result = compare(before, after)
        self.assertEqual(result["added"], ["vm/ubuntu-vm"])
        self.assertEqual(result["removed"], ["lxc/old"])
        self.assertEqual(result["counts"], {"added": 1, "removed": 1, "changed": 1})
        self.assertEqual(result["changed"]["lxc/adguard"]["assessment_before"],
                         "shared_engine_no_app_prompts_detected")
        self.assertEqual(result["changed"]["lxc/adguard"]["assessment_after"],
                         "shared_engine_install_input_review")
        self.assertIn("flags", result["changed"]["lxc/adguard"]["changed_fields"])
        self.assertIn("Recorded static evidence".lower().split()[1], markdown(result).lower())

    def test_same_evidence_with_different_sha_is_not_source_parity(self):
        entries = {"lxc/adguard": self.entry("lxc", "adguard", "custom_entrypoint")}
        result = compare(self.report(entries), self.report(entries, "c"))
        self.assertEqual(result["counts"]["changed"], 0)
        self.assertNotEqual(result["before"]["scripts_revision"],
                            result["after"]["scripts_revision"])
        self.assertIn("does not establish identical source", result["warning"])

    def test_prompt_evidence_without_status_change(self):
        a = self.entry("lxc", "adguard", "shared_engine_install_input_review", prompt_sites=[])
        b = self.entry("lxc", "adguard", "shared_engine_install_input_review",
                       prompt_sites=[{"line": 12, "operation": "msg_menu"}])
        out = compare(self.report({"lxc/adguard": a}), self.report({"lxc/adguard": b}))
        self.assertEqual(out["changed"]["lxc/adguard"]["changed_fields"], ["prompt_sites"])

    def test_rejects_unpinned_and_invalid_input(self):
        out = self.report({})
        out["scripts_revision"] = "main"
        with self.assertRaises(ValueError):
            compare(out, out)
        out = self.report({"lxc/../escape": self.entry("lxc", "adguard", "retired")})
        with self.assertRaises(ValueError):
            compare(out, out)
        out = self.report({"lxc/adguard": self.entry("lxc", "adguard", "supported")})
        with self.assertRaises(ValueError):
            compare(out, out)
        out = self.report({"lxc/adguard": {"kind": 120, "slug": "adguard", "assessment": "retired"}})
        with self.assertRaises(ValueError):
            compare(out, out)
        out = self.report({})
        out["validation"] = "live"
        with self.assertRaises(ValueError):
            compare(out, out)
