// Dumps what the JS core does, so parity_check.py can compare the Python port.
const c = require('../core.js');
const out = { presets: {}, walks: [] };
for (const k of Object.keys(c.PRESETS)) {
  const s = c.PRESETS[k].state || c.PRESETS[k];
  out.presets[k] = {
    canon: c.canon(s),
    options: c.enumerate(s).map(o => [o.rule, o.label, o.ok, o.kind || null, c.canon(o.state)]),
  };
}
for (const k of Object.keys(c.PRESETS)) {
  const s = c.PRESETS[k].state || c.PRESETS[k];
  for (let seed = 1; seed <= 25; seed++) {
    const trail = c.randomWalk(s, 10, seed);
    out.walks.push({ preset: k, seed, rules: trail.map(t => t.rule), canons: trail.map(t => c.canon(t.state)) });
  }
}
console.log(JSON.stringify(out));
