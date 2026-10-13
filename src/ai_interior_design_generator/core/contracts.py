"""Shared contracts every plugin must satisfy.

These are the stable interfaces the host hands to extensions. Breaking changes
here bump the host ABI version declared in `core.abi.HOST_ABI`.
"""
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol, runtime_checkable

Capability = Literal[
    "room_analysis",
    "palette",
    "render_backend",
    "furniture_catalog",
    "export",
    "postprocess",
]


@dataclass(slots=True, frozen=True)
class RoomContext:
    """Everything a plugin needs to reason about a room image.

    Attributes:
        image_path: Absolute path to the source photo (validated under project root).
        width: Image width in pixels, > 0.
        height: Image height in pixels, > 0.
        room_type: Detected or user-declared room type.
        seed: Deterministic seed for any stochastic plugin output.
    """

    image_path: Path
    width: int
    height: int
    room_type: str
    seed: int = 0


@dataclass(slots=True)
class PaletteSuggestion:
    name: str
    colors: list[str] = field(default_factory=list)
    notes: str = ""


@runtime_checkable
class InteriorPlugin(Protocol):
    """The contract. Subclass `PluginBase` for a default implementation."""

    name: str
    version: str
    capabilities: tuple[Capability, ...]

    def activate(self, host_api: "HostAPI") -> None: ...
    def deactivate(self) -> None: ...


class PluginBase(ABC):
    """Convenience base class. Override only what you need."""

    name: str = "unnamed"
    version: str = "0.0.0"
    capabilities: tuple[Capability, ...] = ()

    def activate(self, host_api: "HostAPI") -> None:  # noqa: B027 (intentional no-op)
        return None

    def deactivate(self) -> None:  # noqa: B027
        return None

    # Optional capability hooks — plugins implement the ones they declare.
    def suggest_palette(self, ctx: RoomContext) -> list[PaletteSuggestion]:
        raise NotImplementedError

    def analyze_room(self, ctx: RoomContext) -> dict[str, object]:
        raise NotImplementedError


@runtime_checkable
class HostAPI(Protocol):
    """What the host exposes to plugins. Keep this small."""

    def log(self, plugin: str, message: str) -> None: ...
    def model_path(self, model_id: str) -> Path: ...
    def project_root(self) -> Path: ...