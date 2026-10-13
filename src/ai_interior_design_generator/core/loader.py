"""Manifest scanning + plugin instantiation.

Only reads `plugin.toml`. Instantiation is deferred until `instantiate()` so
that listing plugins never executes third-party code.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import tomli_w  # noqa: F401  (kept for symmetry with writer path; parser is stdlib)

from ai_interior_design_generator.core.abi import abi_compatible
from ai_interior_design_generator.core.contracts import Capability
from ai_interior_design_generator.core.registry import PluginSpec
from ai_interior_design_generator.utils.logging import get_logger

if TYPE_CHECKING:
    from ai_interior_design_generator.core.contracts import InteriorPlugin

log = get_logger("loader")

try:  # Python 3.11+ ships tomllib; 3.12 is our floor so this always succeeds.
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


def scan_plugin_root(root: Path) -> list[PluginSpec]:
    if not root.exists():
        log.warning("loader.root_missing", root=str(root))
        return []

    specs: list[PluginSpec] = []
    for manifest in sorted(root.glob("*/plugin.toml")):
        spec = _parse_manifest(manifest)
        if spec is not None:
            specs.append(spec)
    return specs


def _parse_manifest(manifest: Path) -> PluginSpec | None:
    try:
        with manifest.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        log.error("loader.bad_manifest", path=str(manifest), error=str(exc))
        return None

    plugin = data.get("plugin", {})
    name = plugin.get("name")
    entry = plugin.get("entry")
    if not name or not entry:
        log.error("loader.missing_fields", path=str(manifest))
        return None

    abi = str(plugin.get("abi", "1.0"))
    if not abi_compatible(abi):
        log.error("loader.abi_mismatch", name=name, declared=abi)
        return None

    caps = tuple(plugin.get("capabilities", ()))
    return PluginSpec(
        name=name,
        version=str(plugin.get("version", "0.0.0")),
        capabilities=tuple(c for c in caps if _is_capability(c)),
        source=manifest.parent,
        entry=entry,
        abi=abi,
        enabled=bool(plugin.get("enabled", True)),
    )


_VALID_CAPS: frozenset[str] = frozenset(
    {"room_analysis", "palette", "render_backend", "furniture_catalog", "export", "postprocess"}
)


def _is_capability(value: object) -> bool:
    return isinstance(value, str) and value in _VALID_CAPS


def instantiate(spec: PluginSpec) -> "InteriorPlugin":
    """Import and construct the plugin named by `spec.entry` (`module:ClassName`)."""
    import importlib

    module_name, _, class_name = spec.entry.partition(":")
    if not class_name:
        raise ValueError(f"plugin entry must be 'module:ClassName', got {spec.entry!r}")

    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    instance = cls()
    log.info("loader.instantiated", name=spec.name, cls=class_name)
    return instance


__all__ = ["scan_plugin_root", "instantiate", "Capability"]
</｜｜DSML｜｜ parameter>