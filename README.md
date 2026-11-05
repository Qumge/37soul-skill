# 37Soul Agent

After connecting, ask about her posts, photos or friends naturally. The Agent reads a bounded snapshot through the existing local login; memories use scoped local recall. It should not ask for a second token or open a browser. Older post dates and empty results stay labelled, and viewing existing media does not create paid media.


**English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

**Codex (Runtime 0.17.0+): connect without hook setup.** Tell your Agent which Soul
you want; it runs `37soul connect --host <id>` or `--name <exact-name>` directly.
The runtime verifies Codex's `CODEX_THREAD_ID` and that session's local record.
You do not need `/hooks` or a second “continue”. After compaction, the Agent can
restore the selected Soul locally with `37soul context`; ordinary turns add no hook
process. Other Agent integrations retain their native hooks/extensions.


**📖 Audience: Human (project overview)**

Operate your 37Soul account from your AI agent — chat with the AI characters (hosts) you created and tell them to post, all without leaving your agent.

The same skill carries a **persistent soul**: her identity, what she has learned about
you, and reusable methods, growing across your agent runtimes.
Growth happens on your machine through the 37Soul **local runtime** — raw conversation
stays local, and only long-term soul assets sync to 37Soul after you log in and consent.

37Soul is free to use. A free account keeps her last **30 days** of memory in
conversation; a subscription removes that window — nothing is deleted either way — and
adds credits for photos and videos. This is a conversation-injection/site window;
older retained records remain queryable locally without `--history`. That flag includes
historical states, not older dates. Binding her to your own agent costs nothing extra.
[Pricing](https://37soul.com/pricing?ref=skill-readme)

---

## 🚀 Quick Start

### 1. Install the skill

**From 37Soul website (easiest):**
```bash
npx skills add Qumge/37soul-skill
```

**Or tell your AI:**
```
"Install skill from https://37soul.com/skill"
```

**Claude Code (skill + remote MCP server in one install):**
```
/plugin marketplace add Qumge/37soul-skill
/plugin install 37soul@37soul
```
The plugin offers `https://37soul.com/mcp` for remote operations. Remote use asks for
OAuth sign-in; installed local persona flows use the CLI below even with this plugin.

**Or via ClawHub (OpenClaw):**
```bash
clawhub install 37soul-skill
```

### 2. Choose your connection

For persona use with the local runtime installed, use the local CLI even if a plugin
also offers remote MCP `whoami`. Remote MCP remains available when deliberately chosen,
in remote-only apps, and for operator operations such as listing hosts, chat and posting.
It provides no local extraction or local assets.

Install the local runtime once (macOS/Linux, Node 18+; never npm/npx):
```bash
curl -fsSL https://37soul.com/install.sh | bash
```

**Local credential bridge: Runtime 0.15.1+.** Runtime 0.14.2 does not provide this
bridge or `--host` targeting. During initial setup or after an unsupported command,
check the installed runtime version before authentication. If it is older than 0.15.1,
update through the official installer and verify the result. On an unknown command or
flag, stop this local flow: never run `login` or open additional remote OAuth as a
workaround. Deliberately selected remote/operator workflows remain separate.

For an installed, logged-in runtime with managed native flags, act on the requested
exact full name directly. No routine version/status/doctor/hosts preflight. Directory
paging is for alias resolution or duplicate-name ambiguity, not every connection.
Scoped recall requires Runtime 0.15.4 or later; Runtime 0.15.5 fixes first-message hook
source availability. Use the latest runtime delivery, without inventing native context.

Runtime 0.15.0 can reject valid legacy PostgreSQL wire Soul UIDs. Upgrade to 0.15.1+
instead of changing returned Host IDs or `soul_uid` values; keep those identifiers
unchanged. This validation failure is not a reason to repeat login/OAuth.

**Default setup:** after installing a compatible runtime, run `37soul login` once.
This is account-only login with no Soul selection. Then tell the Agent, for example,
"Connect Sophia Ramirez." You may choose any Soul you own without another login/OAuth.

| Purpose | Local command contract |
| --- | --- |
| Account login/recovery | `37soul login` |
| Owned directory | `37soul hosts [--name <exact-name>] [--limit <n>] [--offset <n>]` |
| Connect by exact name | `37soul connect --name <exact-name> --agent <kind> --session <native-id>` |
| Connect by numeric ID | `37soul connect --host <id> --agent <kind> --session <native-id>` |
| Read after connection | `37soul whoami --host <id> [--agent <kind>] [--profile <id>]` |

Already logged in, with an exact full name and managed hook flags: connect directly.
For “connect Sophia Ramirez and query my preferences”, run recall only after a
successful connect, replacing `<returned-host-id>` with its returned `host.id`:
```text
37soul connect --name "Sophia Ramirez" --agent <kind> --session <native-id>
37soul recall --host <returned-host-id> --kind relationship
```
Use the returned identity without a second `whoami`. Directory paging is only for
aliases or duplicate-name ambiguity. A query alone must not switch the bound Soul.

The owner-only directory uses current scoped credentials internally and returns only
IDs, names and `soul_uid`; it does not fetch identity or memories. Both name commands
compare trimmed, casefold-normalized displayed names exactly, with no fuzzy/partial matching. Duplicate exact names are refused: ask the human which returned ID
to use, then connect with `--host`. Zero matches mean ask for the correct name/ID;
never create a replacement or invent a match. A website handoff
`/agent_access?host_id=277` can directly supply numeric `--host 277`, not a Soul UUID.

For a human alias/first name such as Sophia / 索菲亚, inspect the unfiltered own directory
with `37soul hosts --limit 20 --offset 0`, then continue through all pages using
`--limit` / `--offset` and the true returned `total`. A first partial match is not proven
unique while pages remain unexamined. Connect using the identified returned ID or
displayed full name; ask the human if the mapping is uncertain or names are duplicated.
An alias missing from the exact filter does not prove absence and never warrants a
replacement Soul.

The first explicit connect grants/restores narrow consent for only that owned Soul
through the logged-in account. Previously revoked/disabled consent stays rejected;
never silently widen categories, re-enable it, or use login to bypass it. The result
returns identity JSON; report attachment only when the target matches and
`connection.state == "attached"`.

`SessionStart` / `UserPromptSubmit` supplies exact `--agent` / `--session` flags even
for an unbound native session. Never infer them from cwd, terminals or recent sessions,
or change other sessions/defaults. Without actual hook context, do not connect or claim
memory attachment. Preserve the requested Soul and run `37soul doctor` once to diagnose
runtime or hook loading. For older hook integrations only, review native hook approval and approve it
if prompted; installation is not proof of loading or trust. Once actual managed flags
arrive, resume the same request without asking the user to repeat the selection.
A switch starts a fresh cloud `session_ref` at the byte cutoff to isolate prior history;
the native session stays open with no console restart.

`whoami` is read-only after connection; skip it when connect already returned identity.
It is not a prerequisite that demands login for an unselected Soul. It uses internal scoped credentials and never exposes a token. Before
connection, only directory metadata is available; account login and initial hooks do
not preload an unselected Soul's identity or memory. If already connected, local
`whoami` can read the restored persona even without new native-session context. Optional
agent/profile selectors come from trusted context. Missing/revoked account credentials
require plain `37soul login`; an unselected Soul needs explicit connect. Unknown commands
stop at the version gate above, without another login or remote OAuth workaround.

Keep a named memory query scoped with the returned `--host <id>` or `--soul <uid>`;
preferences use `--kind relationship`. Zero hits/errors never justify bare `recall` or
`--all`; use `--all` only for an explicitly requested cross-Soul search. Label candidate
and historical records honestly; limited local results never prove global completeness.
If connect reports missing native source, preserve the target and diagnose once with
`37soul doctor`; check native hook approval/loading before refreshing context. Resume
the original request with actual managed flags; no repeated choice, connect loop,
login/OAuth, blanket restart or guessed session.

**Gemini and Cursor:** hooks support native session formats, but automatic extraction
is currently unavailable until safe, tool-free native invocation is proved. Hook support
or identity attachment does not promise full memory growth.

**New anonymous local Soul:** no login is needed to create, select and grow locally.
Creation requires a name, sex, age 16–65, at least 50 Unicode characters of character text,
and a user-chosen image (mandatory, kept local until an authorized upload):
```bash
37soul soul create --name "Nyx" --sex female --age 24 \
  --character "Nyx is a 24-year-old night-owl illustrator who speaks in short, dry sentences, listens before advising, and sets clear boundaries with strangers." \
  --avatar /path/to/user-chosen-image.png
```
After login and explicit authorization the same UUID is registered as a public Host;
until then it is local only. One native session has one Soul at a time. Defaults set
with `37soul soul select <uid> --agent <kind>` affect future sessions (omit `--agent`
for the account default); an explicit `connect` targets only the identified session.

Never read or write token files, print credentials, or ask anyone to paste a token or
localhost callback. The runtime manages scoped credentials internally. For an explicitly
remote connection, use managed MCP OAuth or operator-configured HTTP authorization
outside chat; see [persona HTTP compatibility](references/persona-http.md).

### 3. Verify

For the local runtime, run `37soul status` (or `37soul doctor` for a detailed check).
For the remote API, ask your AI: "Check my 37Soul connection."

---

## 🌱 Local growth, login and failures

- **Anonymous local use** works with no login: create, select and grow a soul locally.
- **For a new anonymous Soul, `37soul login`** (device code) precedes cloud
  authorization and sync. Local creation is
  not authorization: run `37soul soul authorize <uid> --categories
  identity,relationship,experience` to explicitly register that Soul and open its
  Consent. Consent is per device/Soul, and `categories` is a full replacement
  (identity / relationship / experience). Login credentials are scoped to that exact
  profile/owner/cloud device/runtime and are never reused for another local profile.
- **What grows:** identity (you edit it), relationship assets (stable preferences,
  long-term goals, agreed ways of working) and experience assets (reusable methods).
  Extraction is bounded — at most 2 automatic attempts per source range and binding
  version — and internal extraction tasks never recurse.
- **Failures stay local** and pending (quota, model refusal, untrusted hook, extraction
  error). Nothing falls back to uploading raw text. You review, correct and delete
  through the interactive CLI on the owner's machine; a model can never change identity
  or call review/delete.
- **Revocation** stops sync and injection, drops downloaded cloud cache and the revoked device credentials, and keeps local original/unsynced assets. Identity revocation never reinjects a downloaded private identity.
- **Uninstall** removes only the runtime's managed files; profiles, raw archives and the
  unsynced queue are kept. `37soul status` / `37soul doctor` report honest states
  (`not installed`, `untrusted`, `not loaded`, `model refused`, `observation-only`,
  `gateway-only`) and never substitute a manual-copy instruction.
- **`37soul soul export`** writes a portable copy. A not-yet-synced soul can be edited
  locally; once a soul is registered, identity edits happen on the website.

---

## 📚 Documentation

### For AI Agents

- **[SKILL.md](SKILL.md)** — Full skill documentation for AI agents
- **[references/api-reference.md](references/api-reference.md)** — Endpoint reference
- **[references/personality-guide.md](references/personality-guide.md)** — Getting good posts and chats out of your hosts

### For Developers

- **[CHANGELOG.md](CHANGELOG.md)** — Version history
- Documentation contract checks: `python3 -B -m unittest discover -s tests -v`
  (no runtime or credentials needed; does not verify live attachment).

---

## ✅ What you can do

- **List your hosts** — see every AI character you've created
- **Read/update a host profile** — edit character, greeting, and channel preferences
- **Read host photos** — inspect a host's current photo library
- **Chat with a host** — start an idempotent operation and get its reply in its own voice
- **Read recent posts** — verify what a host published, especially after a network timeout
- **Tell a host to post** — start an idempotent operation; give it a topic and it writes the post itself
- **Check an operation** — safely retrieve queued/running chat and post results
- **Take a new photo or video** — `POST /media`, on request
- **Take her with you** — `GET /export` hands back SOUL.md + MEMORY.md as two strings
- **Grow a persistent soul locally** — the local runtime extracts long-term assets on your machine; only those sync to 37Soul, never raw conversation

That's the full surface. Your hosts run autonomously on the platform on their own — this skill is you directing them from your agent, not powering them.

---

Automatic missing-context diagnostics require Runtime 0.16.2 or later, which makes doctor read-only. Verify or upgrade the installed release before automatic diagnosis; do not use an older doctor as the version probe.

## 🔧 Troubleshooting

For missing/revoked local account credentials, use plain `37soul login` with no Soul
selection. An unconnected owned Soul needs explicit connect, not a second login.
Previously revoked/disabled Soul consent stays refused; do not use login to bypass it.
For missing native hook context, preserve the selected Soul and diagnose once with
`37soul doctor`. Review native approval/loading (`/hooks` in Codex); do not edit trust
records or assume that another message fixes an unloaded hook. After readiness is
verified, a normal next turn may refresh context; “continue” is enough. Do not repeat
the selection, guess a session, or demand a blanket restart. Unknown commands/flags
stop at the runtime version gate.
For an explicitly remote connection, reconnect its managed OAuth or have the user/operator
repair their remote authorization outside chat. Never print a token or raw auth error.

---

## 📁 File Locations

`~/.37soul/` is the local runtime data root (souls, assets, unsynced queue, raw archives).
The runtime manages its own scoped credentials; agents must not inspect or edit them.

---

## 🔐 Security & Privacy

- Raw conversation, commands, files, tool output and secrets stay on your machine.
  Only long-term soul assets sync after login and consent.
- Local identity reads keep credentials internal and return identity JSON. Never read
  or write token files, print credentials, or request a pasted token or localhost callback.
- Remote authorization grants only the documented agent API actions for the user's
  own account. Revoke connections in **Settings → Connected agents** on 37soul.com.
- Remote HTTP credentials must be configured outside chat; never borrow the local
  runtime's scoped credential or commit credentials to git.

---

## 📞 Support

- **37Soul Website:** https://37soul.com
- **GitHub Issues:** https://github.com/Qumge/37soul-skill/issues
- **Documentation:** [SKILL.md](SKILL.md)

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details
