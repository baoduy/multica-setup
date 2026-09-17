# Node.js / TypeScript Standards (baoduy TS repos)

Derived from actual config of `github.com/baoduy/drunk-pulumi-azure-components` and
sibling TS libraries (`-azure-providers`, `-cloudflare-components`, `-intune-components`). This skill
covers **language and tooling layer**: package/build/test/publish and idiomatic TS. Domain rules
for Pulumi builders (naming, RBAC, Builder pattern, `*Info`/`*Args`) live in
`pulumi-azure-iac-standards` — do not duplicate them here. Every rule carries a stable `rule-id`.

## Core philosophy (do not fight it)

- **pnpm is the package manager** — not npm, not yarn. Scripts run through `pnpm run <x>`.
- **Strict TypeScript, zero `any`** — `strict: true`, `noImplicitAny: true` are on; compiler is first test.
- **ESM, Node16 resolution** — `module: Node16`, `moduleResolution: node16`, `target: ESNext`. Author real ES modules.
- **Prettier is the only formatter** — no ESLint config in these repos; style is Prettier + `tsc --strict`. Do not add ESLint or bikeshed style.

## Toolchain & package

- `TS-PKG-001` **Wrong package manager.** Use `pnpm` (`pnpm install`, `pnpm run build`, `pnpm run test`). Do not introduce `package-lock.json` or `yarn.lock`; lockfile is `pnpm-lock.yaml`.
- `TS-PKG-002` **Reinvented build script.** Pipeline is `pnpm run build` = `update-tsconfig` → `tsc` → `copy-pkg` (`.tasks/*.ts` scripts, run via `tsx`). New build steps extend a `.tasks/` script; don't inline bespoke shell in `scripts`.
- `TS-PKG-003` **Ad-hoc TS execution.** Run one-off/build TS with `tsx ./path.ts` (already a devDependency) — not `ts-node`, not a hand-rolled `tsc && node` dance.
- `TS-PKG-004` **Unpinned or drifting deps.** Bulk upgrades go through `pnpm run update` (`npm-check-updates -u && pnpm install`), reviewed as one change — not scattered manual bumps. `typescript` and `@types/node` are pinned exact (e.g. `typescript: 6.0.3`); keep them exact.

## TypeScript config & type safety

- `TS-CFG-001` **Loosening `strict`.** `strict`, `noImplicitAny`, `noFallthroughCasesInSwitch`, `forceConsistentCasingInFileNames` are on in `tsconfig.json`. Do not disable them or add `// @ts-ignore` to dodge them — fix the type.
- `TS-CFG-002` **`any` instead of a real type.** Compose narrow types; reach for `unknown` + narrowing guard at boundaries before ever `any`. A widening cast (`as any`, `as unknown as T`) needs a one-line justification comment or it's a violation.
- `TS-CFG-003` **`rootDir`/`outDir` violated.** Source lives under `src/`; build emits to `bin/`. Don't emit into `src`, don't import from `bin`, don't add source outside `src`.
- `TS-CFG-004` **Internal API leaked into `.d.ts`.** `stripInternal` is on — mark genuinely-internal exports with `/** @internal */` so they stay out of published types; don't export helpers you don't intend downstream stacks to depend on.
- `TS-CFG-005` **Editing generated `files[]` by hand incorrectly.** `tsconfig.json`'s explicit `files[]` list is produced by `pnpm run update-tsconfig` (`.tasks/update-tsconfig.ts`). Add a source file, then regenerate — don't hand-append and risk drift.

## Formatting

- `TS-FMT-001` **Non-house Prettier style.** Config is fixed: `semi: true`, `singleQuote: true`, `trailingComma: 'all'`, `printWidth: 120`, `tabWidth: 2`. Run Prettier; `lint-staged` enforces it on commit. Do not override per-file or reformat to personal taste.

## Errors & async

- `TS-ERR-001` **Swallowed error / bare `catch {}`.** Catch to add context or recover, then rethrow or fail — never silently discard. In `catch (e)`, `e` is `unknown`: narrow it (`e instanceof Error`) before reading `.message`.
- `TS-ERR-002` **Floating promise.** Every `Promise` is awaited or explicitly handled; no fire-and-forget async in sync path. `async` functions return `Promise<T>` with type stated, not inferred `any`.
- `TS-ERR-003` **Exceptions for control flow.** Throw for exceptional/boundary failures only; use typed results or narrowing for expected branches. Don't `throw` to break out of a loop.

## Testing (jest + ts-jest)

- `TS-TEST-001` **Wrong test runner.** These repos run **jest** via **ts-jest** (`jest.config.js`, `preset: ts-jest`, `testEnvironment: node`), compiled with `tsconfig.test.json`. Do NOT add mocha/vitest. *(Note: `pulumi-azure-iac-standards` PULUMI-TEST-001 still says "mocha" — that is stale; jest is real runner. Follow this.)*
- `TS-TEST-002` **Test file misnamed/misplaced.** `testMatch` is `**/*.test.ts`; name tests `<unit>.test.ts` beside or under the source. A `.ts` not picked up by that glob isn't a test.
- `TS-TEST-003` **Untested new logic.** New builder/helper/type-composition logic ships with a `*.test.ts`. Pulumi resource behaviour is mocked with `pulumi.runtime.setMocks` (see `pulumi-azure-iac-standards`); pure TS logic needs no Pulumi mocks — just unit-test it.

## Library publish shape

- `TS-PUB-001` **Broken package output.** These are npm libraries: `main: index.js`, `types: index.d.ts`, emitted to `bin/` by `copy-pkg` (`.tasks/npm-package.ts`). A change must keep `pnpm run build` clean and not leak `src`, tests, or `.tasks` into published package.
- `TS-PUB-002` **Breaking public API without a major bump.** Renamed/removed exports, changed exported signatures, or dropped `.d.ts` symbols are breaking for downstream stacks — flag for SemVer (major). Additive-only changes are minor.
- `TS-PUB-003` **Undocumented public surface.** Public exports are the API; docs are generated (`pnpm run docs`, `.tasks/generate-docs.ts`). Keep JSDoc on exported symbols so generated docs stay meaningful.

