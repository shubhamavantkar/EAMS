from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from eams.models.events import ReportSummary


def render_html(summary: ReportSummary, templates_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("daily_report.html.j2")
    return template.render(summary=summary, top_apps=list(summary.app_usage_seconds.items())[:10])
