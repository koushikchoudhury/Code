"""Run with:  pytest -q   (from this folder)"""
import pytest

from truss_core import run_tests

_RESULTS = run_tests()


@pytest.mark.parametrize("result", [r for r in _RESULTS if not r["info"]], ids=lambda r: r["name"][:70])
def test_grammar_check(result):
    assert result["pass"], result["detail"]
