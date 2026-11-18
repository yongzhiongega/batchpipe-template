# BatchPipe

A batch tool that reads customer reviews, sends them to an AI sentiment service and saves the results. You build it step by step across the seven chapters of Advanced Programming, from v0.1 to v1.0.

## Getting started

1. Click **Code → Codespaces → Create codespace on main**. It opens with Python 3.12 and a virtual environment (`.venv`) ready.
2. Check: `python --version` shows 3.12 or newer.
3. Make the sample data: `python tools/make_data.py 100` creates `data/reviews_100.csv`.
4. Then follow the Chapter 1 set-up activity: complete `pyproject.toml`, create `src/batchpipe/`, run `pip install -e .`, commit and push.

## What's already here

| Path | What it is |
| --- | --- |
| `tools/make_data.py` | Makes practice review files: `python tools/make_data.py 100`, `10k`, `1m`, or `1000 --dirty` |
| `tools/practice_service.py` | A pretend AI service for Chapter 4 onwards: `python tools/practice_service.py` |
| `pyproject.toml` | Started for you: you add the `[project]` sections in Chapter 1 |
| `.devcontainer/` | Codespace settings: Python 3.12 and `.venv` |
| `.gitignore` | Keeps `data/`, `.venv/` and caches out of Git |

## What you will add

```
src/batchpipe/         your code
tests/                 from Chapter 2
```

## Version history

Tag each version at the end of its lab: `git tag v0.1` then `git push --tags`.

| Version | Chapter | What it adds |
| --- | --- | --- |
| v0.1 | 1 | First working version |
| v0.2 | 2 | Organised core and tests |
| v0.3 | 3 | Handles big files |
| v0.4 | 4 | Reliable |
| v0.5 | 5 | Fast |
| v0.9 | 6 | Flexible |
| v1.0 | 7 | Reviewed release |
