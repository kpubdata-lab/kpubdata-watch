#!/usr/bin/env python3
"""Render the UI Lab prototypes with the demo fixtures (#106, #33).

UI Lab holds disposable layout experiments on the same read model the deployed
demo uses (docs/UI.md, ADR 0005). This script renders each prototype under
`ui-lab/` into a self-contained directory. It is deliberately separate from
`scripts/build_demo.py`: the deployed demo never includes UI Lab, and nothing in
the engine or the product templates depends on it.

    lab/issues/index.html     Issues First (C)
    static/                   the shared CSS, script and images (Brand v2 tokens)

Usage:
    python scripts/build_ui_lab.py [--output _lab] [--fixtures demo/fixtures]
"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys
from pathlib import Path
from types import ModuleType

from jinja2 import ChoiceLoader, FileSystemLoader

from kpubdata_watch.api.read_models.snapshot import ProductSnapshot
from kpubdata_watch.web.presentation import STATIC_DIR, TEMPLATES_DIR, environment

REPO_ROOT = Path(__file__).resolve().parent.parent
LAB_DIR = REPO_ROOT / "ui-lab"
FIXTURES_DIR = REPO_ROOT / "demo" / "fixtures"
DEFAULT_OUTPUT = REPO_ROOT / "_lab"
# prototype template (below ui-lab/) -> page directory in the output
PROTOTYPES = {"issues-first/index.html": "lab/issues"}


def _load_build_demo() -> ModuleType:
    """Import the demo builder for its read-model context; scripts/ is not a package."""
    spec = importlib.util.spec_from_file_location(
        "build_demo", REPO_ROOT / "scripts" / "build_demo.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("build_demo", module)
    spec.loader.exec_module(module)
    return module


def render(template_name: str, fixtures_dir: Path = FIXTURES_DIR, depth: int = 2) -> str:
    """Render one prototype; `depth` is how many directories below the output root it sits."""
    demo = _load_build_demo()
    snapshot = ProductSnapshot.from_directory(fixtures_dir)
    env = environment(TEMPLATES_DIR)
    env.loader = ChoiceLoader(
        [FileSystemLoader(str(LAB_DIR)), FileSystemLoader(str(TEMPLATES_DIR))]
    )
    # No product page is built here, so the navigation shows plain text, not links.
    built_pages: frozenset[str] = frozenset()
    context = demo.overview_context(snapshot, built_pages)
    context["datasets"] = demo.dataset_rows(snapshot)
    context["datasets"].sort(key=lambda row: demo._HEALTH_RANK[row["health"]])
    shell = demo._shell(snapshot, root="../" * depth, active_nav="overview")
    shell["built_pages"] = built_pages
    return env.get_template(template_name).render(**context, **shell)


def build(output_dir: Path = DEFAULT_OUTPUT, fixtures_dir: Path = FIXTURES_DIR) -> Path:
    """Render every prototype into `output_dir`, with the shared static assets."""
    for template_name, page_dir in PROTOTYPES.items():
        page = output_dir / page_dir / "index.html"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            render(template_name, fixtures_dir, len(Path(page_dir).parts)), encoding="utf-8"
        )
    static_out = output_dir / "static"
    if static_out.exists():
        shutil.rmtree(static_out)
    shutil.copytree(STATIC_DIR, static_out)
    return output_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES_DIR)
    args = parser.parse_args(argv)
    print(f"UI Lab written to {build(args.output, args.fixtures)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
