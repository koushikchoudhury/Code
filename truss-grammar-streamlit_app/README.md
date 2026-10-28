# Truss grammar workbench (Streamlit)

Python version of the Phase 1 workbench: five grammar rules on a planar truss, with exact checks
(connectivity, Maxwell count, geometry, rigidity-matrix rank), a rule preview, undo, a seeded random walk,
history thumbnails and the self-tests.

The rules are reconstructed from Fig. 4 of Shea et al., JCISE 25(12), 2025. They are not the paper's own code.

## Run it on your computer

    cd truss-grammar/streamlit_app
    pip install -r requirements.txt
    streamlit run app.py

A browser tab opens at http://localhost:8501.

## Check it

    pytest -q               # 15 grammar checks + 4 UI checks
    python parity_check.py  # compares this Python version with ../core.js (needs Node)

## Put it online (free)

1. Push this folder to your GitHub repo (next to the HTML version).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. New app, pick the repo and branch, set the main file to `truss-grammar/streamlit_app/app.py`, then Deploy.
4. You get a public link like `https://<name>.streamlit.app`.

## Files

- `truss_core.py`   grammar, checks, random walk, self-tests (no Streamlit inside)
- `app.py`          the Streamlit page
- `test_truss_core.py`, `test_app.py`   pytest files
- `parity_dump.js`, `parity_check.py`   JS vs Python comparison
