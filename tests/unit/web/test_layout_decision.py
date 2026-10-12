"""The layout decision of ADR 0015 holds at 10, 50 and 150 datasets (#33).

Overview: the status summary, then active issues, then recent changes, then the
datasets. Datasets: the flat searchable list with a Provider filter that is a
native, labelled control, whose options cover every provider and whose counts add
up to the whole list. Detail: the timeline comes first.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "build_demo.py"
LAB_FIXTURES = REPO_ROOT / "ui-lab" / "fixtures"
SIZES = (10, 50, 150)


@pytest.fixture(scope="module")
def build_demo() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_demo", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module", params=SIZES, ids=lambda n: f"{n}-datasets")
def site(
    request: pytest.FixtureRequest, build_demo: ModuleType, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    out: Path = build_demo.build(
        output_dir=tmp_path_factory.mktemp("site") / "_site",
        fixtures_dir=LAB_FIXTURES / f"{request.param}-datasets",
    )
    return out


def test_overview_is_summary_then_issues_then_changes_then_datasets(site: Path) -> None:
    html = (site / "index.html").read_text(encoding="utf-8")
    order = [
        'aria-label="Health summary"',
        'id="active-issues"',
        'id="recent-changes"',
        'id="datasets"',
    ]
    positions = [html.index(marker) for marker in order]
    assert positions == sorted(positions)


def test_overview_puts_unhealthy_datasets_before_healthy_ones(site: Path) -> None:
    html = (site / "index.html").read_text(encoding="utf-8")
    table = html[html.index('id="datasets"') :]
    badges = re.findall(r'class="status-badge status-(\w+)"', table)
    healthy_at = badges.index("healthy") if "healthy" in badges else len(badges)
    assert all(badge != "healthy" for badge in badges[:healthy_at])


def test_the_provider_filter_is_a_labelled_native_select(site: Path) -> None:
    html = (site / "datasets" / "index.html").read_text(encoding="utf-8")
    assert re.search(
        r'<label class="filter">\s*<span class="filter-label">Provider</span>\s*<select name="provider">',
        html,
    )
    assert 'role="search" aria-label="Filter datasets"' in html


def test_the_provider_options_cover_every_row_and_their_counts_add_up(site: Path) -> None:
    html = (site / "datasets" / "index.html").read_text(encoding="utf-8")
    select = html[html.index('<select name="provider">') :]
    select = select[: select.index("</select>")]
    options = re.findall(r'<option value="([^"]+)">[^<]*\((\d+)\)</option>', select)
    row_providers = re.findall(r'<tr class="catalog-row"[^>]*data-provider="([^"]+)"', html)
    assert options and {pid for pid, _ in options} == set(row_providers)
    for pid, count in options:
        assert row_providers.count(pid) == int(count)
    assert sum(int(count) for _, count in options) == len(row_providers)


def test_the_detail_page_starts_with_the_timeline(site: Path) -> None:
    first = sorted((site / "datasets").glob("*/index.html"))[0]
    html = first.read_text(encoding="utf-8")
    assert html.index(">Timeline</h2>") < html.index(">Health Checks</h2>")
