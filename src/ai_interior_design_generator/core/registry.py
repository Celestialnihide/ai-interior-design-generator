"""Plugin registry: discovery metadata, capability index, lookup."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ai_interior_design_generator.core.contracts import Capability
from ai_interior_design_generator.utils.logging import get_logger

log = get_logger("registry")


@dataclass(slots=True)
class PluginSpec:
    name: str
    version: str
    capabilities: tuple[Capability, ...]
    source: Path
    entry: str  # "module:ClassName"
    abi: str = "1.0"
    enabled: bool = True


class PluginRegistry:
    """Discovers plugins under `plugin_root` and indexes them by capability.

    Discovery is filesystem-based: any directory containing `plugin.toml` is a
    candidate. Manifest parsing lives in `core.loader`; this class only holds
    metadata and answers queries.
    """

    def __init__(self, plugin_root: Path) -> None:
        self._root = plugin_root
        self._specs: dict[str, PluginSpec] = {}
        self._by_capability: dict[Capability, list[str]] = {}

    def discover(self) -> int:
        from ai_interior_design_generator.core.loader import scan_plugin_root

        found = 0
        for spec in scan_plugin_root(self._root):
            self.register(spec)
            found += 1
        log.info("registry.discover", count=found, root=str(self._root))
        return found

    def register(self, spec: PluginSpec) -> None:
        if spec.name in self._specs:
            log.warning("registry.duplicate", name=spec.name, source=str(spec.source))
            return
        self._specs[spec.name] = spec
        for cap in spec.capabilities:
            self._by_capability.setdefault(cap, []).append(spec.name)

    def specs(self) -> list[PluginSpec]:
        return sorted(self._specs.values(), key=lambda s: s.name)

    def get(self, name: str) -> PluginSpec | None:
        return self._specs.get(name)

    def for_capability(self, cap: Capability) -> list[PluginSpec]:
        return [self._specs[n] for n in self._by_capability.get(cap, [])]

    def __len__(self) -> int:
        return len(self._specs)