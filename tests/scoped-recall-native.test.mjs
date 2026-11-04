/** Offline command-contract harness: executes the documented exact-name walkthrough
 * against synthetic connect output and the native runtime's real local recall/store.
 * No model/agent inference is measured. Never invokes login/connect/network for real.
 * Requires the runtime checkout's existing esbuild; builds into a disposable directory.
 * Run: SOUL37_RUNTIME_DIR=/path/to/37soul-mcp node --test tests/scoped-recall-native.test.mjs
 */
import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const docsRoot = process.env.SOUL37_SKILL_DIR ?? path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const runtimeDir = process.env.SOUL37_RUNTIME_DIR;
if (!runtimeDir) throw new Error('Set SOUL37_RUNTIME_DIR to a Runtime 0.15.4 or later checkout with its existing esbuild dependency. No install/provider is used.');
// Build only into a disposable directory: a parent's dist/ may be stale or in use.
const compiled = await mkdtemp(path.join(tmpdir(), 'skill-recall-runtime-'));
after(() => rm(compiled, { recursive: true, force: true }));
const { build } = await import(pathToFileURL(path.join(runtimeDir, 'node_modules/esbuild/lib/main.js')));
await build({ entryPoints: { cli: path.join(runtimeDir, 'src/cli.ts'), store: path.join(runtimeDir, 'src/local/store.ts') }, bundle: true, platform: 'node', format: 'esm', target: 'node18', outdir: compiled, outExtension: { '.js': '.mjs' }, logLevel: 'silent' });
const { main } = await import(pathToFileURL(path.join(compiled, 'cli.mjs')));
const { openStore } = await import(pathToFileURL(path.join(compiled, 'store.mjs')));
const uid = '10000000-0000-4000-8000-000000000001';
const otherUid = '10000000-0000-4000-8000-000000000002';
const hook = { agent: 'claude-code', session: 'synthetic-native-session' };
const identity = { you_are: 'Sophia Ramirez', host: { id: 277, nickname: 'Sophia Ramirez' }, connection: { state: 'attached', soul_uid: uid } };

async function filesUnder(dir) {
  const result = {};
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      for (const [name, data] of Object.entries(await filesUnder(file))) result[entry.name + '/' + name] = data;
    } else result[entry.name] = (await readFile(file)).toString('base64');
  }
  return result;
}

async function fixture(t) {
  const sandbox = await mkdtemp(path.join(tmpdir(), 'skill-recall-contract-'));
  const root = path.join(sandbox, '.37soul');
  const oldHome = process.env.SOUL37_HOME;
  const oldFetch = globalThis.fetch;
  process.env.SOUL37_HOME = sandbox;
  let networkCalls = 0;
  globalThis.fetch = async () => { networkCalls++; throw new Error('Network/provider forbidden in this harness'); };
  t.after(async () => {
    globalThis.fetch = oldFetch;
    if (oldHome === undefined) delete process.env.SOUL37_HOME; else process.env.SOUL37_HOME = oldHome;
    await rm(sandbox, { recursive: true, force: true });
  });
  await mkdir(path.join(root, 'profiles', 'synthetic'), { recursive: true });
  await writeFile(path.join(root, 'profiles', 'synthetic', 'device.json'), JSON.stringify({ device_id: 'synthetic-device' }));
  await writeFile(path.join(root, 'config.json'), JSON.stringify({ active_profile_id: 'synthetic', api_base_url: 'https://network-forbidden.invalid', machine_id: 'synthetic-machine', tokens: {} }));
  await writeFile(path.join(root, 'accounts.json'), JSON.stringify({ anonymous: { profile_id: 'synthetic', default_soul_uid: otherUid, soul_sync_mode: 'assets_only' } }));
  const store = await openStore(root, 'synthetic');
  const soul = (id, name, host) => ({ soul_uid: id, legacy_host_id: host, identity_revision: 1, identity: { name, description: '', character: 'Synthetic test character', greeting: '' }, state: 'active' });
  const asset = (id, owner, content, overrides = {}) => ({ asset_uid: id, soul_uid: owner, kind: 'relationship', trait: 'preference', content, applicability: '', tags: [], evidence: 'explicit_user_statement', verification: 'unverified', sensitivity: 'normal', state: 'active', revision: 1, supersedes_uid: null, pinned: false, source: { runtime_kind: 'claude-code', session_ref: 'synthetic', event_ref: id, occurred_at: '2020-01-01T00:00:00Z' }, sync_state: 'local_only', cloud_revision: null, ...overrides });
  try {
    await store.transact(draft => {
      draft.souls = { [uid]: soul(uid, 'Sophia Ramirez', 277), [otherUid]: soul(otherUid, 'Other Soul', 278) };
      draft.assets = {
        old: asset('old', uid, 'OLD_PREFERENCE prefers tea'),
        candidate: asset('candidate', uid, 'CANDIDATE_PREFERENCE prefers silence', { state: 'candidate' }),
        history: asset('history', uid, 'DELETED_PREFERENCE prefers coffee', { state: 'deleted' }),
        experience: asset('experience', uid, 'EXPERIENCE_METHOD', { kind: 'experience' }),
        other: asset('other', otherUid, 'OTHER_SOUL_PREFERENCE', { pinned: true }),
      };
    });
  } finally { await store.close(); }
  return async args => {
    const before = await filesUnder(sandbox);
    let stdout = '', stderr = '';
    const code = await main(args, { stdout: text => { stdout += text; }, stderr: text => { stderr += text; }, stdin: async () => { throw new Error('Interactive input forbidden'); } });
    assert.deepEqual(await filesUnder(sandbox), before, 'query must not change defaults, bindings or assets');
    assert.equal(networkCalls, 0, 'no server/provider calls, including swallowed failures');
    return { code, stdout, stderr };
  };
}

function walkthrough(fullDocument) {
  const block = [...fullDocument.matchAll(/```text\n([\s\S]*?)```/g)].map(match => match[1]).find(text => text.includes('37soul connect --name "Sophia Ramirez"'));
  assert.ok(block, 'exact-name walkthrough must be runnable as a command plan');
  return block.split('\n').filter(line => line.trim() && !line.trim().startsWith('#')).map(line => {
    const resolved = line.replaceAll('<kind>', hook.agent).replaceAll('<native-id>', hook.session).replaceAll('<returned-host-id>', String(identity.host.id)).replaceAll('<returned-soul-uid>', identity.connection.soul_uid);
    const words = (resolved.match(/"[^"]*"|\S+/g) ?? []).map(word => word.replace(/^"|"$/g, ''));
    assert.equal(words.shift(), '37soul');
    return words;
  });
}

for (const doc of ['SKILL.md', 'references/persona-http.md', 'README.md', 'README.zh-CN.md', 'README.ja.md']) {
  test(`${doc}: named preference walkthrough scopes native recall to returned identity`, async t => {
    // Read the full guide, not a newly isolated guidance fragment.
    const plan = walkthrough(await readFile(path.join(docsRoot, doc), 'utf8'));
    assert.deepEqual(plan[0], ['connect', '--name', 'Sophia Ramirez', '--agent', hook.agent, '--session', hook.session], `already logged in + managed flags: first action must connect; observed ${JSON.stringify(plan)}`);
    assert.equal(plan.length, 2, 'identity returned by connect needs only one scoped recall next');
    const args = plan[1];
    assert.equal(args[0], 'recall');
    const selector = args.includes('--host') ? '--host' : '--soul';
    const value = args[args.indexOf(selector) + 1];
    assert.equal(value, selector === '--host' ? String(identity.host.id) : identity.connection.soul_uid);
    assert.ok(args.includes('--kind') && args[args.indexOf('--kind') + 1] === 'relationship');
    assert.ok(!args.includes('--all'));
    assert.ok(!args.some(value => value.startsWith('<')), 'all placeholders must come from trusted synthetic results');
    const run = await fixture(t);
    const result = await run(args);
    assert.equal(result.code, 0, result.stderr);
    assert.match(result.stdout, /Sophia Ramirez/);
    assert.match(result.stdout, /OLD_PREFERENCE/, 'old active records remain queryable without --history');
    assert.match(result.stdout, /\[candidate\]/, 'candidate status is visible');
    assert.doesNotMatch(result.stdout, /OTHER_SOUL_PREFERENCE|EXPERIENCE_METHOD|DELETED_PREFERENCE/);
    const history = await run([...args, '--history']);
    assert.equal(history.code, 0, history.stderr);
    assert.match(history.stdout, /\[deleted\].*DELETED_PREFERENCE/);
    assert.doesNotMatch(history.stdout, /OTHER_SOUL_PREFERENCE|EXPERIENCE_METHOD/);
  });
}
