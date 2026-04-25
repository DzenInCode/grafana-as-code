"""Dashboard definitions — one Dashboard object per file."""

from src.dashboards.api_latency import dashboard as api_latency
from src.dashboards.system_overview import dashboard as system_overview

ALL_DASHBOARDS = [system_overview, api_latency]
