import { readFile, writeFile } from 'node:fs/promises';
import { createAccount, createClient } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionStatus } from 'genlayer-js/types';

const d = JSON.parse(await readFile(new URL('../artifacts/deployment.json', import.meta.url), 'utf8'));
const key = process.env.GENLAYER_PRIVATE_KEY;
if (!key) throw Error('GENLAYER_PRIVATE_KEY is required');
const c = createClient({ chain: studionet, account: createAccount(key.startsWith('0x') ? key : '0x' + key) });
const id = 'LIVE-' + Date.now();
const sources = JSON.stringify([
  { url: 'https://jsonplaceholder.typicode.com/todos/1', path: ['id'] },
  { url: 'https://dummyjson.com/products/1', path: ['id'] },
  { url: 'https://api.github.com/repos/github/gitignore', path: ['forks_count'] },
]);
const registerHash = await c.writeContract({ address: d.address, functionName: 'register_feed', args: [id, sources, 500], value: 0n });
await c.waitForTransactionReceipt({ hash: registerHash, status: TransactionStatus.FINALIZED, retries: 180, interval: 2500 });
const sampleHash = await c.writeContract({ address: d.address, functionName: 'sample_feed', args: [id], value: 0n });
await c.waitForTransactionReceipt({ hash: sampleHash, status: TransactionStatus.FINALIZED, retries: 180, interval: 2500 });
const record = JSON.parse(String(await c.readContract({ address: d.address, functionName: 'get_feed', args: [c.account.address, id] })));
if (record.id !== id || record.quotes?.length !== 3 || !record.digests?.every(x => x.length === 64)) throw Error('readback failed');
await writeFile(new URL('../artifacts/live-verification.json', import.meta.url), JSON.stringify({ address: d.address, owner: c.account.address, register: registerHash, sample: sampleHash, record }, null, 2) + '\n');
console.log('LIVE QUOTE SNAPSHOT PASSED: ' + record.status);
