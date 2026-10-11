"""The sized UI Lab fixtures are deterministic, valid snapshots (#33)."""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path
from types import ModuleType

import pytest

from kpubdata_watch.api.read_models.snapshot import ProductSnapshot

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def gen() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "gen_ui_lab_fixtures", REPO_ROOT / "scripts" / "gen_ui_lab_fixtures.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("size", [10, 50, 150])
def test_committed_fixtures_are_valid_and_match_the_generator(gen: ModuleType, size: int) -> None:
    snapshot = ProductSnapshot.from_directory(gen.directory(size))
    assert len(snapshot.datasets) == size
    assert len(snapshot.histories) == size
    assert gen.stale(size) == []
    health = Counter(d.health for d in snapshot.datasets)
    assert {"critical", "degraded", "unknown", "healthy"} <= set(health)
    assert health["healthy"] > size / 2


def test_generation_is_deterministic(gen: ModuleType) -> None:
    assert gen.generate(50) == gen.generate(50)
    assert gen.generate(10) != gen.generate(50)


def test_check_flags_a_hand_edited_file(
    gen: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gen, "FIXTURES_ROOT", tmp_path)
    assert gen.stale(10) != []
    gen.write(10)
    assert gen.stale(10) == []
    (tmp_path / "10-datasets" / "datasets.json").write_text("[]\n", encoding="utf-8")
    assert gen.stale(10) == ["10-datasets/datasets.json"]
