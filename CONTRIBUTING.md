# Contributing to ai-interior-design-generator

Thanks for wanting to help build the plugin-host interior design generator. This document covers the workflow, the architecture you'll be extending, and the house style.

## Repo shape

We ship a **plugin host**. The core app boots, loads extensions from `plugins/`, and hands every extension the same shared contracts. If you're adding a feature, ask first: *is this core, or is this a plugin?* If it can live behind the `InteriorPlugin` interface, it belongs in a plugin.

```
src/ai_interior_design_generator/   core host
plugins/                            first-party extensions
```

## Setting up

```bash
git clone https://github.com/<org>/ai-interior-design-generator.git
cd ai-interior-design-generator
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python -m ai_interior_design_generator --list-plugins
```

The desktop shell is PySide6. Model inference runs through ONNX Runtime (CPU by default, DirectML on supported GPUs). Nothing downloads weights at build time — first run pulls them into `.cache/`.

## Adding a plugin

1. Create `plugins/<your_plugin>/` with `plugin.toml` and `__init__.py`.
2. Subclass `InteriorPlugin` from `core.contracts`.
3. Declare capabilities in `plugin.toml` (`room_analysis`, `palette`, `render_backend`, `furniture_catalog`, `export`).
4. Register with the loader — it discovers anything under `plugins/` at startup.
5. Add a test under `tests/plugins/`.

A minimal plugin:

```python
from ai_interior_design_generator.core.contracts import InteriorPlugin, RoomContext

class ScandinavianPlugin(InteriorPlugin):
    name = "scandinavian"
    capabilities = ("palette",)

    def suggest_palette(self, ctx: RoomContext) -> list[str]:
        return ["#F5F1E8", "#D9CBB3", "#8A7E6A", "#2E2A26"]
```

## Code style

- Python 3.12, type hints everywhere, `ruff` + `mypy --strict` on `src/`.
- No silent `except:` — log and re-raise or degrade explicitly.
- Desktop UI code goes in `ui/`; keep it thin. Logic lives in `core/`.
- Determinism matters: rendering pipelines must be seedable.

## Commits

Conventional commits. `feat(plugins): add japandi palette extension`. Reference issues. One logical change per PR.

## Tests

```bash
pytest -q
pytest -q tests/plugins/test_loader.py
```

CI runs on Windows Server 2022, Python 3.12. PRs that fail `ruff` or `mypy` get bounced by the bot, not by a human.

## Reporting bugs

Use the issue template. Attach `logs/host.log` and the output of `python -m ai_interior_design_generator --diagnostics`.

## Code of conduct

Be decent. We're building a design tool, not a fight club.