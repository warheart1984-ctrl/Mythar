import unittest

from mythar.core import MytharCompiler, REGISTRY_DIR


class MandarinISFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiler = MytharCompiler(extension=REGISTRY_DIR / "registry-v0.3.json")

    def test_mandarin_light_to_isf(self):
        isf = self.compiler.compile_v2("光", source_language="zh", format="isf")
        self.assertEqual(isf["root"], "la")
        self.assertEqual(isf["class"], "illumination")
        self.assertEqual(isf["intent"], "reveal")

    def test_mandarin_speak_to_isf(self):
        isf = self.compiler.compile_v2("说", source_language="zh", format="isf")
        self.assertEqual(isf["root"], "ra")
        self.assertEqual(isf["domain"], "speech")

    def test_mandarin_collective_to_isf(self):
        isf = self.compiler.compile_v2("集体", source_language="zh", format="isf")
        self.assertEqual(isf["root"], "rum")
        self.assertEqual(isf["intent"], "unite")
