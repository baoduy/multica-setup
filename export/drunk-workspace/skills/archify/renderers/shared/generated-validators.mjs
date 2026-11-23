// Multica bundle patch: upstream's generated validators exceed the live 1 MB file
// limit, so their source ships gzipped and base64-encoded in generated-validators.gz.b64.
// Regenerate both with: gzip -9nc <upstream generated-validators.mjs> | base64 > generated-validators.gz.b64
import fs from 'node:fs';
import { gunzipSync } from 'node:zlib';

const b64 = fs.readFileSync(new URL('./generated-validators.gz.b64', import.meta.url), 'utf8');
const source = gunzipSync(Buffer.from(b64, 'base64')).toString('utf8')
  .replace("from './portable-path.mjs'", `from ${JSON.stringify(new URL('./portable-path.mjs', import.meta.url).href)}`);
const m = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));

export const { workflow, sequence, dataflow, lifecycle, architecture, erd, tree, timeline, waterfall, explainer, storyChoreography, prPack } = m;
const classDiagram = m.class;
export { classDiagram as class };
