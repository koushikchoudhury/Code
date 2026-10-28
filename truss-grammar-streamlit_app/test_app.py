"""UI smoke test using Streamlit's own test runner. Run: pytest -q"""
from streamlit.testing.v1 import AppTest


def fresh():
    at = AppTest.from_file("app.py", default_timeout=60).run()
    assert not at.exception
    return at


def test_loads_with_triangle():
    at = fresh()
    assert at.title[0].value == "Truss grammar workbench"
    assert [m.value for m in at.metric[:3]] == ["3", "3", "3"]


def test_apply_r1_then_undo():
    at = fresh()
    at.radio[0].set_value("R1").run()
    next(b for b in at.button if b.label == "Apply R1").click().run()
    assert not at.exception
    assert at.metric[0].value == "4" and at.metric[1].value == "5"
    next(b for b in at.sidebar.button if b.label == "Undo last step").click().run()
    assert at.metric[0].value == "3"


def test_blocked_match_cannot_apply():
    at = fresh()
    at.sidebar.selectbox[0].set_value("square").run()
    at.radio[0].set_value("R5").run()
    for i in range(len(at.selectbox[0].options)):
        at.selectbox[0].select_index(i).run()
        assert not at.exception


def test_random_walk_grows_history():
    at = fresh()
    next(b for b in at.sidebar.button if b.label.startswith("Run walk")).click().run()
    assert not at.exception
    assert len(at.session_state.history) > 1
