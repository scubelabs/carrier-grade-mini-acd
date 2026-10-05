"""Checks for M1 cross-component and environment template boundaries."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validation", ROOT / "scripts/validate-config.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)

class LabConfigTests(unittest.TestCase):
    def test_cross_component_references(self):
        validation.validate()
        validation.validate("192.168.1.20")

    def test_entrypoints_reject_injection_and_invalid_octets(self):
        for component in ("kamailio", "freeswitch"):
            for value in ("127.0.0.1/;bad", "256.1.2.3", "1.2.3", "1..2.3", "::1"):
                with self.subTest(component=component, value=value):
                    result = subprocess.run(["sh", str(ROOT / component / "entrypoint.sh"), "true"], env={**os.environ, "LAB_PUBLIC_IP": value}, capture_output=True)
                    self.assertNotEqual(result.returncode, 0)

    def test_entrypoints_render_and_preserve_arguments(self):
        for component, filename in (("kamailio", "kamailio.cfg"), ("freeswitch", "freeswitch.xml")):
            with self.subTest(component=component), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                template = ROOT / component / (filename if component == "kamailio" else "conf/freeswitch.xml")
                (folder / (filename + ".template")).write_text(template.read_text())
                script = (ROOT / component / "entrypoint.sh").read_text().replace(f"/etc/{component}", temp)
                target = folder / "entrypoint.sh"
                target.write_text(script)
                result = subprocess.run(["sh", str(target), "printf", "%s", "argument with spaces"], env={**os.environ, "LAB_PUBLIC_IP": "192.168.1.20"}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "argument with spaces")
                rendered = (folder / filename).read_text()
                self.assertNotIn("__LAB_PUBLIC_IP__", rendered)
                self.assertIn("192.168.1.20", rendered)

if __name__ == "__main__":
    unittest.main()
