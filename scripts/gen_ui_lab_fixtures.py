#!/usr/bin/env python3
"""Generate the deterministic UI Lab demo fixtures at 10, 50 and 150 datasets (#33).

The layout comparison needs the same prototypes at several catalog sizes (docs/UI.md,
PRD "UI Lab Fixtures"). Each size is a complete product snapshot in the five-file
form `ProductSnapshot.from_directory` loads, written under `ui-lab/fixtures/`.
The generator is seeded by the dataset count, so the output never changes between
runs; `--check` fails when the committed files differ from it. Do not edit the
generated files by hand.

    ui-lab/fixtures/10-datasets/   snapshot, datasets, incidents, changes, histories
    ui-lab/fixtures/50-datasets/
    ui-lab/fixtures/150-datasets/

Usage:
    python scripts/gen_ui_lab_fixtures.py [--check]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from kpubdata_watch.api.read_models.snapshot import ProductSnapshot

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_ROOT = REPO_ROOT / "ui-lab" / "fixtures"
SIZES = (10, 50, 150)
KST = timezone(timedelta(hours=9))
NOW = datetime(2026, 10, 2, 21, 15, tzinfo=KST)  # the same instant as demo/fixtures
HISTORY_DAYS = 30

PROVIDERS = (
    ("molit", "국토교통부"),
    ("seoul", "서울특별시"),
    ("kma", "기상청"),
    ("visitkorea", "한국관광공사"),
    ("kostat", "통계청"),
    ("keco", "한국환경공단"),
    ("mois", "행정안전부"),
    ("pps", "조달청"),
    ("hira", "건강보험심사평가원"),
    ("moel", "고용노동부"),
)
CATEGORIES = ("real_estate", "transport", "weather", "tourism", "statistics", "environment")
# How many datasets are not Healthy, as a share of the catalog (at least one each).
SHARE = {"critical": 0.04, "degraded": 0.10, "unknown": 0.04}
CHANGE_SHARE = 0.06


def _iso(moment: datetime) -> str:
    return moment.isoformat()


def _checks() -> dict[str, dict[str, Any]]:
    return {
        name: {"status": "pass", "summary": None}
        for name in ("availability", "freshness", "contract", "quality")
    }


def _incident(
    rng: random.Random, number: int, dataset_id: str, health: str
) -> tuple[dict[str, Any], str, str]:
    """One ongoing incident for a Degraded or Critical dataset: (incident, check, summary)."""
    check = rng.choice(
        ("freshness", "quality") if health == "degraded" else ("availability", "contract")
    )
    started = NOW - timedelta(minutes=rng.randint(40, 300))
    first_seen = started + timedelta(minutes=2)
    confirmed = started + timedelta(minutes=5)
    if check == "freshness":
        delay = rng.randint(40, 120)
        title, summary = (
            "Freshness delayed",
            f"No new data {delay} minutes after the expected update.",
        )
        expected: dict[str, Any] = {"update_at": _iso(started), "tolerance_minutes": 30}
        observed: dict[str, Any] = {"latest_data_at": _iso(started - timedelta(minutes=delay))}
        difference: dict[str, Any] = {"delay_minutes": delay}
        rule = ("freshness.expected_window", "Expected update window exceeded")
    elif check == "quality":
        below = rng.randint(20, 60)
        title, summary = "Volume anomaly", f"Record count is {below}% below the expected range."
        expected = {"record_count_min": 10000, "record_count_max": 10500}
        observed = {"record_count": 10000 * (100 - below) // 100}
        difference = {"below_minimum_percent": below}
        rule = ("quality.volume.range", "Record count outside the expected range")
    elif check == "availability":
        title, summary = "API unavailable", "HTTP 500 on three consecutive probes."
        expected = {"http_status": 200}
        observed = {"http_status": 500, "consecutive_failures": 3}
        difference = {"consecutive_failures": 3}
        rule = ("availability.consecutive_failures", "Three consecutive failed probes")
    else:
        title, summary = (
            "Breaking contract change",
            "The field addr2 disappeared from the response.",
        )
        expected = {"fields": ["addr1:string", "addr2:string"]}
        observed = {"fields": ["addr1:string"]}
        difference = {"removed": ["addr2:string"]}
        rule = ("contract.field_removed", "A field present in the accepted schema was removed")
    incident = {
        "id": f"inc-lab-{number:03d}",
        "dataset_id": dataset_id,
        "check": check,
        "severity": "critical" if health == "critical" else "warning",
        "status": "ongoing",
        "title": title,
        "summary": summary,
        "started_at": _iso(started),
        "detected_at": _iso(first_seen),
        "confirmed_at": _iso(confirmed),
        "resolved_at": None,
        "evidence": {
            "expected": expected,
            "observed": observed,
            "difference": difference,
            "rule": {"id": rule[0], "description": rule[1]},
            "first_seen_at": _iso(first_seen),
            "confirmed_at": _iso(confirmed),
        },
        "timeline": [
            {"at": _iso(first_seen), "summary": "First observed"},
            {"at": _iso(confirmed), "summary": "Confirmed by a second observation"},
        ],
        "related_change_id": None,
    }
    return incident, check, summary


def _history(rng: random.Random, health: str) -> list[dict[str, Any]]:
    """Thirty days ending today: mostly Healthy, a few abnormal days, today as it is."""
    days: list[dict[str, Any]] = []
    for offset in range(HISTORY_DAYS - 1, -1, -1):
        day = (NOW - timedelta(days=offset)).date().isoformat()
        if offset == 0:
            state = health
        elif rng.random() < 0.06:
            state = rng.choice(("degraded", "degraded", "critical", "unknown"))
        else:
            state = "healthy"
        summary = None if state == "healthy" else f"{state.capitalize()} day"
        days.append({"date": day, "health": state, "summary": summary})
    return days


def generate(count: int) -> dict[str, list[Any] | dict[str, Any]]:
    """The five fixture files for a catalog of `count` datasets, as plain data."""
    rng = random.Random(count)
    order = list(range(count))
    rng.shuffle(order)
    health_of: dict[int, str] = {}
    cursor = 0
    for health, share in SHARE.items():
        for index in order[cursor : cursor + max(1, round(count * share))]:
            health_of[index] = health
        cursor += max(1, round(count * share))
    changed = set(order[cursor : cursor + max(1, round(count * CHANGE_SHARE))])

    datasets: list[dict[str, Any]] = []
    incidents: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    histories: list[dict[str, Any]] = []
    for index in range(count):
        provider_id, provider_name = PROVIDERS[min(int(rng.random() ** 2 * len(PROVIDERS)), 9)]
        dataset_id = f"{provider_id}.demo_{index + 1:03d}"
        health = health_of.get(index, "healthy")
        checked = NOW - timedelta(minutes=rng.randint(1, 14), seconds=rng.randint(0, 59))
        checks = _checks()
        active: list[str] = []
        latest_changes: list[str] = []
        last_healthy = checked
        if health in ("degraded", "critical"):
            incident, check, summary = _incident(rng, len(incidents) + 1, dataset_id, health)
            checks[check] = {
                "status": "warn" if health == "degraded" else "fail",
                "summary": summary,
            }
            incidents.append(incident)
            active.append(incident["id"])
            last_healthy = datetime.fromisoformat(incident["started_at"])
            if check == "contract":
                change_id = f"chg-lab-{len(changes) + 1:03d}"
                changes.append(
                    {
                        "id": change_id,
                        "dataset_id": dataset_id,
                        "change_type": "contract",
                        "severity": "critical",
                        "title": "Contract changed",
                        "summary": "The field addr2 was removed.",
                        "detected_at": incident["detected_at"],
                        "diff": {"added": [], "removed": ["addr2:string"], "changed": []},
                        "health_impact": "critical",
                        "related_incident_id": incident["id"],
                    }
                )
                incident["related_change_id"] = change_id
                latest_changes.append(change_id)
        elif health == "unknown":
            checks["quality"] = {"status": "unknown", "summary": "The probe could not run"}
            last_healthy = checked - timedelta(hours=rng.randint(2, 20))
        elif index in changed:
            change_id = f"chg-lab-{len(changes) + 1:03d}"
            changes.append(
                {
                    "id": change_id,
                    "dataset_id": dataset_id,
                    "change_type": "contract",
                    "severity": "info",
                    "title": "Contract changed",
                    "summary": "The field productEngName was added.",
                    "detected_at": _iso(NOW - timedelta(hours=rng.randint(1, 20))),
                    "diff": {"added": ["productEngName:string"], "removed": [], "changed": []},
                    "health_impact": "none",
                    "related_incident_id": None,
                }
            )
            latest_changes.append(change_id)
        datasets.append(
            {
                "id": dataset_id,
                "name": f"Demo dataset {index + 1:03d}",
                "provider": {"id": provider_id, "name": provider_name},
                "category": CATEGORIES[index % len(CATEGORIES)],
                "health": health,
                "checks": checks,
                "last_checked_at": _iso(checked),
                "last_successful_at": None if health == "unknown" else _iso(checked),
                "last_healthy_at": _iso(last_healthy),
                "latest_data_at": None,
                "active_incident_ids": active,
                "latest_change_ids": latest_changes,
            }
        )
        histories.append(
            {
                "dataset_id": dataset_id,
                "requested_days": HISTORY_DAYS,
                "effective_days": HISTORY_DAYS,
                "days": _history(rng, health),
            }
        )
    return {
        "snapshot": {"generated_at": _iso(NOW)},
        "datasets": datasets,
        "incidents": incidents,
        "changes": changes,
        "histories": histories,
    }


def render_file(data: list[Any] | dict[str, Any]) -> str:
    """Serialise one fixture file; a list gets one element per line to keep diffs small."""
    if isinstance(data, list):
        body = ",\n".join("  " + json.dumps(item, ensure_ascii=False) for item in data)
        return f"[\n{body}\n]\n" if data else "[]\n"
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def directory(count: int) -> Path:
    return FIXTURES_ROOT / f"{count}-datasets"


def write(count: int) -> None:
    target = directory(count)
    target.mkdir(parents=True, exist_ok=True)
    for name, data in generate(count).items():
        (target / f"{name}.json").write_text(render_file(data), encoding="utf-8")
    ProductSnapshot.from_directory(target)  # every reference must resolve


def stale(count: int) -> list[str]:
    """The fixture files under `directory(count)` that differ from the generator."""
    target = directory(count)
    return [
        f"{count}-datasets/{name}.json"
        for name, data in generate(count).items()
        if not (target / f"{name}.json").is_file()
        or (target / f"{name}.json").read_text(encoding="utf-8") != render_file(data)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when committed files differ")
    args = parser.parse_args(argv)
    if args.check:
        problems = [path for count in SIZES for path in stale(count)]
        for path in problems:
            print(f"out of date: ui-lab/fixtures/{path}", file=sys.stderr)
        return 1 if problems else 0
    for count in SIZES:
        write(count)
        print(f"wrote {directory(count).relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
