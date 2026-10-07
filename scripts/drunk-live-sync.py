#!/usr/bin/env python3
"""Sync export/drunk-workspace from origin/main to the live drunk workspace.

Run from the root of a clone of baoduy/multica-setup, on the host whose
`multica` CLI is logged in to the drunk workspace (Policy 03 statement 11).

  drunk-live-sync.py            push what changed between tag live/drunk and origin/main
  drunk-live-sync.py --check    compare every supported bundle file with live, push nothing
  drunk-live-sync.py --accept   like the default, but move the tag even when changes were
                                reported unsupported (only after the owner applied them by hand)

Prints one JSON report. Exit 0 = synced or up to date, 2 = blocked (tag not moved),
1 = error. The tag moves only when every pushed resource reads back equal to its file.
"""
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys

BUNDLE = "export/drunk-workspace"
TAG = "live/drunk"
WORKSPACE_ID = "4539126d-0687-4993-8852-3554b7c5fb50"
LOCK = os.path.expanduser("~/.multica-sync/drunk.lock")
DESC_MAX = 255
# Bundle files that never reach the live workspace.
NOT_LIVE_PREFIXES = ("docs/",)
NOT_LIVE_FILES = ("README.md", "manifest.json")


def run(args, stdin=None):
    p = subprocess.run(args, input=stdin, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("%s: %s" % (" ".join(args[:4]), (p.stderr or p.stdout).strip()[-400:]))
    return p.stdout


def mjson(*args):
    d = json.loads(run(["multica", *args, "--output", "json"]))
    if isinstance(d, dict) and len(d) <= 2 and any(isinstance(v, list) for v in d.values()):
        d = next(v for v in d.values() if isinstance(v, list))  # {"autopilots": [...], "total": n}
    return d


def git(*args):
    return run(["git", *args]).strip()


def show(rev, path):
    return run(["git", "show", "%s:%s/%s" % (rev, BUNDLE, path)])


class Live:
    """Live resources by bundle name, loaded once."""

    def __init__(self):
        self.agents = {a["name"]: a for a in mjson("agent", "list")}
        self.squads = {s["name"]: s for s in mjson("squad", "list")}
        self.projects = {p["title"]: p for p in mjson("project", "list")}
        self.autopilots = {a["title"]: a for a in mjson("autopilot", "list")}
        self.skills = {s["name"]: s for s in mjson("skill", "list")}
        self._skill_full = {}

    def skill(self, sid, refresh=False):
        if refresh or sid not in self._skill_full:
            self._skill_full[sid] = mjson("skill", "get", sid, "--with-content")
        return self._skill_full[sid]


def owners(rev):
    """Map each live-text bundle file to (kind, live name, field) using the bundle's own json."""
    out = {}
    manifest = json.loads(show(rev, "manifest.json"))
    for a in manifest["agents"]:
        cfg = json.loads(show(rev, a["file"]))
        out[cfg["instructions_file"]] = ("agent", cfg["name"], "instructions")
        out[cfg["description_file"]] = ("agent", cfg["name"], "description")
        out[a["file"]] = ("agent", cfg["name"], "config")
    for s in manifest["squads"]:
        for field in ("instructions", "description"):
            if s.get(field + "_file"):
                out[s[field + "_file"]] = ("squad", s["name"], field)
    for p in manifest["projects"]:
        cfg = json.loads(show(rev, p["file"]))
        out[cfg["description_file"]] = ("project", cfg["title"], "description")
        out[p["file"]] = ("project", cfg["title"], "config")
    for a in manifest["autopilots"]:
        cfg = json.loads(show(rev, a["file"]))
        out[cfg["description_file"]] = ("autopilot", cfg["title"], "description")
        out[a["file"]] = ("autopilot", cfg["title"], "config")
    out["workspace/workspace.context.md"] = ("workspace", WORKSPACE_ID, "context")
    skills = {s["dir"].rstrip("/"): s["name"] for s in manifest["skills"]}
    return out, skills


def classify(path, owner_map, skill_dirs):
    """Return (kind, name, field_or_path) for a live text file, 'ignore', or None if unsupported."""
    if path.startswith(NOT_LIVE_PREFIXES) or path in NOT_LIVE_FILES:
        return "ignore"
    if path in owner_map:
        return owner_map[path]
    for d, name in skill_dirs.items():
        if path.startswith(d + "/"):
            rel = path[len(d) + 1:]
            return ("skill", name, rel)
    return None


def live_value(live, kind, name, field):
    if kind == "workspace":
        return mjson("workspace", "get", name).get(field) or ""
    table = {"agent": live.agents, "squad": live.squads, "project": live.projects,
             "autopilot": live.autopilots}[kind]
    return (table[name].get(field) or "") if name in table else None


def norm(kind, field, text):
    # Live agent, squad and project descriptions carry no trailing newline; the bundle files do.
    return text.rstrip("\n") if field == "description" and kind != "autopilot" else text


def push(live, kind, name, field, text):
    if kind == "workspace":
        if "\\" in text:
            raise RuntimeError("workspace context holds a backslash; --context would decode it")
        run(["multica", "workspace", "update", name, "--context", text])
        return
    if kind == "skill":
        sid = live.skills[name]["id"]
        if field == "SKILL.md":
            run(["multica", "skill", "update", sid, "--content-stdin"], stdin=text)
        elif field == "config.json":  # the skill's config field, not a file
            run(["multica", "skill", "update", sid, "--config", json.dumps(json.loads(text))])
        else:
            run(["multica", "skill", "files", "upsert", sid, "--path", field, "--content-stdin"], stdin=text)
        return
    if kind == "agent" and field == "config":
        push_agent_config(live, name, text)
        return
    value = norm(kind, field, text)
    if field == "description" and kind == "agent" and len(value) > DESC_MAX:
        raise RuntimeError("agent description is %d characters, cap %d" % (len(value), DESC_MAX))
    table = {"agent": live.agents, "squad": live.squads, "project": live.projects,
             "autopilot": live.autopilots}[kind]
    run(["multica", kind, "update", table[name]["id"], "--" + field, value])


def matches(live, kind, name, field, text):
    """Byte-exact read-back: True when live equals the file."""
    if kind == "skill":
        sid = live.skills[name]["id"]
        if field == "SKILL.md":
            s = mjson("skill", "get", sid)
            data = text.encode()
            return s.get("content_hash") == hashlib.sha256(data).hexdigest() and s.get("content_size") == len(data)
        if field == "config.json":
            return (mjson("skill", "get", sid).get("config") or {}) == json.loads(text)
        files = {f["path"]: f["content"] for f in live.skill(sid, refresh=True).get("files") or []}
        return files.get(field) == text
    if kind == "agent" and field == "config":
        return agent_config_live(live, name) == agent_config_file(text)
    if field == "config":
        return json_matches_live(live, kind, name, text)
    got = live_value(live, kind, name, field)
    return got is not None and got == norm(kind, field, text)


def exists(live, kind, name):
    if kind == "workspace":
        return True
    return name in {"agent": live.agents, "squad": live.squads, "project": live.projects,
                    "autopilot": live.autopilots, "skill": live.skills}[kind]


AGENT_CONFIG = ("model", "thinking_level", "max_concurrent_tasks", "skill_names")


def agent_config_live(live, name):
    a = live.agents[name]
    return {"model": a.get("model") or "", "thinking_level": a.get("thinking_level") or "",
            "max_concurrent_tasks": a.get("max_concurrent_tasks"),
            "skill_names": sorted(s["name"] for s in a.get("skills") or [])}


def agent_config_file(text):
    cfg = json.loads(text)
    return {"model": cfg.get("model") or "", "thinking_level": cfg.get("thinking_level") or "",
            "max_concurrent_tasks": cfg.get("max_concurrent_tasks"),
            "skill_names": sorted(cfg.get("skill_names") or [])}


def agent_config_unsupported(old_text, new_text):
    """Keys changed in an agent .json that this script cannot push (avatar, env, runtime...)."""
    old, new = json.loads(old_text) if old_text else {}, json.loads(new_text)
    return sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k) and k not in AGENT_CONFIG)


def push_agent_config(live, name, text):
    want, a = agent_config_file(text), live.agents[name]
    run(["multica", "agent", "update", a["id"], "--model", want["model"], "--thinking-level",
         want["thinking_level"], "--max-concurrent-tasks", str(want["max_concurrent_tasks"])])
    ids = [live.skills[n]["id"] for n in want["skill_names"]]
    run(["multica", "agent", "skills", "set", a["id"], "--skill-ids", ",".join(ids)])


def json_live_view(live, kind, name):
    """The live side of a bundle .json, in the bundle's own keys (ids resolved to names)."""
    if kind == "agent":
        a = live.agents[name]
        return {**agent_config_live(live, name), "avatar_url": a.get("avatar_url"),
                "visibility": a.get("visibility"), "permission_mode": a.get("permission_mode"),
                "service_tier": a.get("service_tier") or "", "custom_args": a.get("custom_args") or [],
                "runtime_config": a.get("runtime_config") or {}, "source_runtime_id": a.get("runtime_id"),
                "invocation_targets": a.get("invocation_targets") or [],
                "conversation_starters": a.get("conversation_starters") or [],
                "disabled_runtime_skills": a.get("disabled_runtime_skills") or [],
                "mcp_config": a.get("mcp_config"), "has_custom_env": bool(a.get("has_custom_env"))}
    people = {m["user_id"]: m["name"] for m in mjson("workspace", "member", "list")}
    agents = {a["id"]: a["name"] for a in live.agents.values()}
    if kind == "project":
        p = live.projects[name]
        res = mjson("project", "resource", "list", p["id"])
        return {"icon": p.get("icon"), "priority": p.get("priority"), "status": p.get("status"),
                "due_date": p.get("due_date"), "start_date": p.get("start_date"),
                "lead_type": p.get("lead_type"),
                "lead_name": (people if p.get("lead_type") == "member" else agents).get(p.get("lead_id")),
                "resources": sorted([r["resource_type"], json.dumps(r["resource_ref"], sort_keys=True),
                                     r.get("label"), r.get("position")] for r in res)}
    a = live.autopilots[name]
    projects = {p["id"]: t for t, p in live.projects.items()}
    triggers = mjson("autopilot", "trigger-list", a["id"])
    return {"status": a.get("status"), "execution_mode": a.get("execution_mode"),
            "issue_title_template": a.get("issue_title_template"),
            "project_title": projects.get(a.get("project_id")), "assignee_type": a.get("assignee_type"),
            "assignee_name": agents.get(a.get("assignee_id")) or people.get(a.get("assignee_id")),
            "subscriber_names": sorted(people.get(x.get("user_id") if isinstance(x, dict) else x, "?")
                                       for x in a.get("subscribers") or []),
            "had_webhook_trigger": any(t["kind"] == "webhook" for t in triggers),
            "triggers": sorted([t["kind"], t.get("label"), t.get("enabled"), t.get("cron_expression"),
                                t.get("timezone")] for t in triggers if t["kind"] != "webhook")}


def json_file_view(kind, text):
    """The bundle side of the same comparison; ids, file pointers and export bookkeeping drop out."""
    c = json.loads(text)
    if kind == "agent":
        return {**agent_config_file(text), "avatar_url": c.get("avatar_url"), "visibility": c.get("visibility"),
                "permission_mode": c.get("permission_mode"), "service_tier": c.get("service_tier") or "",
                "custom_args": c.get("custom_args") or [], "runtime_config": c.get("runtime_config") or {},
                "source_runtime_id": c.get("source_runtime_id"),
                "invocation_targets": c.get("invocation_targets") or [],
                "conversation_starters": c.get("conversation_starters") or [],
                "disabled_runtime_skills": c.get("disabled_runtime_skills") or [],
                "mcp_config": c.get("mcp_config"), "has_custom_env": bool(c.get("custom_env") or c.get("had_secrets"))}
    if kind == "project":
        return {"icon": c.get("icon"), "priority": c.get("priority"), "status": c.get("status"),
                "due_date": c.get("due_date"), "start_date": c.get("start_date"),
                "lead_type": c.get("lead_type"), "lead_name": c.get("lead_name"),
                "resources": sorted([r["resource_type"], json.dumps(r["resource_ref"], sort_keys=True),
                                     r.get("label"), r.get("position")] for r in c.get("resources") or [])}
    return {"status": c.get("status"), "execution_mode": c.get("execution_mode"),
            "issue_title_template": c.get("issue_title_template"), "project_title": c.get("project_title"),
            "assignee_type": c.get("assignee_type"), "assignee_name": c.get("assignee_name"),
            "subscriber_names": sorted(c.get("subscriber_names") or []),
            "had_webhook_trigger": bool(c.get("had_webhook_trigger")),
            "triggers": sorted([t["kind"], t.get("label"), t.get("enabled"), t.get("cron_expression"),
                                t.get("timezone")] for t in c.get("triggers") or [])}


def json_matches_live(live, kind, name, text):
    return json_live_view(live, kind, name) == json_file_view(kind, text)


def check(head):
    """Full drift report: every supported bundle file against live."""
    owner_map, skill_dirs = owners(head)
    live = Live()
    drift, missing = [], []
    files = git("ls-tree", "-r", "--name-only", head, "--", BUNDLE).splitlines()
    for full in files:
        path = full[len(BUNDLE) + 1:]
        c = classify(path, owner_map, skill_dirs)
        if c in ("ignore", None):
            continue
        kind, name, field = c
        if not exists(live, kind, name):
            missing.append(path)
        elif not (json_matches_live(live, kind, name, show(head, path)) if field == "config"
                  else matches(live, kind, name, field, show(head, path))):
            drift.append(path)
    return {"status": "clean" if not drift and not missing else "drift", "rev": head,
            "drift": drift, "missing_live": missing}


def sync(base, head, accept):
    owner_map, skill_dirs = owners(head)
    live = Live()
    changes = [l.split("\t") for l in git(
        "diff", "--name-status", "--no-renames", base, head, "--", BUNDLE).splitlines() if l]
    pushed, already, unsupported, failed, ignored = [], [], [], [], []
    for status, full in changes:
        path = full[len(BUNDLE) + 1:]
        c = classify(path, owner_map, skill_dirs)
        if c == "ignore":
            ignored.append(path)
            continue
        if c is None or not exists(live, c[0], c[1]) or (status == "D" and c[0] != "skill") \
                or (status == "D" and c[2] in ("SKILL.md", "config.json")):
            unsupported.append({"path": path, "status": status})
            continue
        kind, name, field = c
        if field == "config":
            text = show(head, path)
            if json_matches_live(live, kind, name, text):
                already.append(path)  # applied live by hand before the merge
                continue
            old = run(["git", "show", "%s:%s" % (base, full)]) if status == "M" else ""
            extra = agent_config_unsupported(old, text) if kind == "agent" else ["config"]
            if extra:
                unsupported.append({"path": path, "status": status, "keys": extra})
                continue
        try:
            if status == "D":
                sid = live.skills[name]["id"]
                if field in {f["path"] for f in live.skill(sid).get("files") or []}:
                    run(["multica", "skill", "files", "delete", sid, "--path", field])
                ok = field not in {f["path"] for f in live.skill(sid, refresh=True).get("files") or []}
            else:
                text = show(head, path)
                if not matches(live, kind, name, field, text):
                    push(live, kind, name, field, text)
                    if kind != "skill" and kind != "workspace":
                        live = Live()  # re-read lists so the read-back sees the update
                ok = matches(live, kind, name, field, text)
            (pushed if ok else failed).append({"path": path, "status": status, **({} if ok else {"error": "read-back differs"})})
        except Exception as e:  # report and keep going; the tag stays put
            failed.append({"path": path, "status": status, "error": str(e)})
    commits = git("log", "--format=%h %s", "%s..%s" % (base, head)).splitlines()
    # A squash merge keeps the fix commits only in the body, so read full messages.
    keys = sorted(set(re.findall(r"\[(DRK-[0-9]+)\]", git("log", "--format=%B", "%s..%s" % (base, head)))))
    move = not failed and (not unsupported or accept)
    if move:
        git("tag", "-f", TAG, head)
        git("push", "-f", "origin", "refs/tags/%s" % TAG)
    return {"status": "synced" if move else "blocked", "base": base, "head": head,
            "commits": commits, "issue_keys": keys, "pushed": pushed, "already_live": already, "unsupported": unsupported,
            "failed": failed, "ignored": ignored, "tag_moved": move}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("", "--check", "--accept"):
        print(__doc__)
        return 1
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # a second run waits, then finds nothing left to do
        git("fetch", "--quiet", "--force", "origin", "main", "+refs/tags/%s:refs/tags/%s" % (TAG, TAG)) \
            if git("ls-remote", "origin", "refs/tags/" + TAG) else git("fetch", "--quiet", "origin", "main")
        head = git("rev-parse", "origin/main")
        if mode == "--check":
            report = check(head)
        else:
            try:
                base = git("rev-parse", "refs/tags/" + TAG)
            except RuntimeError:
                report = {"status": "blocked", "error": "tag %s missing; seed it at the main commit live matches" % TAG}
                print(json.dumps(report, indent=2))
                return 2
            if base == head:
                report = {"status": "up-to-date", "head": head}
            else:
                report = sync(base, head, mode == "--accept")
    print(json.dumps(report, indent=2))
    return {"synced": 0, "up-to-date": 0, "clean": 0}.get(report["status"], 2)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, indent=2))
        sys.exit(1)
