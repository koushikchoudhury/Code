"""Compares the Python port with the JavaScript core. Run: python parity_check.py (needs node)."""
import json, subprocess, pathlib, sys
import truss_core as c

here = pathlib.Path(__file__).parent
js = json.loads(subprocess.check_output(["node", str(here / "parity_dump.js")], text=True))
bad = 0
for k, d in js["presets"].items():
    s = c.preset_state(k)
    if c.canon(s) != d["canon"]:
        bad += 1; print("canon differs", k)
    py = [[o.rule, o.label, o.ok, o.kind, c.canon(o.state)] for o in c.enumerate_options(s)]
    if py != d["options"]:
        bad += 1; print("options differ", k, len(py), len(d["options"]))
n = 0
for w in js["walks"]:
    trail = c.random_walk(c.preset_state(w["preset"]), 10, w["seed"])
    if [t["rule"] for t in trail] != w["rules"] or [c.canon(t["state"]) for t in trail] != w["canons"]:
        bad += 1; print("walk differs", w["preset"], w["seed"])
    n += 1
print(f"{len(js['presets'])} presets and {n} seeded walks compared; {bad} differences")
sys.exit(1 if bad else 0)
