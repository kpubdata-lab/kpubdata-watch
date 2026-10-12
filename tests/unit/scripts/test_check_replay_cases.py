"""The replay corpus gate has to actually fail (#43).

A replay case claims a real dataset changed, so the gate refuses one whose source
cannot be traced or whose files could leak a credential. These tests plant one
violation at a time in a temporary repository and expect exit code 1. The planted
cases are inputs to the gate, not evidence: nothing here is added to the corpus.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts" / "check_replay_cases.py"
_CASE = "contract-field-removed"


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_SCRIPT), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )


def _manifest() -> dict[str, Any]:
    return {
        "id": _CASE,
        "dataset": "datago.air_quality",
        "scenario": "contract_field_removed",
        "provenance": {
            "source": "kpubdata-fixture",
            "reference": "kpubdata-lab/kpubdata@abc1234:tests/fixtures/example.json",
            "observed_on": "2026-10-01",
        },
        "expected": {"check": "contract", "outcome": "breaking"},
    }


def _repo(
    tmp_path: Path,
    manifest: dict[str, Any] | None = None,
    before: str = '{"fields": ["a", "b"]}',
    after: str = '{"fields": ["a"]}',
) -> Path:
    case = tmp_path / "tests" / "replay" / "cases" / _CASE
    case.mkdir(parents=True)
    (case.parent / ".gitkeep").write_text("", encoding="utf-8")
    (case / "case.json").write_text(json.dumps(manifest or _manifest()), encoding="utf-8")
    (case / "before.json").write_text(before, encoding="utf-8")
    (case / "after.json").write_text(after, encoding="utf-8")
    return tmp_path


def test_this_repository_passes() -> None:
    """The case the gate must not break: the corpus as it is today."""
    result = _run(REPO_ROOT)
    assert result.returncode == 0, result.stderr


def test_a_well_formed_case_passes(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "1 case(s)" in result.stdout


def test_a_redacted_or_null_credential_passes(tmp_path: Path) -> None:
    manifest = _manifest()
    manifest["provenance"]["reference"] = "https://apis.data.go.kr/x?serviceKey=<redacted>&a=1"
    result = _run(_repo(tmp_path, manifest=manifest, after='{"fields": ["a"], "api_key": null}'))
    assert result.returncode == 0, result.stderr


def test_a_missing_corpus_fails_rather_than_passing_empty(tmp_path: Path) -> None:
    result = _run(tmp_path)
    assert result.returncode == 1


def _without(key: str) -> dict[str, Any]:
    manifest = _manifest()
    del manifest[key]
    return manifest


def _provenance(**changes: Any) -> dict[str, Any]:
    manifest = _manifest()
    manifest["provenance"].update(changes)
    return manifest


@pytest.mark.parametrize(
    ("manifest", "message"),
    [
        (_manifest() | {"id": "other"}, "'id' must be the directory name"),
        (_manifest() | {"dataset": "air_quality"}, "'dataset'"),
        (_manifest() | {"scenario": "looks_odd"}, "'scenario'"),
        (_without("provenance"), "'provenance' is missing"),
        (_provenance(source="ai-guess"), "'provenance.source'"),
        (_provenance(reference=" "), "'provenance.reference'"),
        (_provenance(observed_on="01/10/2026"), "'provenance.observed_on' must be an ISO date"),
        (_provenance(observed_on="2999-01-01"), "is in the future"),
        (_provenance(notice="http://example.go.kr/notice"), "'provenance.notice'"),
        (_provenance(source="documented"), "must link the provider's 'notice'"),
        (_without("expected"), "'expected' is missing"),
        (_manifest() | {"expected": {"check": "vibes", "outcome": "x"}}, "'expected.check'"),
        (_manifest() | {"expected": {"check": "contract"}}, "'expected.outcome'"),
    ],
)
def test_an_untraceable_manifest_fails(
    tmp_path: Path, manifest: dict[str, Any], message: str
) -> None:
    result = _run(_repo(tmp_path, manifest=manifest))
    assert result.returncode == 1
    assert message in result.stderr


@pytest.mark.parametrize(
    "leak",
    [
        '{"fields": ["a"], "serviceKey": "planted-xxxx"}',
        '{"fields": ["a"], "url": "https://x/y?ServiceKey=abcd1234&n=1"}',
        '{"fields": ["a"], "crtfc_key": "0123456789"}',
        '{"fields": ["a"], "API_KEY": "zzz"}',
    ],
)
def test_an_unredacted_credential_fails(tmp_path: Path, leak: str) -> None:
    result = _run(_repo(tmp_path, after=leak))
    assert result.returncode == 1
    assert "after.json:1: credential" in result.stderr


def test_an_unchanged_case_fails(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path, after='{"fields": ["a", "b"]}'))
    assert result.returncode == 1
    assert "are the same" in result.stderr


def test_invalid_json_fails(tmp_path: Path) -> None:
    result = _run(_repo(tmp_path, before="{not json"))
    assert result.returncode == 1
    assert "before.json: not valid JSON" in result.stderr


def test_a_raw_response_kept_beside_the_case_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "tests" / "replay" / "cases" / _CASE / "raw.xml").write_text("<x/>", encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "raw.xml: not part of a case" in result.stderr


def test_a_missing_observation_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "tests" / "replay" / "cases" / _CASE / "after.json").unlink()
    result = _run(root)
    assert result.returncode == 1
    assert "after.json: missing" in result.stderr


def test_a_stray_file_in_the_corpus_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "tests" / "replay" / "cases" / "notes.txt").write_text("x", encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "a case is a directory" in result.stderr


def test_a_manifest_that_is_not_an_object_fails(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    (root / "tests" / "replay" / "cases" / _CASE / "case.json").write_text("[]", encoding="utf-8")
    result = _run(root)
    assert result.returncode == 1
    assert "must be a JSON object" in result.stderr
