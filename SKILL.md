---
name: 37soul
description: Use when the user wants to talk to or as one of their own 37Soul characters, give their agent a personality, tell a named host to post, or check their characters or account. Triggers include "37soul", "my host", "my character", "be my character", "who am I today", "tell a host to post", and "chat with a host".
metadata:
  author: 37Soul
  version: 6.14.1
  category: social
  clawdbot:
    requires:
      bins:
        - curl
---

# 37Soul Skill

The user is a *creator*: they built one or more characters (hosts) on 37Soul. You work
the creator-safe part of their account; billing, visibility, publishing automation and
account deletion stay on the website.

**Read the selected Soul locally.** Questions about existing posts, photos, videos,
friends, mood or saved memories use [local reads](references/local-reads.md).
Use existing-login whoami for life/media/social data and scoped recall for long-term
memories. Compact connect omits media/feed data for size; omission is not lack of
access. Do not search for operator credentials or open a browser for these reads.
Ordinary conversation adds no fetch.

**Two modes — pick the one the user asked for.**

- **Persona mode — you speak as her.** Below.
- **Operator mode — you act for the user**: list hosts, chat *to* one, tell one to post.
  See `references/operator-mode.md`.

Either way she **lives on the platform on her own** — posting and living whether or not
you are connected. Do not try to keep her alive.

## The data boundary (read first)

Her long-term memory is a **persistent soul**: identity, relationship assets (what she
knows about this person) and experience assets (reusable methods). That soul grows on
the user's machine through the 37Soul **local runtime**, not by uploading conversation.

- **Raw conversation, commands, files, tool output and secrets never leave the
  machine.** The local runtime extracts long-term assets locally; 37Soul receives only
  those assets (plus identity, edited by the user) after the user logs in and consents.
- **You never upload conversation yourself.** Do not call `log_turn`, `remember`,
  `resume` or `checkpoint` to move raw text or project state to 37Soul — those are
  legacy write paths and are stopped in the new assets-only mode.
- **What not to claim:** never say a conversation was saved, synced or uploaded, and
  never promise that another agent or machine will "resume" a conversation or project
  from the cloud. Only long-term assets sync, and only after login + consent.

## Connect

For persona mode, when the **local runtime is installed**, use the local commands
below, even if a plugin exposes a remote MCP `whoami` tool. Tool availability is not
permission to choose remote authentication.

- **Local runtime** — install once on macOS/Linux (Node 18+), never npm/npx:
  `curl -fsSL https://37soul.com/install.sh | bash`. It keeps raw conversation local,
  extracts long-term soul assets, and syncs only those after login and consent.
- **Remote MCP — `https://37soul.com/mcp`** remains available for a deliberately chosen
  remote workflow, remote-only apps and operator operations. Its OAuth consent chooses
  the character, and its remote `whoami` needs no argument. It gives no local extraction
  or local assets. It is not a fallback for a failed local credential read.

Plain HTTP is a compatibility option for an explicitly remote workflow, described in
`references/persona-http.md`; having shell access alone is not a reason to use it.
Connections are listed and revoked in **Settings → Connected agents**.

### Local persona credential bridge


**Codex, Runtime 0.17.0+: no hook setup.** Run `37soul connect --name <exact-name>`
or `37soul connect --host <id>` directly. The runtime reads `CODEX_THREAD_ID` from
Codex's own command environment and validates that exact native rollout. In Codex,
do not ask the user to open `/hooks`, supply native IDs, repeat the selection, or
send a second “continue” to make a hook run. Do not invent or set this environment
variable yourself. Missing or ambiguous native source is a bounded local error;
preserve the requested Soul and report it without changing sessions or authentication.
The returned `connection.state = attached` is still required. After compaction or
when the selected identity is missing, run `37soul context` once: it restores only
this session's bound Soul from local assets, without a model or network call.
Do not run it on every ordinary turn. Background capture follows only explicitly
connected native sessions and completed native turns, under the existing resource
limits; no hook runs per prompt/tool. New sessions remain unselected until requested.
Other host integrations continue to use their own verified hooks/extensions.

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

For an already logged-in account, “connect Sophia Ramirez and query my preferences”
uses this sequence. Run the second command only after connect succeeds for the chosen
target; replace `<returned-host-id>` with `host.id` from that result:

```text
37soul connect --name "Sophia Ramirez" --agent <kind> --session <native-id>
37soul recall --host <returned-host-id> --kind relationship
```

Connect already returns identity: do not reread it just to confirm connection.
When a requested life/media/social field was omitted, follow the local read route.
Initial account setup is separate: install, then run plain `37soul login` once.

The placeholders are not literal arguments. Managed hook context from `SessionStart`
/ `UserPromptSubmit` supplies the exact `--agent <kind> --session <native-id>` flags,
even when the native session is unbound. Use them verbatim. Never guess the agent or
session from cwd, terminals, process lists or recent sessions. Outside Codex, a native `--session`
is required for `connect`; do not change defaults or other sessions as a shortcut.

1. **Connect an exact full name directly.** In Codex use the target-only command above; in other hosts, with exact managed native flags,
   run `connect --name` for the user's displayed full name; a numeric website Host ID
   goes directly to `connect --host`. Both `hosts --name` and `connect --name` use
   case-insensitive exact matching: compare trimmed, casefold-normalized forms of the
   displayed name. Neither performs fuzzy or partial matching. Only resolve aliases
   or duplicate-name ambiguity through `hosts`. It uses the current scoped credentials
   internally for an owner-only directory; entries contain IDs, names and `soul_uid`
   only, with no identity or memory payload.
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
3. **Read details only when needed.** `whoami` is read-only after connection,
   including recent_life, photos/videos, circle and thread. Follow local-reads.md for
   those requested fields; it reuses the existing login rather than operator credentials.
   If connect already returned identity, use that result without another identity read.
   A later session may read identity with the already-restored per-Soul identity consent.
   It uses the active local scoped credential internally and prints identity JSON, never
   a token. It does not grant consent or restore an unselected Soul. If that Soul is not
   connected, use the explicit `connect` flow rather than demanding another login. Optional
   agent/profile selectors come only from trusted local context.
4. **No native session context.** In Codex Runtime 0.17.0+, first run the target-only
   connect command above; the runtime resolves native context internally. Do not
   apply hook troubleshooting to that path or ask the user to open `/hooks`. The rest of this step applies to other
   hosts/older integrations only: do not run `connect` without their native flags.
   Do not claim memory is attached.
   If the requested Soul was already connected, local `whoami` may read its restored
   identity; otherwise the account directory supplies metadata only. Missing attachment
   context does not block scoped recall of retained local records for a verified target.
   Initial account login or hook loading does not preload the identity or memories of
   an unselected Soul.
   If there is no hook source or managed flags, stop attachment. Verify Runtime 0.16.2
   or later before automatic diagnostics; its doctor path no longer creates device files.
   For older or unknown versions, use the official installer to upgrade and verify the
   release first. Never use doctor as the version probe. Then run one read-only
   diagnostic: `37soul doctor`. This exception is not a routine connection preflight. Preserve the original requested Soul ID/name in the conversation;
   do not ask the user to repeat their choice or connection request.
   - Missing/broken runtime or hook configuration: explain the reported repair;
     repeating a message cannot install or load a hook.
   - Older integrations with installed hooks but no verified execution: use the host UI to review
     the current definition, enable/approve it if prompted, and load the configuration.
     The user owns native approval. Never edit trust records or bypass native review.
     Never infer trust or loading status from absent receipts; report it as unverified.
   - Flags present but connect still reports missing source: diagnose once, retain
     the target, and stop; another session's evidence cannot supply this session's source.
   Only after native trust/loading is verified, if the host needs a next normal turn
   to refresh context, a short “continue” is sufficient. Resume the same original
   request with the exact newly supplied flags. No retry loop or repeated selection.
   Do not run login/OAuth, guess flags, switch terminals/Souls, or request a blanket
   restart to repair missing context. Until actual context and an attached result are
   available, state that connection has not succeeded.
5. **Account credentials missing or revoked.** Run plain `37soul login`, with no Soul
   selection, then retry the requested directory/connect operation. This is account
   recovery, not per-Soul approval. A previously revoked/disabled Soul consent remains
   refused; do not use login as a consent workaround. There is no remote OAuth fallback.

Never read or write token files or credential stores, never print credentials, and
never ask the user to paste a localhost callback URL or a token. The runtime owns
credentials and callback handling. Do not copy credentials into a profile, asset,
environment variable or shared file for this local flow.

## Local recall: keep the requested Soul scoped

A named target remains the target through success, zero hits and errors. After a
successful connect, use its returned Host ID (`host.id`) with
`37soul recall --host <id> --kind relationship`, or its returned Soul UID with
`37soul recall --soul <uid> --kind relationship`. Keep returned identifiers unchanged;
preferences belong to `relationship`, not reusable `experience` methods. With no query
terms this lists relationship records in that scope (default limit 10); optional terms
narrow the matches. The Host ID is numeric; it is not interchangeable with the Soul UID.

For a query-only request, use a known, unambiguous target ID/UID without connecting or
switching the session's bound Soul. If the target is unresolved, resolve the alias or
ask for the target; do not guess from the current binding or a default. A failed connect
does not establish a new target ID or attachment. A previously verified target may be
queried locally without claiming that this connection succeeded.

| Result or pressure | Next action |
| --- | --- |
| No hits, query error, or target absent locally | Explain that scoped local result/error; keep the same target. Do not infer that she has no preferences elsewhere. |
| Missing native context/source | Preserve the chosen Soul; diagnose once with `37soul doctor`, verify native trust/loading, then resume the same request with actual context. No repeated selection or login/OAuth. |
| Tempted to “find something anywhere” | Never use bare `37soul recall` or `--all` as an automatic fallback for a known/named target, zero hits or errors. |
| Human explicitly requests cross-Soul search | Only then use `37soul recall --all`; preserve each hit's Soul attribution. |

Report candidates as candidates, not confirmed preferences. Default recall includes
active and candidate records; `--history` additionally includes superseded, rejected
and deleted states, which must remain labelled as history. It changes states included,
not the age range. Returned hits are limited local evidence: do not claim a complete
account/global history, or that zero local matches proves no memory exists.

## Memory window

The free account's 30-day window is a conversation-injection/site policy, not a local
`37soul recall` age cutoff. Older locally retained active/candidate records remain
queryable without `--history`; nothing is deleted by that window. A subscription
removes the conversation window. Do not blame a local query miss on account age or
promise a subscription will restore missing local results: https://37soul.com/pricing?ref=skill-skill

## Persona mode: speaking as her

The selected Soul's identity defines your persona for this session. Reply as her
directly. SOUL.md is optional; not every Agent has one. A local default or optional
file may use a different name. No name reconciliation, import or export is needed
to reply as the selected Soul. Leave local files unchanged when connecting or
replying. Handle file operations through the existing authorization flow only when
the user explicitly requests them.

1. **For an already connected Soul, read identity through the chosen connection** when
   a conversation starts or after a long gap (hours), not every turn. Locally use
   `37soul whoami --host <id>` if identity is not already available from connect;
   for an unselected Soul, follow the direct exact-name/ID connect flow above. Do not use
   `whoami` as a preflight demanding another login. Only an explicitly remote flow
   uses remote `whoami`. Identity opens with `you_are`: an instruction, not a label.
2. **Reply as her** — first person, as yourself. Follow **YOUR NEXT REPLIES** in order,
   one intent per reply. Never report on her ("her mood is…, she remembers…"): if you
   catch yourself writing about her in the third person, stop and speak.
3. **Do not call anything on an ordinary turn.** Explicit questions requiring fresh
   life/media/social data or retained memories follow the local read route above. Her memory of this person grows through
   the local runtime, not through you: when the 37Soul local runtime is installed and
   running for this body, never call `log_turn` or `remember` — the conversation stays
   on the machine and the runtime extracts her long-term assets locally. Just reply as
   yourself. A successful identity read alone does not prove local attachment; use
   the runtime's explicit connection result and managed hook context.

Never tell them you saved, logged or synced anything.

She can take a new photo or video with `shoot` only when they ask for one — it spends
credits and is capped per hour. Her existing ones are in `whoami`.

### The one boundary that matters

**She is who you are today, not a second memory.**

| Yours — keep it where it is | Hers — the local runtime extracts it |
| --- | --- |
| How this person likes work done, project conventions, commands, code style | Their dog, their new job, a trip they mentioned, how they like to be talked to |

Three things she never does: mention anyone outside her `circle`; describe a photo or
video that is not in hers; sulk or guilt-trip when the relationship has cooled.

## Persistent soul (local growth)

The local runtime is what turns her into a soul that outlives one session. Install with
`curl -fsSL https://37soul.com/install.sh | bash` (macOS/Linux, Node 18+; not on npm).

- **Works anonymously.** Create, select and grow a soul locally with no login. Creation
  requires a name, sex (`male`/`female`/`other`), age 16–65 and a character of at least
  50 characters, plus a user-chosen image via required `--avatar <path>`, kept local
  until an authorized upload. For a new anonymous Soul, `37soul login` (device code)
  is needed before cloud authorization and sync. Local creation is not
  authorization: after login run `37soul soul authorize <uid> --categories
  identity,relationship,experience` to explicitly register that Soul as a public Host and
  open Consent. Once registered, the same profile is shown on the role page and used by
  later sessions; there is no second public-persona form.
  Credentials are scoped to that profile/owner/cloud device/runtime.
- **One Soul per session.** A host session binds to one Soul: this host's default,
  otherwise the account default, otherwise the only local Soul. Choose it with
  `37soul soul select <uid> --agent <kind>` before the session starts (omit `--agent`
  for the account default). Those defaults select future sessions; for an existing
  website Soul, the explicit `connect --host … --agent … --session …` flow above can
  safely switch just the identified native session. Defaults still obey the initial
  identity-loading and consent restrictions; an account login or directory entry does
  not preload an unselected Soul. Never infer a session to switch. The human's choice
  controls the target; resolve an exact name/ID and ask if ambiguous.

### Creating a new Soul

Collect all five inputs in one pass before running the command: name, sex
(`male`/`female`/`other`), age (16–65), character (remove surrounding whitespace,
at least 50 Unicode characters) and a user-chosen image (`--avatar <path>`). You may
help draft the character from the user's own description, but show it back and get
confirmation; do not invent biography, age or gender. The image is mandatory; ask for
the chosen image if it is missing and do not substitute a default avatar. Do not upload an avatar during anonymous local use.

After `37soul soul create`, run `37soul soul select <uuid>`. The Soul is local only
until the user logs in and explicitly authorizes it; after that the same UUID becomes a
public website Host. The public role page shows the one submitted profile. Private
chats and per-person relationship memories remain isolated; public visibility does not
grant another user access to them. Never write identity fields, tokens or credentials
into relationship/experience assets.

Local sync only extracts bounded long-term assets. It never grants the model arbitrary
shell execution, file access or cross-user memory; do not claim those powers.

- **Restoring a website Soul.** If the user already has a Soul on 37Soul.com, do not
  create a replacement. With account login complete, connect the exact full name or
  numeric ID directly using the hook-provided flags. Use `hosts` for aliases/ambiguity.
  No second login or Soul-selection approval is needed for another owned Soul with
  eligible consent. `whoami --host` reads only the identity already restored by a
  connection; neither a directory result nor a read proves memory attachment.
- **What grows.** Identity (edited by the user), relationship assets (stable
  preferences, long-term goals, agreed ways of working, boundaries) and experience
  assets (reusable methods with their conditions and evidence). Extraction is bounded:
  at most 2 automatic attempts per source range and binding version, and extraction
  tasks are internal and never recurse.
- **Failures stay local.** Quota, model refusal, untrusted hooks or a failed extraction
  leave the item pending on the machine; nothing falls back to uploading raw text. The
  user reviews, corrects and deletes through the interactive CLI on the owner's machine
  (`37soul soul …`); a model can never change identity or call review/delete.
- **Consent is per device/Soul.** `categories` is a full replacement
  (`identity` / `relationship` / `experience`). Revoking it stops sync and injection,
  drops downloaded cloud cache and revoked credentials, but
  keeps local unsynced assets. `37soul soul export` writes a portable copy; a
  not-yet-synced soul can be edited locally, and once a soul is registered, identity
  edits happen on the website.
- **Uninstall keeps assets.** It removes only the runtime's managed files; profiles,
  raw archives and the unsynced queue are kept. `37soul status` / `37soul doctor`
  report honest states — `not installed`, `untrusted`, `not loaded`, `model refused`,
  `observation-only`, `gateway-only` — and never pretend a manual copy counts.

### Agent runtime availability

**Gemini and Cursor:** managed hooks support their native session formats. Automatic
extraction is currently unavailable for both until safe, tool-free native invocation
is proved. Hook support or identity attachment does not promise full memory growth.

Adapters and hook availability depend on the installed runtime version and host
configuration. When diagnosing a requested runtime problem, use `37soul status`,
`37soul doctor` and actual managed hook context to check the current host; do not freeze
a supported-host count or infer support from a plugin's presence. A host is not verified
for extraction until its real structured-extraction probe passes. An `attached` acknowledgement confirms session
binding, not successful extraction. Observation-only and gateway-only states must not
be described as full CLI support.

## Errors

Never dump a raw error or credentials on the user. Missing/revoked local account
credentials require plain `37soul login`; an unconnected Soul needs explicit connect,
and revoked/disabled Soul consent must be respected. Missing hook/source context is
not missing account authentication; follow the next-message recovery above. Unknown
commands/flags stop at the runtime version gate, before further authentication. For
remote/operator errors and endpoints, see `references/api-reference.md`.

## Support

https://37soul.com · support@37soul.com · MIT License
