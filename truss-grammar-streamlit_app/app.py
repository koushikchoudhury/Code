"""Truss grammar workbench (Streamlit). Run:  streamlit run app.py

Rules are reconstructed from Fig. 4 of Shea et al., JCISE 25(12), 2025; they are not the paper's own code.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

import truss_core as tc

INK, MUTED, AMBER, BLUE, RED, GRID = "#1f2933", "#7b8794", "#d98e04", "#1f6feb", "#d1242f", "#e4e7eb"

st.set_page_config(page_title="Truss grammar workbench", page_icon="📐", layout="wide")


# ---------- drawing ----------
def draw(ax, state, option=None, mini=False):
    nm = tc.node_map(state)
    removed, added = set(), set()
    new_nm = None
    if option is not None:
        new_nm = tc.node_map(option.state)
        old = {tc.edge_key_xy(e, nm): e for e in state.edges}
        new = {tc.edge_key_xy(e, new_nm): e for e in option.state.edges}
        removed, added = set(old) - set(new), set(new) - set(old)
    pts = [(n.x, n.y) for n in state.nodes] + ([(n.x, n.y) for n in option.state.nodes] if option else [])
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    pad = 0.35
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.set_aspect("equal")
    lw = 1.6 if mini else 2.4
    for e in state.edges:
        k = tc.edge_key_xy(e, nm)
        p, q = nm[e.a], nm[e.b]
        if k in removed:
            ax.plot([p.x, q.x], [p.y, q.y], color=AMBER, lw=lw + 1.2, solid_capstyle="round", zorder=2)
        else:
            ax.plot([p.x, q.x], [p.y, q.y], color=INK, lw=lw, ls=(0, (4, 3)) if e.free else "-",
                    solid_capstyle="round", zorder=2)
    if option is not None:
        colour = BLUE if option.ok else RED
        for e in option.state.edges:
            if tc.edge_key_xy(e, new_nm) in added:
                p, q = new_nm[e.a], new_nm[e.b]
                ax.plot([p.x, q.x], [p.y, q.y], color=colour, lw=lw + 0.6, ls=(0, (2, 2)), zorder=3)
        for n in option.state.nodes:
            if tc.nkey(n) not in {tc.nkey(m) for m in state.nodes}:
                ax.scatter([n.x], [n.y], s=70, color="white", edgecolor=colour, lw=2, zorder=5)
    for n in state.nodes:
        if n.fixed:
            ax.scatter([n.x], [n.y - 0.07], marker="^", s=(110 if mini else 260), color=MUTED, zorder=3)
        ax.scatter([n.x], [n.y], s=(26 if mini else 80), color="white", edgecolor=INK, lw=1.6, zorder=4)
        if not mini:
            ax.annotate(str(n.id), (n.x, n.y), xytext=(7, 7), textcoords="offset points", fontsize=9, color=MUTED)
    if mini:
        ax.axis("off")
    else:
        ax.grid(True, color=GRID, lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(labelsize=8, colors=MUTED)


def figure(state, option=None, mini=False):
    fig, ax = plt.subplots(figsize=(1.7, 1.4) if mini else (6.4, 4.6), dpi=110)
    draw(ax, state, option, mini)
    fig.tight_layout(pad=0.3 if mini else 1.0)
    return fig


def show(fig):
    st.pyplot(fig, clear_figure=True, width="stretch")
    plt.close(fig)


# ---------- session state ----------
def reset(preset):
    st.session_state.preset = preset
    st.session_state.history = [{"rule": "start", "label": tc.PRESETS[preset][0], "state": tc.preset_state(preset)}]
    st.session_state.version = st.session_state.get("version", 0) + 1


if "history" not in st.session_state:
    reset("triangle")

hist = st.session_state.history
cur = hist[-1]["state"]
version = st.session_state.version


def push(rule, label, state):
    hist.append({"rule": rule, "label": label, "state": state})
    st.session_state.version += 1


@st.cache_data
def cached_tests():
    return tc.run_tests()


# ---------- sidebar ----------
with st.sidebar:
    st.header("Start")
    keys = list(tc.PRESETS)
    choice = st.selectbox("Starting design", keys, index=keys.index(st.session_state.preset),
                          format_func=lambda k: tc.PRESETS[k][0])
    if choice != st.session_state.preset:
        reset(choice)
        st.rerun()
    if st.button("Reset", width="stretch"):
        reset(st.session_state.preset)
        st.rerun()
    if st.button("Undo last step", width="stretch", disabled=len(hist) < 2):
        hist.pop()
        st.session_state.version += 1
        st.rerun()

    st.header("Random walk")
    steps = st.slider("Steps", 1, 20, 8)
    seed = st.number_input("Seed", 1, 999999, 7, step=1)
    st.caption("Applies a random valid rule at each step. The same seed always gives the same walk.")
    if st.button("Run walk from current design", width="stretch"):
        for t in tc.random_walk(cur, int(steps), int(seed)):
            hist.append({"rule": t["rule"], "label": t["label"], "state": t["state"]})
        st.session_state.version += 1
        st.rerun()

# ---------- main ----------
st.title("Truss grammar workbench")
st.caption("Phase 1: a hand-coded grammar with exact checks. Rules reconstructed from Fig. 4 of Shea et al. (2025), "
           "not taken from the paper's supplementary code.")

tab_work, tab_hist, tab_tests, tab_about = st.tabs(["Workbench", "History", "Self-tests", "Scope"])

with tab_work:
    options = tc.enumerate_options(cur)
    sm = tc.summary(cur)
    left, right = st.columns([3, 2], gap="large")

    with right:
        banner = {"isostatic": st.success, "mechanism": st.error, "redundant": st.warning}[sm.status]
        banner({"isostatic": "Isostatic: stiff, with no redundant members.",
                "mechanism": "Mechanism: this design can move.",
                "redundant": "Redundant: more members than needed."}[sm.status])
        c1, c2, c3 = st.columns(3)
        c1.metric("Joints", sm.j)
        c2.metric("Members", sm.b)
        c3.metric("Needed (2j−3)", sm.need)
        c4, c5, c6 = st.columns(3)
        c4.metric("Rigidity rank", sm.rank)
        c5.metric("Supports", sm.fixed)
        c6.metric("Free members", sm.free)

        st.subheader("Apply a rule")
        rule_ids = [r.id for r in tc.RULES]

        def count(rid):
            mine = [o for o in options if o.rule == rid]
            return sum(o.ok for o in mine), len(mine)

        rid = st.radio("Rule", rule_ids, key=f"rule{version}", horizontal=True,
                       format_func=lambda r: f"{r} {tc.RULE_BY_ID[r].name} ({count(r)[0]})")
        rule = tc.RULE_BY_ID[rid]
        st.caption(rule.text)
        mine = [o for o in options if o.rule == rid]
        selected = None
        if not mine:
            st.info(f"{rid} has no match in this design.")
        else:
            idx = st.selectbox("Match", range(len(mine)), key=f"match{version}{rid}",
                               format_func=lambda i: mine[i].label + ("" if mine[i].ok else "  — blocked"))
            selected = mine[idx]
            if selected.ok:
                st.success(f"Valid. Result: {selected.sm.j} joints, {selected.sm.b} members, rank {selected.sm.rank} "
                           f"of {selected.sm.need}.")
            else:
                st.error(f"Blocked ({selected.kind}): {selected.reason}")
            if st.button(f"Apply {rid}", type="primary", disabled=not selected.ok, width="stretch"):
                push(rid, selected.label, selected.state)
                st.rerun()
        valid_total = sum(o.ok for o in options)
        st.caption(f"{valid_total} of {len(options)} rule matches are valid in this design.")
        if valid_total == 0:
            st.warning("Dead end: no rule can be applied. Undo or reset.")

    with left:
        show(figure(cur, selected))
        st.caption("Dashed black = free member. Triangle = support. Amber = removed by the previewed rule; "
                   "blue dashed = added; red dashed = added but blocked.")

with tab_hist:
    st.write(f"{len(hist)} designs in the sequence, oldest first.")
    per_row = 5
    for start in range(0, len(hist), per_row):
        cols = st.columns(per_row)
        for col, i in zip(cols, range(start, min(start + per_row, len(hist)))):
            h = hist[i]
            with col:
                show(figure(h["state"], mini=True))
                s = tc.summary(h["state"])
                title = "start" if h["rule"] == "start" else f"{i}. {h['rule']} {tc.RULE_BY_ID[h['rule']].name}"
                st.caption(f"**{title}**  \n{s.j} joints, {s.b} members")

with tab_tests:
    results = cached_tests()
    real = [r for r in results if not r["info"]]
    passed = sum(r["pass"] for r in real)
    (st.success if passed == len(real) else st.error)(f"{passed} of {len(real)} checks pass")
    st.dataframe([{"": "info" if r["info"] else ("pass" if r["pass"] else "FAIL"), "Check": r["name"],
                   "Detail": r["detail"]} for r in results], hide_index=True, width="stretch")
    st.caption("These tests run the real rules, not a fixed script. The same 15 checks run in the JavaScript "
               "version, and parity_check.py confirms both versions give identical results.")

with tab_about:
    st.markdown("""
**What this shows.** A planar truss grammar of five rules (Subdivide, Merge, Extend, Contract, Flip) acting on a
graph of joints and members. Every result is checked: connectivity, the Maxwell count (members = 2 joints − 3),
joint and member geometry, and the rank of the rigidity matrix.

**What it does not show yet.**
- The rules are my reconstruction from the before and after panels of Fig. 4. Compare them with the paper's
  supplementary code before calling this the paper's grammar.
- Checks are exact structural checks. There is no load case, member sizing or stress solver yet.
- There is no language model in the loop. Phase 2 lets a model propose rules, and these tests judge them.
""")
