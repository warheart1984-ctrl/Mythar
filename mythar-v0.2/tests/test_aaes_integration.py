import unittest

from mythar.aaes import to_aaes_envelope
from mythar.core import MytharCompiler, REGISTRY_DIR


class AAESIntegrationTests(unittest.TestCase):
    def test_valid_mythar_compilation_projects_to_all_local_surfaces(self):
        compilation = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json").compile("ja ema")
        envelope = to_aaes_envelope(compilation)
        self.assertEqual(envelope["cmm"]["semantic_primitives"]["isf"]["root"], "ema")
        self.assertTrue(envelope["ccs"]["invariants_passed"])
        self.assertEqual(envelope["dos"]["decision_graph_status"], "candidate-input")
