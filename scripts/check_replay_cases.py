#!/usr/bin/env python3
"""Every replay case is traceable real evidence, with no credential in it (#43).

`tests/replay/cases/` is the regression corpus of real changes and silent-data
cases (docs/TESTING.md, "Replay Tests"). A case claims something happened to a
real dataset, so this gate refuses one whose claim cannot be checked or whose
files could leak a secret. Each case is a directory holding exactly:

- `case.json`  - the manifest: `id` (the directory name), `dataset`
  (`provider.dataset_key`), `scenario`, `provenance` and `expected`;
- `before.json` and `after.json` - the normalised observations on either side of
  the change. They must parse as JSON and must differ.

`provenance` records where the evidence came from: `source` is one of
`watch-observed`, `kpubdata-fixture` or `documented`, `reference` says where to
find it (a URL, or a repository path at a commit), `observed_on` is the ISO date
it was observed and may not lie in the future, and an optional `notice` is the
https URL of the provider's official notice. A `documented` case must link its
notice. Anything else in a case directory fails, because raw response bodies are
not kept long-term (SECURITY.md); and a credential-named key with a value other
than `<redacted>` (or JSON `null`), in any of the three files, fails.

This gate checks the corpus's shape. Replaying a case through its detector is the
replay test's job, once that detector exists.

Usage:
    python scripts/check_replay_cases.py [--root PATH]
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

CASES_DIR = Path("tests") / "replay" / "cases"
MANIFEST = "case.json"
BEFORE = "before.json"
AFTER = "after.json"
ALLOWED_FILES = {MANIFEST, BEFORE, AFTER}
IGNORED_FILES = {".gitkeep"}

SCENARIOS = (
    "contract_field_added",
    "contract_field_removed",
    "contract_type_changed",
    "freshness_delayed",
    "volume_anomaly",
    "completeness_anomaly",
    "provider_outage",
    "monitoring_failure",
)
SOURCES = ("watch-observed", "kpubdata-fixture", "documented")
CHECKS = ("availability", "freshness", "contract", "quality")
REDACTED = "<redacted>"

_DATASET = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
_CREDENTIAL = re.compile(
    r"""["']?\b(service_?key|api_?key|auth_?key|crtfc_key|access_?token|secret|password)\b["']?"""
    r"""\s*[:=]\s*["']?([^"'\s,&}]*)""",
    re.IGNORECASE,
)


def _text(value: object) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _date(value: object) -> dt.date | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def credential_violations(path: Path, where: str) -> list[str]:
    """Credential-named keys whose value was not redacted."""
    text = path.read_text(encoding="utf-8")
    found: list[str] = []
    for match in _CREDENTIAL.finditer(text):
        if match.group(2) not in (REDACTED, "null"):
            line = text.count("\n", 0, match.start()) + 1
            found.append(
                f"{where}:{line}: credential {match.group(1)!r} is not {REDACTED!r} "
                "(no credentials anywhere, SECURITY.md)"
            )
    return found


def _manifest_violations(manifest: dict[str, object], name: str, where: str) -> list[str]:
    found: list[str] = []
    if manifest.get("id") != name:
        found.append(f"{where}: 'id' must be the directory name {name!r}")
    dataset = manifest.get("dataset")
    if not (isinstance(dataset, str) and _DATASET.match(dataset)):
        found.append(f"{where}: 'dataset' must be 'provider.dataset_key'")
    if manifest.get("scenario") not in SCENARIOS:
        found.append(f"{where}: 'scenario' must be one of {', '.join(SCENARIOS)}")

    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict):
        found.append(f"{where}: 'provenance' is missing; a real case says where it came from")
    else:
        source = provenance.get("source")
        if source not in SOURCES:
            found.append(f"{where}: 'provenance.source' must be one of {', '.join(SOURCES)}")
        if _text(provenance.get("reference")) is None:
            found.append(f"{where}: 'provenance.reference' must say where the evidence is")
        observed = _date(provenance.get("observed_on"))
        if observed is None:
            found.append(f"{where}: 'provenance.observed_on' must be an ISO date (YYYY-MM-DD)")
        elif observed > dt.date.today():
            found.append(f"{where}: 'provenance.observed_on' {observed} is in the future")
        notice = provenance.get("notice")
        if notice is not None and not (isinstance(notice, str) and notice.startswith("https://")):
            found.append(f"{where}: 'provenance.notice' must be an https URL")
        if source == "documented" and notice is None:
            found.append(f"{where}: a 'documented' case must link the provider's 'notice'")

    expected = manifest.get("expected")
    if not isinstance(expected, dict):
        found.append(f"{where}: 'expected' is missing; a replay case states what it must yield")
    else:
        if expected.get("check") not in CHECKS:
            found.append(f"{where}: 'expected.check' must be one of {', '.join(CHECKS)}")
        if _text(expected.get("outcome")) is None:
            found.append(f"{where}: 'expected.outcome' must name the expected result")
    return found


def case_violations(case: Path, root: Path) -> list[str]:
    """Everything wrong with one case directory."""
    rel = case.relative_to(root)
    found: list[str] = []
    files = {path.name for path in case.iterdir() if path.name not in IGNORED_FILES}
    for extra in sorted(files - ALLOWED_FILES):
        found.append(
            f"{rel / extra}: not part of a case; keep only {', '.join(sorted(ALLOWED_FILES))}"
        )
    for missing in sorted(ALLOWED_FILES - files):
        found.append(f"{rel / missing}: missing")

    parsed: dict[str, object] = {}
    for name in sorted(ALLOWED_FILES & files):
        path = case / name
        if not path.is_file():
            found.append(f"{rel / name}: not a file")
            continue
        found.extend(credential_violations(path, str(rel / name)))
        try:
            parsed[name] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            found.append(f"{rel / name}: not valid JSON ({error})")

    manifest = parsed.get(MANIFEST)
    if MANIFEST in parsed:
        if isinstance(manifest, dict):
            found.extend(_manifest_violations(manifest, case.name, str(rel / MANIFEST)))
        else:
            found.append(f"{rel / MANIFEST}: must be a JSON object")
    if BEFORE in parsed and AFTER in parsed and parsed[BEFORE] == parsed[AFTER]:
        found.append(f"{rel}: {BEFORE} and {AFTER} are the same; a case records a change")
    return found


def main(argv: list[str] | None = None) -> int:
    """Check every case. Returns 0 when the corpus is well formed, 1 otherwise."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    root: Path = parser.parse_args(argv).root.resolve()

    cases_dir = root / CASES_DIR
    if not cases_dir.is_dir():
        print(f"  {cases_dir} does not exist, so nothing was checked", file=sys.stderr)
        return 1

    problems: list[str] = []
    cases = sorted(path for path in cases_dir.iterdir() if path.name not in IGNORED_FILES)
    for case in cases:
        if not case.is_dir():
            problems.append(f"{case.relative_to(root)}: a case is a directory")
            continue
        problems.extend(case_violations(case, root))

    if problems:
        print("The replay corpus has a case that cannot be trusted.\n", file=sys.stderr)
        for line in problems:
            print(f"  {line}", file=sys.stderr)
        print(
            "\nA replay case is real evidence: it names its source and date, holds only"
            "\nnormalised before/after observations, and carries no credential (#43).",
            file=sys.stderr,
        )
        return 1

    print(f"Replay corpus is well formed: {len(cases)} case(s) under {CASES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
