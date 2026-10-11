"""The UI Lab builder renders every Overview prototype at every size and stays out of the demo."""

from __future__ import annotations

import importlib.util
import re
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


SIZES = (10, 50, 150)
PROTOTYPE_DIRS = ("status", "provider", "issues")


def _rows(html: str) -> int:
    return len(re.findall(r'<li class="dataset-row', html))


@pytest.mark.parametrize("name", PROTOTYPE_DIRS)
@pytest.mark.parametrize("size", SIZES)
def test_every_prototype_lists_every_dataset_at_each_size(
    build_ui_lab: ModuleType, tmp_path: Path, name: str, size: int
) -> None:
    out = build_ui_lab.build(tmp_path)
    html = (out / "lab" / name / str(size) / "index.html").read_text(encoding="utf-8")
    assert _rows(html) == size
    assert f"{size} datasets" in html
    assert 'href="../../../static/brand-v2.css"' in html
    assert "<style" not in html


def test_status_page_is_a_flat_list_without_issue_panels(
    build_ui_lab: ModuleType, tmp_path: Path
) -> None:
    out = build_ui_lab.build(tmp_path)
    html = (out / "lab" / "status" / "index.html").read_text(encoding="utf-8")
    assert 'id="datasets"' in html
    assert 'id="active-issues"' not in html
    assert "provider-1" not in html


def test_provider_grouped_puts_the_worst_provider_first(
    build_ui_lab: ModuleType, tmp_path: Path
) -> None:
    out = build_ui_lab.build(tmp_path)
    html = (out / "lab" / "provider" / "50" / "index.html").read_text(encoding="utf-8")
    assert html.index('id="provider-1"') < html.index('id="provider-2"')
    groups = build_ui_lab.provider_groups(
        [
            {"provider": "A", "health": "healthy"},
            {"provider": "B", "health": "critical"},
            {"provider": "B", "health": "healthy"},
            {"provider": "C", "health": "degraded"},
        ]
    )
    assert [g["name"] for g in groups] == ["B", "C", "A"]
    assert groups[0]["counts"]["healthy"] == 1
    assert groups[0]["total"] == 2


def test_index_links_each_prototype_at_each_size(build_ui_lab: ModuleType, tmp_path: Path) -> None:
    out = build_ui_lab.build(tmp_path)
    html = (out / "lab" / "index.html").read_text(encoding="utf-8")
    for name in PROTOTYPE_DIRS:
        for target in (f"{name}/index.html", *(f"{name}/{size}/index.html" for size in SIZES)):
            assert f'href="{target}"' in html
            assert (out / "lab" / target).is_file()


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
