import unittest

from mythar.dos_benchmark import run_a01_benchmark


class DOSBenchmarkTests(unittest.TestCase):
    def test_a01_is_deterministic_and_traceable(self):
        report = run_a01_benchmark()
        self.assertTrue(report["deterministic"])
        self.assertTrue(report["traceability_complete"])
        self.assertEqual(len(report["hashes"]), 3)
