"""Documentation contract checks; no runtime, credentials, or network access.

Run: python3 -B -m unittest discover -s tests -v
"""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = (
    "SKILL.md", "references/persona-http.md", "README.md",
    "README.zh-CN.md", "README.ja.md",
)
ACTIVE_DOCS = ENTRYPOINTS + (
    "references/api-reference.md", "references/operator-mode.md",
)
COMMANDS = (
    "37soul login",
    "37soul hosts [--name <exact-name>] [--limit <n>] [--offset <n>]",
    "37soul connect --name <exact-name> --agent <kind> --session <native-id>",
    "37soul connect --host <id> --agent <kind> --session <native-id>",
    "37soul whoami --host <id> [--agent <kind>] [--profile <id>]",
)


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class LocalAgentContractTest(unittest.TestCase):
    def test_persona_entrypoints_offer_account_and_soul_commands(self):
        missing = [f"{name}: {command}" for name in ENTRYPOINTS
                   for command in COMMANDS if f"`{command}`" not in read(name)]
        self.assertFalse(missing, "Missing local command contracts: " + repr(missing))

    def test_persona_guidance_covers_credential_and_session_boundaries(self):
        # These are safety invariants, not a test of runtime implementation.
        rules = {
            "local preference despite remote tool": r"even if .*remote.*whoami",
            "internal scoped credential": r"active local scoped credential.*identity JSON",
            "read only after connection": r"whoami.*read-only.*after connection",
            "no second authentication for an owned Soul": r"without a second login or OAuth",
            "no OAuth fallback": r"no remote OAuth fallback",
            "explicit connect grants only the chosen Soul": r"first explicit connect.*grants.*restores.*only.*owned Soul",
            "hook-supplied native context": r"managed hook context.*agent.*session",
            "no session guessing": r"never guess.*cwd.*recent sessions",
            "identity is not attachment": r"do not claim.*memory.*attached",
            "no token files": r"never read or write token files",
            "no credential output": r"never print credentials",
            "no callback paste": r"never ask.*paste.*localhost callback",
        }
        missing = [f"{name}: {label}"
                   for name in ("SKILL.md", "references/persona-http.md")
                   for label, pattern in rules.items()
                   if not re.search(pattern, " ".join(read(name).split()), re.I)]
        self.assertFalse(missing, "Missing safety boundaries: " + repr(missing))

    def test_account_login_does_not_select_soul_or_require_whoami_preflight(self):
        missing = [name for name in ("SKILL.md", "references/persona-http.md")
                   if not re.search(r"account-only.*no Soul selection.*"
                                    r"whoami.*not a prerequisite", " ".join(read(name).split()), re.I)]
        self.assertFalse(missing, "Old identity preflight still defines the flow: " + repr(missing))

    def test_owner_directory_is_minimal_and_name_resolution_never_guesses(self):
        rules = {
            "owner-only metadata directory": r"owner-only directory.*IDs, names and .*soul_uid.*only",
            "no initial identity preload": r"does not preload.*identity.*unselected Soul",
            "exact name matching": r"case-insensitive exact.*name",
            "duplicate names need human ID choice": r"duplicate.*refuses.*human.*ID",
            "zero matches must not fabricate": r"zero.*no replacement.*fabrication",
        }
        missing = [f"{name}: {label}"
                   for name in ("SKILL.md", "references/persona-http.md")
                   for label, pattern in rules.items()
                   if not re.search(pattern, " ".join(read(name).split()), re.I)]
        self.assertFalse(missing, "Missing owner-directory boundaries: " + repr(missing))

    def test_human_aliases_use_complete_directory_before_exact_connection(self):
        rules = {
            "displayed-name normalization": r"trimmed.*casefold.*displayed name",
            "aliases use unfiltered directory": r"alias or first name.*Sophia.*索菲亚.*unfiltered.*directory",
            "pagination before uniqueness": r"all pages.*total.*first partial match.*unique",
            "connect the identified target": r"connect.*returned ID or displayed full name",
        }
        missing = [f"{name}: {label}"
                   for name in ("SKILL.md", "references/persona-http.md", "references/api-reference.md")
                   for label, pattern in rules.items()
                   if not re.search(pattern, " ".join(read(name).split()), re.I)]
        missing += [f"{name}: {marker}" for name in ENTRYPOINTS
                    for marker in ("casefold", "索菲亚", "total", "--limit", "--offset")
                    if marker not in read(name)]
        self.assertFalse(missing, "Missing alias/pagination boundaries: " + repr(missing))

    def test_explicit_connect_keeps_revoked_or_disabled_consent_closed(self):
        missing = []
        for name in ("SKILL.md", "references/persona-http.md"):
            text = " ".join(read(name).split())
            if not re.search(r"rejects.*revoked or disabled.*consent.*never silently widen", text, re.I):
                missing.append(name)
        self.assertFalse(missing, "Missing consent refusal boundary: " + repr(missing))
        self.assertTrue("POST /hosts/:id/connection" in read("references/api-reference.md"),
                        "Document the runtime-managed connection operation")

    def test_targeted_login_is_not_default_or_recovery_in_active_docs(self):
        stale = [name for name in ACTIVE_DOCS if "37soul login --host" in read(name)]
        self.assertFalse(stale, "Targeted-login instructions remain in active docs: " + repr(stale))

    def test_active_docs_do_not_teach_hand_managed_token_files(self):
        unsafe = [name for name in ACTIVE_DOCS
                  if "credentials.json" in read(name) or "your_token_here" in read(name)]
        self.assertFalse(unsafe, "Hand-managed credential recipes remain: " + repr(unsafe))

    def test_local_creation_requires_an_image(self):
        violations = []
        for name in ENTRYPOINTS:
            text = read(name)
            if re.search(r"optional `--avatar|image is optional|stable default avatar", text):
                violations.append(name + ": optional/default avatar guidance")
            for block in re.findall(r"```bash\n(.*?)```", text, re.S):
                if "37soul soul create" in block and "--avatar" not in block:
                    violations.append(name + ": create example lacks --avatar")
        self.assertFalse(violations, "Image contract violations: " + repr(violations))

    def test_attachment_acknowledgement_and_hook_recovery_are_explicit(self):
        rules = {
            "start hook": r"SessionStart",
            "prompt hook": r"UserPromptSubmit",
            "unbound session context": r"even .*unbound",
            "explicit attachment acknowledgement": r"connection\.state == \"attached\"",
            "diagnosis before source retry": r"no hook source.*37soul doctor",
            "switch history isolation": r"fresh cloud .*session_ref.*byte cutoff",
            "no console restart": r"no console restart",
        }
        missing = [f"{name}: {label}"
                   for name in ("SKILL.md", "references/persona-http.md")
                   for label, pattern in rules.items()
                   if not re.search(pattern, " ".join(read(name).split()), re.I)]
        self.assertFalse(missing, "Missing runtime handoff contracts: " + repr(missing))

    def test_skill_does_not_freeze_the_number_of_agent_hosts(self):
        match = re.search(r"(?i)\b(?:four|five|six|[0-9]+) runtimes\b", read("SKILL.md"))
        self.assertFalse(match, "Skill hardcodes an agent runtime count")

    def test_gemini_cursor_hooks_do_not_promise_automatic_extraction(self):
        text = " ".join(read("SKILL.md").split())
        pattern = (r"Gemini and Cursor.*native session formats.*"
                   r"automatic extraction is currently unavailable.*"
                   r"safe, tool-free native invocation")
        self.assertTrue(re.search(pattern, text, re.I),
                        "Gemini/Cursor need an explicit hooks-only capability boundary")

    def test_manifest_descriptions_keep_approval_callbacks_out_of_chat(self):
        marketplace = json.loads(read("marketplace.json"))
        claude_marketplace = json.loads(read(".claude-plugin/marketplace.json"))
        descriptions = {
            "marketplace": marketplace["description"],
            "marketplace skill": marketplace["skills"][0]["description"],
            "plugin": json.loads(read(".claude-plugin/plugin.json"))["description"],
            "Claude marketplace": claude_marketplace["description"],
            "Claude marketplace plugin": claude_marketplace["plugins"][0]["description"],
        }
        missing = [name for name, text in descriptions.items()
                   if "Never ask users to paste credentials or localhost approval callback URLs."
                   not in text]
        self.assertFalse(missing, "Missing discovery-time callback prohibition: " + repr(missing))

    def test_local_bridge_requires_a_compatible_runtime_before_authentication(self):
        missing = [f"{name}: {version}" for name in ENTRYPOINTS
                   for version in ("0.15.1+", "0.14.2") if version not in read(name)]
        for name in ("SKILL.md", "references/persona-http.md"):
            text = " ".join(read(name).split())
            if not re.search(r"check.*installed runtime.*version.*before", text, re.I):
                missing.append(name + ": check installed runtime version before local commands")
            if not re.search(r"unknown command.*stop.*never run .*login.*OAuth", text, re.I):
                missing.append(name + ": unknown-command recovery must stop before auth")
        blockers = ("unpublished candidate", "compatible local candidate", "wait for its release",
                    "尚未发布的候选版本", "未公開の候補版")
        missing += [f"{name}: stale release blocker" for name in ENTRYPOINTS + ("references/api-reference.md",)
                    if any(blocker in read(name) for blocker in blockers)]
        self.assertFalse(missing, "Missing local runtime version gate: " + repr(missing))

    def test_skill_and_plugin_versions_match_latest_changelog(self):
        latest = re.search(r"^## (\d+\.\d+\.\d+) -", read("CHANGELOG.md"), re.M).group(1)
        self.assertEqual(latest, "6.14.0", "Formal skill release version")
        versions = {
            "SKILL.md": re.search(r"^  version: (.+)$", read("SKILL.md"), re.M).group(1),
            "marketplace.json": json.loads(read("marketplace.json"))["version"],
            ".claude-plugin/plugin.json": json.loads(read(".claude-plugin/plugin.json"))["version"],
        }
        self.assertEqual(versions, dict.fromkeys(versions, latest))


if __name__ == "__main__":
    unittest.main()
