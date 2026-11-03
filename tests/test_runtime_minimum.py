"""Guard the active documentation against admitting the broken 0.15.0 runtime."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_GUIDES = (
    "SKILL.md", "README.md", "README.zh-CN.md", "README.ja.md",
    "references/persona-http.md", "references/api-reference.md",
)


class RuntimeMinimumTest(unittest.TestCase):
    def test_active_minimum_excludes_runtime_0150(self):
        expected = (0, 15, 1)
        failures = []
        for name in ACTIVE_GUIDES:
            text = (ROOT / name).read_text(encoding="utf-8")
            declared = re.findall(r"(\d+\.\d+\.\d+)\+", text)
            # Check upgrade conditions as well as the headline minimum.
            bounds = re.findall(r"(?:older than|低于)\s*(\d+\.\d+\.\d+)", text)
            bounds += re.findall(r"(\d+\.\d+\.\d+)\s*未満", text)
            if not declared or any(tuple(map(int, value.split("."))) != expected
                                   for value in declared + bounds):
                failures.append(f"{name}: minima={declared}, upgrade bounds={bounds}")
        self.assertFalse(failures, "Runtime 0.15.0 must not pass the active version gate: "
                         + repr(failures))


if __name__ == "__main__":
    unittest.main()
