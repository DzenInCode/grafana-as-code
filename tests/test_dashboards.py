"""Validate that grafanalib definitions render to well-formed Grafana JSON."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from grafanalib._gen import DashboardEncoder

from src.dashboards import ALL_DASHBOARDS


REQUIRED_KEYS = {"title", "panels", "schemaVersion", "version"}


@pytest.mark.parametrize("dashboard", ALL_DASHBOARDS, ids=lambda d: d.title)
def test_dashboard_renders_to_valid_json(dashboard) -> None:
    payload = json.loads(json.dumps(dashboard.to_json_data(), cls=DashboardEncoder))
    assert REQUIRED_KEYS.issubset(payload.keys()), (
        f"missing keys: {REQUIRED_KEYS - payload.keys()}"
    )
    assert payload["title"] == dashboard.title
    assert isinstance(payload["panels"], list)
    assert payload["panels"], "dashboard has no panels"


@pytest.mark.parametrize("dashboard", ALL_DASHBOARDS, ids=lambda d: d.title)
def test_panel_ids_are_unique(dashboard) -> None:
    payload = json.loads(json.dumps(dashboard.to_json_data(), cls=DashboardEncoder))
    panel_ids = [p["id"] for p in payload["panels"]]
    assert len(panel_ids) == len(set(panel_ids)), f"duplicate panel ids: {panel_ids}"


def test_generate_writes_files(tmp_path: Path) -> None:
    from scripts.generate import render

    paths = render(tmp_path)
    assert len(paths) == len(ALL_DASHBOARDS)
    for path in paths:
        assert path.exists()
        json.loads(path.read_text(encoding="utf-8"))  # roundtrips
