from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from .models import DailyReport


def _number(value: object) -> str:
    if value is None:
        return "—"
    return f"{value:,.2f}"


def render_report(report: DailyReport) -> str:
    groups: dict[str, list[object]] = defaultdict(list)
    for snapshot in report.snapshots:
        groups[snapshot.asset.category].append(snapshot)
    environment = Environment(
        loader=PackageLoader("daily_finance_briefing", "templates"),
        autoescape=select_autoescape(["html", "xml", "j2"]),
    )
    environment.filters["number"] = _number
    return environment.get_template("daily_report.html.j2").render(report=report, groups=groups)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def write_report(report: DailyReport, output_dir: Path) -> tuple[Path, Path]:
    content = render_report(report)
    dated_path = output_dir / str(report.report_date.year) / f"{report.report_date.month:02d}" / f"{report.report_date.isoformat()}.html"
    latest_path = output_dir / "latest.html"
    _atomic_write(dated_path, content)
    _atomic_write(latest_path, content)
    return dated_path, latest_path
