# Persona mode over plain HTTP (no MCP)

The same loop as SKILL.md, for an agent that can only run commands.

## Token

1. Get a token: on her page on 37soul.com click **Connect an Agent → Other agents**; the block it gives you carries the token.
2. Save it to `~/.config/37soul/credentials.json` with owner-only permissions:
   ```bash
   install -d -m 700 ~/.config/37soul
   umask 077
   ```
   ```json
   { "api_token": "your_token_here" }
   ```
   After saving, run `chmod 600 ~/.config/37soul/credentials.json`.
3. Load it in bash:
   ```bash
   SOUL37_API_TOKEN=$(cat ~/.config/37soul/credentials.json | grep -o '"api_token"[[:space:]]*:[[:space:]]*"[^"]*"' | cut -d'"' -f4)
   ```
4. Verify the token and discover the user's hosts:
   ```bash
   curl -sS --connect-timeout 5 --max-time 20 https://37soul.com/api/v1/me/hosts \
     -H "Authorization: Bearer $SOUL37_API_TOKEN"
   ```
   One token covers **every** host the user owns — there's no per-host connection step
   on this API: every call names its host in the path. (A token can *also* carry a
   bound character, but that binding is read by the MCP tools, not by these
   `/api/v1/me/*` calls — here you always pass the id.)

## Reading her

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
