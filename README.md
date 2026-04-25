# grafana-as-code

Grafana dashboards defined as **Python code** (via [`grafanalib`](https://github.com/weaveworks/grafanalib)), rendered to JSON, and auto-loaded into Grafana on container start. Includes a working Prometheus + node_exporter stack so you can `docker compose up` and see real metrics in 30 seconds.

> **Why this matters.** Hand-edited dashboards live in Grafana's database — version-uncontrolled, hard to review, easy to lose. With this setup every dashboard change is a Python diff, reviewed in a PR, validated in CI, and applied by restarting Grafana.

## What's inside

```
grafana-as-code/
├── docker-compose.yml         # Grafana + Prometheus + node_exporter
├── prometheus/prometheus.yml  # scrape config
├── grafana/provisioning/      # auto-load datasource + dashboards on start
│   ├── datasources/prometheus.yml
│   └── dashboards/default.yml
├── src/dashboards/            # Python source for each dashboard
│   ├── system_overview.py
│   └── api_latency.py
├── dashboards/                # generated JSON (committed; consumed by Grafana)
├── scripts/generate.py        # render src/dashboards/*.py → dashboards/*.json
├── tests/test_dashboards.py   # validate JSON output
└── Makefile                   # install / generate / test / up / down
```

## Quickstart

```bash
git clone https://github.com/DzenInCode/grafana-as-code
cd grafana-as-code
make install      # pip install -e ".[dev]"
make generate     # render Python → dashboards/*.json
make up           # docker compose up -d
```

Open **http://localhost:3000** (admin / admin). You'll see two dashboards in the home folder:
- **System Overview** — CPU / memory / disk / network from node_exporter
- **API Latency** — p50/p95/p99, error rate, requests by status (template — needs an HTTP exporter)

## How it works

```
┌──────────────────────┐      ┌─────────────────────┐      ┌──────────┐
│ src/dashboards/*.py  │ ──▶  │ scripts/generate.py │ ──▶  │ JSON     │
│ (grafanalib DSL)     │      │ (renders to JSON)   │      │ files    │
└──────────────────────┘      └─────────────────────┘      └────┬─────┘
                                                                │ mount
                                                                ▼
                            ┌──────────────────────────┐  ┌─────────────┐
                            │ grafana/provisioning/    │──▶│ Grafana    │
                            │ dashboards/default.yml   │  │ auto-loads │
                            └──────────────────────────┘  └─────────────┘
```

CI runs `generate.py` and fails if `dashboards/` doesn't match `src/dashboards/` — so the committed JSON can never drift from the source.

## Editing dashboards

1. Open `src/dashboards/system_overview.py` (or add a new file)
2. Change a panel, query, or threshold
3. `make generate` — JSON is regenerated under `dashboards/`
4. `make test` — validates structure
5. Commit both the `.py` and `.json` changes
6. Restart Grafana (`docker compose restart grafana`) — new dashboards auto-load

## Adding a new dashboard

```python
# src/dashboards/redis.py
from grafanalib.core import Dashboard, Graph, Target, GridPos

dashboard = Dashboard(
    title="Redis",
    panels=[
        Graph(
            title="Connected clients",
            dataSource="Prometheus",
            targets=[Target(expr="redis_connected_clients", legendFormat="{{instance}}")],
            gridPos=GridPos(h=8, w=24, x=0, y=0),
        ),
    ],
).auto_panel_ids()
```

Then add it to `src/dashboards/__init__.py`:

```python
from src.dashboards.redis import dashboard as redis
ALL_DASHBOARDS = [system_overview, api_latency, redis]
```

`make generate && make test && docker compose restart grafana` — done.

## Stack

| Layer | Technology |
|---|---|
| Dashboard DSL | [`grafanalib`](https://github.com/weaveworks/grafanalib) |
| Datasource | Prometheus 2.54 |
| Sample exporter | node_exporter 1.8 |
| Visualization | Grafana 11.2 |
| Orchestration | Docker Compose |
| Tests | pytest |

## Tests

```bash
make test
```

Validates that every dashboard:
- Renders to valid JSON
- Has the required Grafana keys (`title`, `panels`, `schemaVersion`, `version`)
- Has unique panel IDs

## Limitations

- **Anonymous viewer access enabled** — for development only. Set `GF_AUTH_ANONYMOUS_ENABLED=false` and use proper auth in production.
- **No persistent volume for Grafana** — restarts wipe Grafana's internal state (alerts, ad-hoc folders). Add a named volume on `/var/lib/grafana` for production.
- **`api_latency.py` is a template** — it needs an actual HTTP service exporting `http_request_duration_seconds_bucket` and `http_requests_total`. Point it at your service.
- **No alerting rules** — extend `prometheus/` with `rules/*.yml` and reference them in `prometheus.yml`.

## License

MIT — see [LICENSE](LICENSE).
