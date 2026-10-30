import unittest
from iac_common.vm_evidence import vm_script_evidence

class VMEvidenceTests(unittest.TestCase):
    def test_bpg_style_keys_without_certifying_consumption(self):
        evidence = vm_script_evidence(
            'source "pve/vm-core.func"\nvm_start_script\nBRG VLAN STORAGE MAC vm_start_vm\n')
        self.assertTrue(evidence["uses_shared_unattended"])
        for key in ("vlan_id", "datastore_id", "mac_address", "started"):
            self.assertTrue(evidence["field_references"][key])
        self.assertEqual(evidence["validation"], "static_source_evidence_only")
        self.assertIn("memory", evidence["unverified_fields"])
