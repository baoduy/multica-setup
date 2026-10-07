#!/usr/bin/env python3
"""Setup health counts for the drunk bundle: the six lenses of the weekly retro.

Run from the setup repo root:  python3 scripts/setup-health.py [--digest digest.json]
(`--selftest` checks the parsers.)
Prints one JSON object. Read-only: it reads the bundle, `multica skill list` and
the GitHub releases API, and changes nothing. A live read that fails yields null.
"""
import glob, json, os, re, subprocess, sys

B = "export/drunk-workspace"
BUDGET = 24000      # always-loaded bytes per agent, about 6K tokens
LONG_LINE = 600     # characters
BIG_SKILL = 10240   # SKILL.md bytes before it should route to references/


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def live(cmd):
    try:
        return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
    except Exception:
        return None


def frontmatter_description(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    lines = m.group(1).split("\n")
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            v = line[len("description:"):].strip()
            if v in (">", ">-", "|", "|-"):
                block = []
                for nxt in lines[i + 1:]:
                    if nxt and not nxt.startswith(" "):
                        break
                    block.append(nxt.strip())
                v = " ".join(b for b in block if b)
            return v.strip().strip('"').strip("'")
    return None


def shingles(text, n=10):
    w = re.findall(r"[a-z0-9_`'-]+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def norm(s):
    return " ".join((s or "").split())


def main():
    digest = sys.argv[sys.argv.index("--digest") + 1] if "--digest" in sys.argv else None
    wc = read(f"{B}/workspace/workspace.context.md")
    skill_dirs = sorted(d for d in os.listdir(f"{B}/skills") if d != "archify")
    skill_md = {d: f"{B}/skills/{d}/SKILL.md" for d in skill_dirs}
    runtime = sorted(
        glob.glob(f"{B}/agents/*.md") + glob.glob(f"{B}/squads/*.md")
        + glob.glob(f"{B}/autopilots/*.description.md")
        + [p for d in skill_dirs for p in glob.glob(f"{B}/skills/{d}/**/*.md", recursive=True)]
    )
    runtime = [p for p in runtime if not p.endswith(".description.md") or "/autopilots/" in p]
    texts = {p: read(p) for p in runtime}
    all_runtime = {f"{B}/workspace/workspace.context.md": wc, **texts}

    # 1 Duplication
    # 10-word runs shared with the Workspace Context: near-verbatim restatements.
    wc_sh = shingles(wc)
    overlap = sorted(((len(wc_sh & shingles(t)), p) for p, t in texts.items()), reverse=True)
    overlap = [(n, p) for n, p in overlap if n]
    same = {}
    for p, t in texts.items():
        if "/agents/" in p:
            same.setdefault(t, []).append(os.path.basename(p))
    ref_files = {os.path.basename(p) for p in glob.glob(f"{B}/skills/*/references/*.md")}
    dangling = sorted({f"{p}: references/{m}" for p, t in texts.items()
                       for m in re.findall(r"references/([A-Za-z0-9._-]+\.md)", t) if m not in ref_files})

    # 2 Wording
    agents = {}
    for j in glob.glob(f"{B}/agents/*.json"):
        a = json.loads(read(j))
        own = read(f"{B}/{a['instructions_file']}") if a.get("instructions_file") else ""
        agents[a["name"]] = len(wc.encode()) + len(own.encode())
    for j in glob.glob(f"{B}/squads/*.json"):
        s = json.loads(read(j))
        if s.get("instructions_file") and s.get("leader_name") in agents:
            agents[s["leader_name"]] += len(read(f"{B}/{s['instructions_file']}").encode())
    long_lines = sorted(((len(l), f"{p}:{i}") for p, t in all_runtime.items()
                         for i, l in enumerate(t.split("\n"), 1) if len(l) > LONG_LINE), reverse=True)
    always = [f"{B}/workspace/workspace.context.md"] + [p for p in texts if "/agents/" in p or "/squads/" in p]
    keys = sorted({(p, k) for p in always for k in re.findall(r"\bDRK-\d+\b", all_runtime[p])})

    # 3 Structure
    big_no_refs = [d for d in skill_dirs if os.path.getsize(skill_md[d]) > BIG_SKILL
                   and not os.path.isdir(f"{B}/skills/{d}/references")]
    no_frontmatter = [d for d in skill_dirs if not read(skill_md[d]).startswith("---\n")]

    # 4 Practices
    agent_md = {json.loads(read(j))["name"]: read(f"{B}/" + json.loads(read(j))["instructions_file"])
                for j in glob.glob(f"{B}/agents/*.json") if json.loads(read(j)).get("instructions_file")}
    no_goal = sorted(n for n, t in agent_md.items() if "**Goal.**" not in t[:800])
    no_never = sorted(n for n, t in agent_md.items() if not re.search(r"(?im)^(#+\s*never|\*\*never)", t))
    ls = live(["multica", "skill", "list", "--output", "json"])
    ls = ls.get("skills", ls) if isinstance(ls, dict) else ls
    desc_no_when = desc_drift = None
    if ls is not None:
        livedesc = {s["name"]: s.get("description") or "" for s in ls}
        when = re.compile(r"\b(use (when|for|before|whenever|this)|must use|load (before|when))\b", re.I)
        desc_no_when = sorted(n for n in skill_dirs if n in livedesc and not when.search(livedesc[n]))
        desc_drift = sorted(n for n in skill_dirs if n in livedesc
                            and frontmatter_description(read(skill_md[n])) is not None
                            and norm(frontmatter_description(read(skill_md[n]))) != norm(livedesc[n]))

    # 5 Built-ins
    behind = None
    last = json.loads(read("release-reviews/last-run.json"))
    rel = live(["gh", "api", "repos/multica-ai/multica/releases?per_page=100"])
    if rel is not None:
        behind = sorted(r["tag_name"] for r in rel if r.get("published_at", "") > last["published_at"])

    # 6 Performance (from the retro's gate digest)
    perf = None
    if digest:
        d = json.loads(read(digest))
        perf = {g: {"reviews": v["count"], "first_pass_pct": round(100 * v["first_pass"] / v["count"]) if v["count"] else None,
                    "mean_rounds": v["mean_rounds"], "escalated": v["escalated"]}
                for g, v in d.items() if isinstance(v, dict) and "count" in v}

    over = {n: b for n, b in sorted(agents.items(), key=lambda x: -x[1]) if b > BUDGET}
    print(json.dumps({
        "1_duplication": {"workspace_context_overlap": sum(n for n, _ in overlap),
                          "top_overlap": [f"{p} ({n})" for n, p in overlap[:3]],
                          "identical_agent_instructions": [g for g in same.values() if len(g) > 1],
                          "dangling_references": dangling},
        "2_wording": {"agents_over_budget": len(over), "over_budget_bytes": over,
                      "always_loaded_bytes_max": max(agents.values()),
                      "long_lines": len(long_lines), "longest": [w for _, w in long_lines[:3]],
                      "incident_keys_always_loaded": len(keys)},
        "3_structure": {"big_skills_without_references": big_no_refs, "skills_without_frontmatter": len(no_frontmatter)},
        "4_practices": {"agents_without_goal": no_goal, "agents_without_never_list": len(no_never),
                        "descriptions_without_when": None if desc_no_when is None else len(desc_no_when),
                        "descriptions_drifted_from_live": desc_drift},
        "5_builtins": {"last_reviewed_tag": last["last_reviewed_tag"], "releases_since": behind},
        "6_performance": perf,
    }, indent=1))


def selftest():
    assert frontmatter_description('---\nname: x\ndescription: "Do X. Use when Y."\n---\nbody') == "Do X. Use when Y."
    assert frontmatter_description("---\nname: x\ndescription: >-\n  Do X.\n  Use when Y.\ncategory: c\n---\n") == "Do X. Use when Y."
    assert frontmatter_description("# no frontmatter") is None
    assert len(shingles("one two three four five six seven eight nine ten eleven")) == 2
    print("ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
