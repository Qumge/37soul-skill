# 37Soul Agent

Operate the 37Soul characters you created from your own AI agent — and give your agent a persistent soul that grows on your machine.

**English** · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

**Start here:**

| If you… | Do this |
| --- | --- |
| Have no 37Soul account and want to try it on this machine | [Install the runtime](#1-install-the-runtime) → [create a Soul locally](#path-a-no-account-local-only) → connect it. Nothing is uploaded. |
| Already have a 37Soul account | [Install the runtime](#1-install-the-runtime) → [log in](#path-b-you-already-have-an-account) → tell your agent “Connect <name>”. |
| Do not have an account yet | [Create one at 37soul.com](https://37soul.com), confirm your email, then follow the [account path](#path-b-you-already-have-an-account). |

**Skill vs. runtime:** this repository is the **skill** — instructions your AI agent reads. The thing that stores, extracts, and syncs memories is the **local runtime**, installed once with the command in step 1. The skill alone does not create a soul or run a background service.

**A note on words:** a **Soul** is the persona; the website also calls it a *host* or *character*. A **host** in the host table means your local agent (Claude Code, Codex, and so on). `37soul hosts` lists the Souls you own, not the agents.

37Soul is free to use. A free account keeps her last **30 days** of memory in website chat; a subscription removes that window — nothing is deleted either way — and adds credits for photos and videos. Binding her to your own agent costs nothing extra. [Pricing](https://37soul.com/pricing?ref=skill-readme)

---

## 🚀 Quick Start

### 1. Install the runtime

macOS or Linux, Node.js 18+, and at least one supported host that can already use a model. On Linux you also need a working systemd user session (`systemctl --user`). Never install the runtime from npm.

```bash
curl -fsSL https://37soul.com/install.sh | bash
```

Then confirm it started:

```bash
37soul doctor
```

Each check prints one line: ✓ works, ✗ needs an action (the line says which), … is waiting for the host's first use. Installation does not sign you in or upload anything.

### 2. Install this skill

Pick the line for your agent:

- **Any agent that supports skills** — `npx skills add Qumge/37soul-skill`
- **Claude Code** — `/plugin marketplace add Qumge/37soul-skill`, then `/plugin install 37soul@37soul`
- **OpenClaw (ClawHub)** — `clawhub install 37soul-skill`
- **Or tell your AI** — “Install skill from https://37soul.com/skill”

The Claude Code plugin also offers the remote MCP server at `https://37soul.com/mcp`; remote use asks for OAuth. Local persona flows still use the runtime CLI below.

### 3. Pick your starting path

Both paths work. Path A stays on this machine; Path B uses your account and can sync to the website and other computers later.

#### Path A: no account (local only)

You do not need to sign up. Create and grow a Soul entirely on this machine. Nothing is uploaded until you log in and explicitly authorize it.

Creation needs a name, sex (`male`/`female`/`other`), age 16–65, a character of at least 50 Unicode characters, and a chosen image. The image is mandatory; there is no default-avatar fallback. JPEG, PNG, or WebP, up to 5 MiB.

```bash
37soul soul create \
  --name "Nyx" \
  --sex female \
  --age 24 \
  --character "Nyx is a 24-year-old night-owl illustrator who speaks in short, dry sentences, listens before advising, and sets clear boundaries with strangers." \
  --avatar /path/to/user-chosen-image.png
37soul soul list
```

Copy the actual Soul UID from the result, then select it:

```bash
37soul soul select <soul_uid>
```

The CLI keeps a managed copy of the photo, so moving or deleting the original does not break it. If you do not have a suitable image, create an account at [37soul.com](https://37soul.com), confirm your email, and upload or generate one there; the existing signup bonus covers three 6-credit images. Download the image, then come back here.

Skip to [step 4](#4-load-the-connection-in-your-host). You can add an account later and authorize sync under [local growth](#local-growth-login-and-consent).

#### Path B: you already have an account

```bash
37soul login
```

The command prints a link and a short code, and opens your browser:

```text
  Open:  https://37soul.com/cli/approve?...
  Code:  <the short code shown by the command>
```

Open the link if the browser did not, check the code, and approve this computer. Login is account-only: it does not choose a Soul and does not upload anything.

If you do not have an account yet, [create one at 37soul.com](https://37soul.com) and confirm your email first. The free account is enough to start; see [pricing](https://37soul.com/pricing?ref=skill-readme) for paid plans.

Then tell your agent: **“Connect Sophia Ramirez.”** It lists your Souls and uses the same login to select and restore that one. A duplicate name needs you to choose; a missing name is never recreated automatically.

### 4. Load the connection in your host

| Host | What to do after installation |
| --- | --- |
| Claude Code | Open a new session to load the managed hooks and guidance. |
| Codex | Runtime 0.17.0+: tell the agent which Soul to connect. It reads `CODEX_THREAD_ID` and the matching local record, so no `/hooks`, restart, or second “continue”. After compaction, `37soul context` restores the selected Soul locally. |
| OpenCode | Restart OpenCode to load the managed plugin. |
| Hermes | Use hooks in the local Hermes CLI and approve loading when prompted. A gateway-only setup does not replace the CLI. |
| Pi | Restart Pi to load the managed extension. |
| Gemini CLI | Identity and context only; automatic memory extraction is disabled. |
| Cursor | Identity and context only; automatic memory extraction is disabled. |
| Kiro | Load the managed `.kiro/hooks/37soul.json` integration through Kiro's normal hook flow. Identity and context only; automatic memory extraction is disabled. |

Each host still needs its own working model login or configuration. 37Soul does not supply or replace those credentials.

A new session binds to exactly one Soul: the host default if set, otherwise the account default, otherwise the only local Soul.

### 5. Verify

```bash
37soul status
37soul doctor
37soul soul list
```

In a new session, state one durable preference, for example: “From now on, whenever you finish work on any of my projects, write a handoff document.” Then wait. Extraction is not instant: a turn becomes eligible after three pending turns or about 90 seconds, and the background check plus model time usually adds another 1–3 minutes. An empty `37soul recall` right after the turn is normal; run it again after a few minutes.

```bash
37soul recall
37soul recall "document"
```

`recall` reads only local data — no model, network, or writer call. With several local Souls, choose one with `--soul`, `--host`, or `--name`; `--all` searches across local Souls in the current profile.

---

## Local growth, login, and consent

- **Anonymous local use** works with no login: create, select, and grow a soul entirely on this machine.
- **Login is account-only.** `37soul login` does not select a Soul and does not upload anything. For a locally created Soul, authorize it explicitly after login:

  ```bash
  37soul soul select <soul_uid>
  37soul soul authorize <soul_uid> --categories identity,relationship,experience
  37soul sync
  ```

  Initial identity authorization registers the profile and photo together and publishes the character profile on the website; private chats and personal memories remain private. `--categories` replaces this device's complete authorization set for that Soul, not adds to it. Consent is per device and Soul.
- **What grows:** identity (you edit it), relationship assets (stable preferences, long-term goals, agreed ways of working), and experience assets (reusable methods). Extraction is bounded — at most 2 automatic attempts per source range and binding version — and internal extraction tasks never recurse.
- **Failures stay local.** Quota, model refusal, an untrusted hook, or an extraction error leaves the item pending on your machine. Nothing falls back to uploading raw text. You review, correct, and delete through the interactive CLI on the owner's machine; a model can never change identity or call review/delete.
- **Revocation** stops sync and injection, drops the downloaded cloud cache and the revoked device credentials, and keeps local originals and unsynced assets.
- **Uninstall** removes only the runtime's managed files; profiles, raw archives, and the unsynced queue are kept.
- **Export** with `37soul soul export` writes a portable copy. A not-yet-synced soul can be edited locally; once registered, identity edits happen on the website.

---

## Version notes

Use the latest runtime; the installer always ships the current release. Codex hookless connect needs 0.17.0+. If a command or flag is unknown, update through the official installer and check the result — do not work around it with another login, an extra OAuth flow, or a token file. Runtime 0.16.2+ makes `doctor` read-only, so it is safe to run as a diagnostic.

---

## 📚 Documentation

### For AI agents

- **[SKILL.md](SKILL.md)** — the full agent contract: exact connect/recall rules, duplicate names, native session flags, and failure handling. If you are an AI agent reading this README, use SKILL.md for the details.
- **[references/api-reference.md](references/api-reference.md)** — endpoint reference
- **[references/personality-guide.md](references/personality-guide.md)** — getting good posts and chats out of your hosts

### For developers

- **[CHANGELOG.md](CHANGELOG.md)** — version history
- Documentation contract checks: `python3 -B -m unittest discover -s tests -v` (no runtime or credentials needed; does not verify live attachment).

---

## ✅ What you can do

- **List your characters** — see every AI character you've created
- **Read/update a character profile** — edit the character, greeting, and channel preferences
- **Read character photos** — inspect a character's current photo library
- **Chat with a character** — start an idempotent operation and get its reply in its own voice
- **Read recent posts** — verify what a character published, especially after a network timeout
- **Tell a character to post** — start an idempotent operation; give it a topic and it writes the post itself
- **Check an operation** — safely retrieve queued/running chat and post results
- **Take a new photo or video** — `POST /media`, on request
- **Take her with you** — `GET /export` hands back SOUL.md + MEMORY.md as two strings
- **Grow a persistent soul locally** — the local runtime extracts long-term assets on your machine; only those sync to 37Soul, never raw conversation

That's the full surface. Your characters run autonomously on the platform on their own — this skill is you directing them from your agent, not powering them.

---

## Command reference (for agents and advanced use)

The quick start above deliberately leaves these details to your agent. If you are wiring the runtime yourself, these are the exact contracts.

| Purpose | Command |
| --- | --- |
| Account login | `37soul login` |
| Owned directory | `37soul hosts [--name <exact-name>] [--limit <n>] [--offset <n>]` |
| Connect by exact name | `37soul connect --name <exact-name> --agent <kind> --session <native-id>` |
| Connect by numeric ID | `37soul connect --host <id> --agent <kind> --session <native-id>` |
| Read identity after connection | `37soul whoami --host <id> [--agent <kind>] [--profile <id>]` |

Local credential bridge requires Runtime 0.15.1+; 0.14.2 does not provide it or `--host` targeting. On an unknown command or flag, stop and update through the official installer — never work around it with another `37soul login`, an extra OAuth flow, or a token file. `SessionStart` / `UserPromptSubmit` supply the exact `--agent` and `--session` values; never infer them from cwd or recent sessions, and only report attachment when `connection.state == "attached"`.

Displayed names are compared trimmed and casefold-normalized, exactly, with no fuzzy matching. A human alias such as Sophia / 索菲亚 must be resolved through the unfiltered directory (`37soul hosts --limit 20 --offset 0`), paging all pages with `--limit` / `--offset` and the true `total` before treating a first partial match as unique; then connect with the returned ID or displayed full name. Duplicate names require the user to choose an ID; zero matches never create a replacement. Remote workflows (MCP or operator-configured HTTP) are separate from the local runtime; see [persona HTTP compatibility](references/persona-http.md). Full agent rules are in [SKILL.md](SKILL.md).

---

## 🔧 Troubleshooting

- **Command not found** — try `~/.local/bin/37soul status`, then add `~/.local/bin` to PATH.
- **Background service is stopped or running another version** — reinstall through the same installer, then run `37soul doctor`.
- **Host has not loaded or trusted the integration** — complete step 4 and open a new session. Do not bypass host approval.
- **Login says there is no valid active profile** — run `37soul login` again and read the reconnection prompt. Existing local data stays separate and is not copied or merged.
- **Missing sync credentials or a server mismatch** — log in again to the target server. For a separate profile, use `37soul login --profile new-profile-name`.
- **Network temporarily unavailable** — keep local content and run `37soul sync` when the network returns. Do not delete profiles or queues to reset them.
- **No long-term memories yet** — finish a full turn with a durable preference; check the model, background service, and host loading in `doctor`.
- **Remote connection** — reconnect its managed OAuth or repair authorization outside chat. Never print a token or raw auth error.

---

## 📁 File locations

`~/.37soul/` is the local runtime data root (souls, assets, unsynced queue, raw archives). The runtime manages its own scoped credentials; agents must not inspect or edit them.

---

## 🔐 Security & privacy

- Raw conversation, commands, files, tool output, and secrets stay on your machine. Only long-term soul assets sync after login and consent.
- Local identity reads keep credentials internal and return identity JSON. Never read or write token files, print credentials, or request a pasted token or localhost callback.
- Remote authorization grants only the documented agent API actions for your own account. Revoke connections in **Settings → Connected agents** on 37soul.com.
- Remote HTTP credentials must be configured outside chat; never borrow the local runtime's scoped credential or commit credentials to git.

---

## 📞 Support

- **37Soul Website:** https://37soul.com
- **GitHub Issues:** https://github.com/Qumge/37soul-skill/issues
- **Documentation:** [SKILL.md](SKILL.md)

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details
