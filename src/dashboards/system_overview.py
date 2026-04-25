"""System overview dashboard — CPU, memory, disk, network from node_exporter."""
from __future__ import annotations

from grafanalib.core import (
    PERCENT_FORMAT,
    Dashboard,
    GridPos,
    Graph,
    Stat,
    Target,
    Templating,
    Template,
    Time,
    single_y_axis,
)

DATASOURCE = "Prometheus"

cpu_usage = Stat(
    title="CPU usage",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr='100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
            legendFormat="{{instance}}",
        ),
    ],
    format=PERCENT_FORMAT,
    reduceCalc="lastNotNull",
    gridPos=GridPos(h=8, w=8, x=0, y=0),
)

memory_usage = Stat(
    title="Memory usage",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr="(1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100",
            legendFormat="{{instance}}",
        ),
    ],
    format=PERCENT_FORMAT,
    reduceCalc="lastNotNull",
    gridPos=GridPos(h=8, w=8, x=8, y=0),
)

disk_usage = Stat(
    title="Disk usage (root)",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr=(
                '(1 - node_filesystem_avail_bytes{mountpoint="/",fstype!="rootfs"} '
                '/ node_filesystem_size_bytes{mountpoint="/",fstype!="rootfs"}) * 100'
            ),
            legendFormat="{{instance}}",
        ),
    ],
    format=PERCENT_FORMAT,
    reduceCalc="lastNotNull",
    gridPos=GridPos(h=8, w=8, x=16, y=0),
)

network_io = Graph(
    title="Network I/O",
    dataSource=DATASOURCE,
    targets=[
        Target(
            expr='rate(node_network_receive_bytes_total{device!~"lo|veth.*"}[5m])',
            legendFormat="{{device}} rx",
        ),
        Target(
            expr='rate(node_network_transmit_bytes_total{device!~"lo|veth.*"}[5m])',
            legendFormat="{{device}} tx",
        ),
    ],
    yAxes=single_y_axis(format="Bps"),
    gridPos=GridPos(h=8, w=24, x=0, y=8),
)

dashboard = Dashboard(
    title="System Overview",
    description="CPU / memory / disk / network from node_exporter.",
    tags=["system", "node-exporter", "as-code"],
    timezone="browser",
    refresh="30s",
    time=Time("now-1h", "now"),
    templating=Templating(
        list=[
            Template(
                name="instance",
                label="Instance",
                dataSource=DATASOURCE,
                query="label_values(node_uname_info, instance)",
                includeAll=True,
                multi=True,
                refresh=1,
                type="query",
            ),
        ]
    ),
    panels=[cpu_usage, memory_usage, disk_usage, network_io],
).auto_panel_ids()
