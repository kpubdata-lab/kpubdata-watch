"""The UI Lab builder renders the Issues First prototype and stays out of the demo (#106)."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def build_ui_lab() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_ui_lab", REPO_ROOT / "scripts" / "build_ui_lab.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_issues_first_orders_issues_changes_then_datasets(
    build_ui_lab: ModuleType, tmp_path: Path
) -> None:
    out = build_ui_lab.build(tmp_path)
    html = (out / "lab" / "issues" / "index.html").read_text(encoding="utf-8")
    assert html.index('id="active-issues"') < html.index('id="recent-changes"')
    assert html.index('id="recent-changes"') < html.index('id="datasets"')
    assert "UI Lab" in html
    assert "catalog-table" not in html  # the matrix belongs to the deployed Overview


def test_prototype_links_the_shared_assets_and_defines_no_tokens(
    build_ui_lab: ModuleType, tmp_path: Path
) -> None:
    out = build_ui_lab.build(tmp_path)
    html = (out / "lab" / "issues" / "index.html").read_text(encoding="utf-8")
    assert 'href="../../static/brand-v2.css"' in html
    assert (out / "static" / "brand-v2.css").is_file()
    assert "<style" not in html


def test_demo_build_does_not_include_ui_lab(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "build_demo", REPO_ROOT / "scripts" / "build_demo.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    out = module.build(tmp_path)
    assert not (out / "lab").exists()
    assert "UI Lab" not in (out / "index.html").read_text(encoding="utf-8")
