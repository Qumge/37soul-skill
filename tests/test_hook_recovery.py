"""Offline policy regressions for missing native hook context; no model calls."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ("SKILL.md", "references/persona-http.md")


def recovery(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    return " ".join(text.split("4. **No native session context.**", 1)[1]
                    .split("5. **Account credentials", 1)[0].split())


class HookRecoveryTest(unittest.TestCase):
    def test_missing_context_runs_a_bounded_diagnostic_before_recovery(self):
        for name in GUIDES:
            with self.subTest(guide=name):
                text = recovery(name)
                self.assertIn("37soul doctor", text)
                self.assertRegex(text, r"(?i)(?:one|once|single).*diagnostic|diagnostic.*(?:one|once|single)")

    def test_automatic_diagnosis_requires_the_readonly_runtime_fix(self):
        for name in GUIDES:
            with self.subTest(guide=name):
                text = recovery(name)
                self.assertRegex(text, r"(?i)Runtime 0\.16\.2.*(?:before|then|after).*37soul doctor")
                self.assertRegex(text, r"(?i)(?:older|unknown).*official.*(?:upgrad|install)")
                self.assertRegex(text, r"(?i)(?:never|do not).*doctor.*version probe")

    def test_known_target_is_retained_and_never_needs_a_repeated_selection(self):
        for name in GUIDES:
            with self.subTest(guide=name):
                text = recovery(name)
                self.assertRegex(text, r"(?i)preserve.*(?:requested|original|chosen).*Soul")
                self.assertRegex(text, r"(?i)do not ask.*repeat.*(?:choice|selection|connection request)")
                self.assertRegex(text, r"(?i)resume.*(?:same|original).*request")

    def test_native_review_is_human_owned_and_no_evidence_is_not_rejection(self):
        for name in GUIDES:
            with self.subTest(guide=name):
                text = recovery(name)
                self.assertIn("/hooks", text)
                self.assertRegex(text, r"(?i)(?:user|human).*approv|approv.*(?:user|human)")
                self.assertRegex(text, r"(?i)(?:not|never).*infer.*(?:trust|load)")

    def test_prompt_refresh_is_conditional_and_not_a_repeat_request_loop(self):
        for name in GUIDES:
            with self.subTest(guide=name):
                text = recovery(name)
                self.assertNotRegex(text, r"(?i)if there is no hook source, tell the user to send")
                self.assertRegex(text, r"(?i)only after.*(?:trust|load).*verified.*(?:normal|next).*turn")
                self.assertRegex(text, r"(?i)continue.*(?:enough|sufficient)|(?:enough|sufficient).*continue")
                self.assertRegex(text, r"(?i)(?:no|never|do not).*retry loop")

    def test_public_readmes_explain_diagnostics_and_native_hook_review(self):
        stale = ("If connect reports missing native source, stop and use the next managed message",
                 "Missing native hook context requires the next message",
                 "memory attachment; send the next message",
                 "缺少原生 hook 上下文时等待下一条消息",
                 "缺少原生 source 时停止当前连接，等下一条消息")
        for name in ("README.md", "README.zh-CN.md", "README.ja.md"):
            with self.subTest(guide=name):
                text = (ROOT / name).read_text(encoding="utf-8")
                self.assertIn("37soul doctor", text)
                self.assertIn("/hooks", text)
                for phrase in stale:
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
