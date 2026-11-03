"""Selected persona contract; static documentation only, no native/model access."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SelectedSoulContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.persona = " ".join(skill.split("## Persona mode: speaking as her", 1)[1]
                               .split("## Persistent soul", 1)[0].split())

    def test_selected_connected_identity_is_current_session_persona(self):
        self.assertRegex(self.persona, r"(?i)(?:selected|connected) Soul.*identity.*persona.*(?:current|this) session")

    def test_soul_file_is_optional_across_agents(self):
        self.assertRegex(self.persona, r"(?i)SOUL\.md.*optional")
        self.assertRegex(self.persona, r"(?i)(?:not every|not all).*Agent|(?:without|does not require).*SOUL\.md")

    def test_local_default_does_not_require_name_reconciliation_or_import_export(self):
        self.assertRegex(self.persona, r"(?i)local default.*(?:differ|another name|match)")
        self.assertRegex(self.persona, r"(?i)(?:no|without|does not require).*name (?:comparison|reconciliation).*import.*export.*(?:reply|speak)")

    def test_connecting_and_replying_leave_local_files_unchanged(self):
        self.assertRegex(self.persona, r"(?i)(?:leave|keep).*local files.*unchanged.*(?:connect|reply)")

    def test_file_operations_require_explicit_request_and_existing_authorization(self):
        self.assertRegex(self.persona, r"(?i)file operations.*existing authorization.*only when.*user explicitly requests")

    def test_active_persona_guides_remove_universal_soul_file_authority(self):
        stale = []
        patterns = (
            r"your SOUL\.md keeps who she is",
            r"the person your SOUL\.md describes",
            r"if your SOUL\.md uses another name, go by hers and tell them once",
        )
        for name in ("SKILL.md", "references/persona-http.md"):
            text = " ".join((ROOT / name).read_text(encoding="utf-8").split())
            stale.extend(name + ": " + pattern for pattern in patterns
                         if re.search(pattern, text, re.I))
        self.assertFalse(stale, "Old universal-file/name-reconciliation guidance: " + repr(stale))


if __name__ == "__main__":
    unittest.main()
