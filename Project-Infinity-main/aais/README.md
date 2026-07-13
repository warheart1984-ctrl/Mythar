# AAIS Launcher Package

This folder contains the top-level AAIS projection wrapper used by ULX IDE.

It owns startup, bundle preparation, data-dir resolution, desktop-style app
checks, and a stable projection manifest for integration surfaces.

It does not own Jarvis runtime semantics.

## Owns

- `python -m aais` entrypoints
- project-root discovery
- frontend build preparation and staging into `app/static/`
- per-platform user data-dir selection
- `uvicorn` startup for the packaged shell
- desktop readiness checks through `doctor`
- projection manifest output through `projection`

## Does Not Own

- core Jarvis runtime truth in [`../Project-Infinity-main/src/api.py`](../Project-Infinity-main/src/api.py)
- workflow-shell behavior in [`../Project-Infinity-main/app/main.py`](../Project-Infinity-main/app/main.py)
- frontend route semantics in [`../Project-Infinity-main/frontend/src/App.jsx`](../Project-Infinity-main/frontend/src/App.jsx)

## External Suggestion Admission

This launcher folder inherits the project-wide external suggestion admission
law.

Outside proposals may influence comparison or packaging discussion here, but
they do not become launcher truth unless project law has filtered them and the
admitted form is documented.

## Main Files

- [`__main__.py`](./__main__.py)
  - module entrypoint for `python -m aais`
- [`launcher.py`](./launcher.py)
  - implements `start`, `prepare`, `doctor`, and `projection`

## Main Commands

```bash
python -m aais start --data-dir ./.runtime/aais-data
python -m aais prepare --force-build --data-dir ./.runtime/aais-data
python -m aais doctor --data-dir ./.runtime/aais-data
python -m aais projection --data-dir ./.runtime/aais-data
```

Legacy note:

- [`../Project-Infinity-main/start_jarvis.py`](../Project-Infinity-main/start_jarvis.py) now forwards to this launcher path

## Projection Behavior

The launcher now resolves the nested canonical AAIS app root under
[`../Project-Infinity-main`](../Project-Infinity-main) when run from the
top-level projection checkout.

The `projection` command prints a stable JSON manifest containing:

- projection identity
- entrypoints
- supported launcher commands
- runtime surface summary
- packaged frontend readiness

## Read Next

1. [../Project-Infinity-main/README.md](../Project-Infinity-main/README.md)
2. [../Project-Infinity-main/app/README.md](../Project-Infinity-main/app/README.md)
3. [../Project-Infinity-main/src/README.md](../Project-Infinity-main/src/README.md)
4. [../Project-Infinity-main/docs/contracts/EXTERNAL_SUGGESTION_ADMISSION_RULE.md](../Project-Infinity-main/docs/contracts/EXTERNAL_SUGGESTION_ADMISSION_RULE.md)
5. [../Project-Infinity-main/docs/runtime/AAIS_SYSTEM_HANDBOOK.md](../Project-Infinity-main/docs/runtime/AAIS_SYSTEM_HANDBOOK.md)
