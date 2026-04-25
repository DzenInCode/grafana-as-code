"""Render grafanalib Dashboard objects to JSON files for Grafana provisioning."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from grafanalib._gen import DashboardEncoder  # noqa: E402

from src.dashboards import ALL_DASHBOARDS  # noqa: E402

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT = REPO_ROOT / "dashboards"


def render(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for dashboard in ALL_DASHBOARDS:
        slug = dashboard.title.lower().replace(" ", "-")
        path = output_dir / f"{slug}.json"
        path.write_text(
            json.dumps(
                dashboard.to_json_data(),
                cls=DashboardEncoder,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        logger.info("wrote %s", path)
        written.append(path)
    return written


def main() -> None:
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Directory to write dashboard JSON files (default: ./dashboards).",
    )
    args = parser.parse_args()
    paths = render(Path(args.output))
    print(f"Generated {len(paths)} dashboard(s): {[p.name for p in paths]}")


if __name__ == "__main__":
    sys.exit(main())
