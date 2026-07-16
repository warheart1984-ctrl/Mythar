import unittest

from mythar import compile_expression
from mythar.conformance import run_conformance


class MytharCompilerTests(unittest.TestCase):
    def test_particle_frame_and_lineage(self):
        result = compile_expression("ja tor")
        self.assertTrue(result["valid"])
        self.assertEqual(result["lineage"]["particle_frame"], "PARTICLE-JA")
        self.assertEqual(result["lineage"]["roots"], ["ROOT-TOR"])
        self.assertEqual(result["diagnostics"], [])

    def test_compound_segmentation(self):
        result = compile_expression("kala")
        self.assertTrue(result["valid"])
        self.assertEqual(result["lineage"]["roots"], ["ROOT-KA", "ROOT-LA"])

    def test_unknown_token_is_rejected(self):
        result = compile_expression("ema")
        self.assertFalse(result["valid"])
        self.assertEqual(result["diagnostics"][0]["code"], "E_UNKNOWN_TOKEN")

    def test_registry_conformance_suite(self):
        report = run_conformance()
        self.assertEqual(report["failed"], 0, report)


if __name__ == "__main__":
    unittest.main()
