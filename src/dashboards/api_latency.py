"""API latency dashboard — example pattern for request-path observability."""
from __future__ import annotations

from grafanalib.core import (
    SECONDS_FORMAT,
    Dashboard,
    GridPos,
    Graph,
    Stat,
    Target,
    Time,
    single_y_axis,
)

DATASOURCE = "Prometheus"

p95_latency = Stat(
    title="p95 latency (last 5m)",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr="histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))",
            legendFormat="p95",
        ),
    ],
    format=SECONDS_FORMAT,
    reduceCalc="lastNotNull",
    thresholds=[
        {"color": "green", "value": None},
        {"color": "yellow", "value": 0.3},
        {"color": "red", "value": 1.0},
    ],
    gridPos=GridPos(h=6, w=12, x=0, y=0),
)

error_rate = Stat(
    title="Error rate (last 5m)",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr=(
                'sum(rate(http_requests_total{status=~"5.."}[5m])) '
                '/ sum(rate(http_requests_total[5m]))'
            ),
            legendFormat="errors",
        ),
    ],
    format="percentunit",
    reduceCalc="lastNotNull",
    thresholds=[
        {"color": "green", "value": None},
        {"color": "red", "value": 0.01},
    ],
    gridPos=GridPos(h=6, w=12, x=12, y=0),
)

latency_quantiles = Graph(
    title="Latency quantiles",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr="histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))",
            legendFormat="p50",
        ),
        Target(
            expr="histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))",
            legendFormat="p95",
        ),
        Target(
            expr="histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))",
            legendFormat="p99",
        ),
    ],
    yAxes=single_y_axis(format="s"),
    gridPos=GridPos(h=8, w=24, x=0, y=6),
)

requests_by_status = Graph(
    title="Requests by status",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr="sum by (status) (rate(http_requests_total[5m]))",
            legendFormat="{{status}}",
        ),
    ],
    yAxes=single_y_axis(format="reqps"),
    gridPos=GridPos(h=8, w=24, x=0, y=14),
)

dashboard = Dashboard(
    title="API Latency",
    description="p50/p95/p99 latency, error rate, requests by status code.",
    tags=["api", "latency", "as-code"],
    timezone="browser",
    refresh="30s",
    time=Time("now-1h", "now"),
    panels=[p95_latency, error_rate, latency_quantiles, requests_by_status],
).auto_panel_ids()
