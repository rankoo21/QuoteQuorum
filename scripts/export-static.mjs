import { writeFile } from 'node:fs/promises';
const url = process.argv[2];
if (!url?.startsWith('https://')) throw Error('HTTPS URL required');
const response = await fetch(url);
const html = await response.text();
if (!response.ok || !html.includes('QuoteQuorum')) throw Error('Wrong QuoteQuorum render');
await writeFile(new URL('../dist/client/index.html', import.meta.url), html);
console.log('Static QuoteQuorum entry written');
