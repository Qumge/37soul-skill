from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
class CodexHookless(unittest.TestCase):
 def test_codex_uses_runtime_host_environment_without_manual_hook_review(self):
  for name in ['SKILL.md','references/persona-http.md']:
   text=' '.join((ROOT/name).read_text().split())
   self.assertIn('Runtime 0.17.0',text)
   self.assertIn('CODEX_THREAD_ID',text)
   self.assertRegex(text,r'(?i)Codex.*do not ask.*?/hooks')
   self.assertIn('37soul context',text)
   self.assertIn('37soul connect --host <id>',text)
 def test_public_guides_explain_the_codex_exception(self):
  for name in ['README.md','README.zh-CN.md','README.ja.md']:
   text=(ROOT/name).read_text()
   self.assertIn('0.17.0',text)
   self.assertIn('CODEX_THREAD_ID',text)
   self.assertIn('37soul context',text)
