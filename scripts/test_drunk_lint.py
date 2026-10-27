"""Each lint rule fires on one injected fault. Run: python3 scripts/test_drunk_lint.py"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("sync", os.path.join(HERE, "drunk-live-sync.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)
SRC = os.path.join(HERE, "..", sync.BUNDLE)


def edit_json(path, fn):
    c = json.load(open(path))
    fn(c)
    json.dump(c, open(path, "w"), indent=2)


def edit_text(path, old, new):
    s = open(path).read()
    assert old in s, (path, old)
    open(path, "w").write(s.replace(old, new, 1))


def first(seq, key, value):
    return next(x for x in seq if x[key] == value)


FAULTS = {
    "L1": lambda b: open(b + "/agents/mika.description.md", "w").write("x" * 300 + "\n"),
    "L2": lambda b: edit_json(b + "/squads/dev-team.json", lambda c: c["members"].append({"agent_name": "ghost", "role": "member"})),
    "L3": lambda b: shutil.copy(b + "/agents/mika.json", b + "/agents/stray.json"),
    "L4": lambda b: edit_json(b + "/manifest.json", lambda c: first(c["squads"], "name", "dev-team")["members"].pop()),
    "L5": lambda b: edit_json(b + "/agents/mika.json", lambda c: c["skill_names"].append("no-such-skill")),
    "L6": lambda b: edit_json(b + "/autopilots/daily-stall-sweep.json", lambda c: c.update(assignee_name="default")),
    "L7": lambda b: shutil.copy(b + "/agents/mika.avatar.png", b + "/agents/dev-leader.avatar.png"),
    "L8": lambda b: edit_text(b + "/README.md", re.search(r"\d+ agents", open(b + "/README.md").read()).group(0), "99 agents"),
    "L9": lambda b: edit_text(b + "/README.md", "| run-medic        | codex   | gpt-6-luna          | low      |",
                              "| run-medic        | codex   | gpt-6-luna          | high     |"),
    "L10": lambda b: edit_text(b + "/docs/policies/09-agent-roles-and-responsibilities.md", "The fifteen chartered", "The fourteen chartered"),
    "L11": lambda b: open(b + "/skills/archify/SKILL.md", "a").write("\0"),
}


def lint_with(fault):
    tmp = tempfile.mkdtemp()
    try:
        bundle = os.path.join(tmp, sync.BUNDLE)
        shutil.copytree(SRC, bundle)
        if fault:
            FAULTS[fault](bundle)
        for cmd in (["init", "-q"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "t"]):
            subprocess.run(["git"] + cmd, cwd=tmp, check=True)
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            return sync.lint(sync.git("rev-parse", "HEAD"))["errors"]
        finally:
            os.chdir(cwd)
    finally:
        shutil.rmtree(tmp)


if __name__ == "__main__":
    assert lint_with(None) == [], lint_with(None)
    for rule in FAULTS:
        errors = lint_with(rule)
        assert any(e.startswith(rule + " ") for e in errors), (rule, errors)
        print("ok", rule, errors[0])
