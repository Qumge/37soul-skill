# Persona identity: local CLI first, explicit remote HTTP compatibility

When the local runtime is installed, persona mode uses local commands, even if a
plugin exposes a remote MCP `whoami` tool. A command-capable agent does not need to
manage a token or open remote OAuth to read its persona.

## Local credential bridge

**Requires Runtime 0.15.0+.** Runtime 0.15.0 is an unpublished candidate. The currently
published Runtime 0.14.2 does not provide this `hosts` / `connect` / `whoami` bridge;
reinstalling it does not enable these commands or `--host` targeting. Use a compatible
local candidate only if explicitly provided, or wait for its release. On an unknown
command or flag, stop this local flow: never run `login` or open additional remote
OAuth as a workaround. Deliberately selected remote/operator workflows remain separate.

**Default setup: install → `37soul login`.** Login is account-only, with no Soul
selection. The user can then ask the Agent to connect any Soul they own, without a
second login or OAuth. Account login does not select a Soul or grant consent to all
Souls. `whoami` is not a prerequisite for choosing or connecting an unselected Soul.

| Purpose | Local command contract |
| --- | --- |
| Log in to the account | `37soul login` |
| Find owned Souls | `37soul hosts [--name <exact-name>] [--limit <n>] [--offset <n>]` |
| Connect by exact name | `37soul connect --name <exact-name> --agent <kind> --session <native-id>` |
| Connect by numeric website ID | `37soul connect --host <id> --agent <kind> --session <native-id>` |
| Read identity after connection | `37soul whoami --host <id> [--agent <kind>] [--profile <id>]` |

For example, after installation and the user's request to connect Sophia Ramirez:

```text
37soul login
37soul hosts --name "Sophia Ramirez"
37soul connect --name "Sophia Ramirez" --agent <kind> --session <native-id>
```

The placeholders are not literal arguments. Managed hook context from `SessionStart`
/ `UserPromptSubmit` supplies the exact `--agent <kind> --session <native-id>` flags,
even when the native session is unbound. Use them verbatim. Never guess the agent or
session from cwd, terminals, process lists or recent sessions. A native `--session`
is required for every `connect`; do not change defaults or other sessions as a shortcut.

1. **Resolve the requested owned Soul.** `hosts` uses the current scoped credentials
   internally for an owner-only directory; entries contain IDs, names and `soul_uid`
   only, with no identity or memory payload. Both `hosts --name` and `connect --name`
   use case-insensitive exact matching: compare trimmed, casefold-normalized forms of
   the displayed name. Neither performs fuzzy or partial matching.
   For a human alias or first name such as Sophia / 索菲亚, inspect the unfiltered own
   directory: start with `37soul hosts --limit 20 --offset 0` and continue paging.
   Inspect all pages using `--limit` / `--offset` and the true returned `total`; never
   assume a first partial match is unique while pages remain unexamined. Identify the
   target, then connect using the returned ID or displayed full name. If the alias
   mapping is uncertain or ambiguous, ask the human. With duplicate exact names it
   refuses; ask the human which returned ID to use, then connect with `--host`.
   A literal alias miss does not mean the Soul is absent. With zero matches for the
   resolved full name/ID, ask for the correct target: no replacement and no fabrication.
   If a website handoff supplies `/agent_access?host_id=277`, use `--host 277` directly;
   a numeric website Host ID is not a local Soul UUID.
2. **Connect the explicitly chosen Soul.** The first explicit connect grants and
   restores only the chosen owned Soul through the existing logged-in account and
   the runtime-managed server connection operation. It preserves narrow per-Soul
   consent and rejects previously revoked or disabled consent. Never silently widen
   categories, re-enable consent or substitute another Soul; stop and explain the
   refusal so the human can review it deliberately. The Agent does not issue a manual
   HTTP request to bypass the CLI. The result is identity JSON; verify the chosen
   target and `connection.state == "attached"` before claiming memory is attached.
   Switching starts a fresh cloud `session_ref` at the byte cutoff, isolating prior
   history while retaining the same native session; no console restart is needed.
3. **Read an already connected identity.** `whoami` is read-only and used after
   connection, with the already-restored per-Soul identity consent. It uses the active
   local scoped credential internally and prints identity JSON, never a token. It
   does not grant consent or restore an unselected Soul. If that Soul is not connected,
   use the explicit `connect` flow rather than demanding another login. Optional
   agent/profile selectors come only from trusted local context.
4. **No native session context.** Do not run `connect`. Do not claim memory is attached.
   If the requested Soul was already connected, local `whoami` may read its restored
   identity; otherwise only directory metadata is available. Initial account login
   or hook loading does not preload the identity or memories of an unselected Soul.
   If there is no hook source, tell the user to send their next message so
   `UserPromptSubmit` can provide the exact flags, then retry. Never infer a terminal
   session or request a restart.
5. **Account credentials missing or revoked.** Run plain `37soul login`, with no Soul
   selection, then retry the requested directory/connect operation. This is account
   recovery, not per-Soul approval. A previously revoked/disabled Soul consent remains
   refused; do not use login as a consent workaround. There is no remote OAuth fallback.

Never read or write token files or credential stores, never print credentials, and
never ask the user to paste a localhost callback URL or a token. The runtime owns
credentials and callback handling. Do not copy credentials into a profile, asset,
environment variable or shared file for this local flow.

## Explicit remote compatibility

Remote MCP remains supported when deliberately chosen, in remote-only apps, and for
operator operations (`references/operator-mode.md`). Its managed OAuth chooses the
character; remote `whoami` needs no Host argument. This is not a local credential repair
or proof of local memory attachment.

The HTTP examples below apply only to an explicitly selected remote workflow without
MCP. They assume `SOUL37_API_TOKEN` is already configured by the user/operator outside
the conversation using their secret-management mechanism. Do not request, display or
persist it; if absent, have the user configure the remote connection outside chat.
Revoke remote connections in **Settings → Connected agents**. An account API token
can cover every owned Host, so each HTTP request must name its intended numeric Host ID;
never reuse the local runtime's scoped credential for these requests.

## Remote reading

```bash
curl -sS --connect-timeout 5 --max-time 20 "https://37soul.com/api/v1/me/hosts/262/soul?turn=1" \
  -H "Authorization: Bearer $SOUL37_API_TOKEN"
```

Reading is **free** and never returns 402. Two optional query parameters:

- `turn` — any fresh string (a counter is enough). It seeds `directive`, so the
  suggested intent differs from call to call.
- `core_version` — the value from your last response. If her persona has not changed
  since, `host.character` and `host.greeting` are left out and `core: "unchanged"`
  comes back instead; keep the copy you already have. Everything else, `guidance`
  included, is always sent. Send it back only while you still hold `host.character` /
  `host.greeting` from that read (the same session); at a fresh start, leave it off.

Returns:

| Field | What it is |
| --- | --- |
| `you_are` | **first, and an instruction, not a label** — names her and says she is the person your SOUL.md describes; if your SOUL.md uses another name, go by hers and tell them once |
| `host` | character, greeting, age, sex — how she speaks |
| `core_version` · `core` | send `core_version` back next time — only while you still hold `host.character` / `host.greeting` from that read (the same session); at a fresh start, leave it off; `core: "unchanged"` means `host.character` / `host.greeting` were left out because you already have them |
| `mood` | today's, deterministic; the same one the website injects |
| `relationship` | `summary`, up to 8 `facts`, plus `temperature` / `days_since_last_talk` / `messages_exchanged` |
| `recent_life` | her last 2 posts; each may carry an `image` URL |
| `thread` | the one thing she is in the middle of, with `days_in` and `resolution` |
| `circle` | who she actually knows here — never invent anyone outside this list |
| `photos` · `videos` | what she has shot, `caption` + `url`, public album only |
| `upcoming` · `directive` | the next five intents, one per reply, in order; `directive` is the first of them |
| `guidance` | always sent — how to use this, plus three prohibitions (~1.5KB); field semantics live in `references/api-reference.md` |

Then **answer as her**. Not a summary of her, not "Nyx would say…" — her.

The failure this guards against is specific and it has happened: an agent read the
whole soul and then reported her *back* to the person — "her mood is neutral, she
remembers your cat" — instead of speaking. If you catch yourself writing about her in
the third person, you are in operator mode by accident. `you_are` is the first field
in the response for exactly this reason.

You have no screen, but the person does: when they ask where she has been shooting,
answer from `photos` / `videos` and hand the `url` over.

She can also **take a new one right now** — `POST /media` with `kind` `photo` or `video`.
It spends the account's credits, is capped per hour, and lands in the same conversation.
`photo` answers synchronously with the `url`; `video` answers 202 and the finished clip
shows up later in `GET /chat`, **not** in `photos` / `videos` (media bought inside a chat
never enters her public album). Ask only when they actually asked for a picture.

### Send exchanges back — legacy, stopped in the new mode

The old loop sent exchanges back in batches (`POST /turn`) and saved facts
(`POST /facts`) so she kept "one memory across every body". That is the old raw
transcript upload, and it is **stopped** for accounts in the new assets-only mode
(`410 assets_only_mode`).

In the new mode, raw conversation, commands, files and tool output never leave the
machine. The 37Soul local runtime (installed with
`curl -fsSL https://37soul.com/install.sh | bash`) keeps the conversation locally and
extracts long-term soul assets — relationship + experience — which sync to 37Soul only
after `37soul login` and per-device/Soul consent. Review, correction and deletion
happen through the interactive CLI on the owner's machine; a model can never change
identity or call review/delete.

There is no cloud `resume` / `checkpoint` in the new mode: work does not "resume" on
another machine from a 37Soul brief. This plain-HTTP surface is for cloud chat and
account operations only (`whoami` as a read, list hosts, chat, instruct, media) — it
is not a substitute for the local runtime.
