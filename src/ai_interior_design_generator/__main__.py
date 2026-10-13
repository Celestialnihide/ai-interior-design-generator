"""Entry point. Boots the host, loads plugins, dispatches to the UI or CLI."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_interior_design_generator.core.host import DesignHost
from ai_interior_design_generator.core.registry import PluginRegistry
from ai_interior_design_generator.config.settings import load_settings
from ai_interior_design_generator.utils.logging import configure_logging, get_logger


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="aidg",
        description="AI interior design generator (plugin host)",
    )
    p.add_argument("--list-plugins", action="store_true", help="list discovered plugins and exit")
    p.add_argument("--diagnostics", action="store_true", help="print environment diagnostics and exit")
    p.add_argument("--project", type=Path, default=None, help="open an .iidproj on launch")
    p.add_argument("--no-gui", action="store_true", help="run headless (batch render only)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings()
    configure_logging(settings.log_level)
    log = get_logger("host")

    registry = PluginRegistry(plugin_root=settings.plugin_root)
    registry.discover()

    if args.list_plugins:
        for spec in registry.specs():
            caps = ", ".join(spec.capabilities) or "-"
            print(f"{spec.name:<20} v{spec.version:<8} [{caps}]  {spec.source}")
        return 0

    if args.diagnostics:
        from ai_interior_design_generator.utils.diagnostics import print_diagnostics

        print_diagnostics(settings, registry)
        return 0

    host = DesignHost(settings=settings, registry=registry)
    host.bootstrap()

    if args.no_gui:
        log.info("headless mode; nothing to render without a project")
        return 0

    from ai_interior_design_generator.ui.app import run_app

    return run_app(host, initial_project=args.project)


if __name__ == "__main__":
    sys.exit(main())