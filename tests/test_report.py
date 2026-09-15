from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_finance_briefing.models import Asset, DailyReport, MarketSnapshot
from daily_finance_briefing.report import render_report, write_report


def sample_report() -> DailyReport:
    asset = Asset("TEST", "테스트 <지수>", "국내 주가지수", "KRW")
    snapshot = MarketSnapshot(
        asset=asset,
        status="ok",
        as_of_date=date(2026, 9, 14),
        previous_date=date(2026, 9, 11),
        open=Decimal("100"),
        close=Decimal("105"),
        change=Decimal("5"),
        change_percent=Decimal("5"),
    )
    return DailyReport(
        report_date=date(2026, 9, 14),
        generated_at=datetime(2026, 9, 15, 10, tzinfo=ZoneInfo("Asia/Seoul")),
        snapshots=(snapshot,),
    )


def test_render_report_escapes_asset_name() -> None:
    html = render_report(sample_report())

    assert "테스트 &lt;지수&gt;" in html
    assert "+5.00%" in html


def test_write_report_creates_dated_and_latest_files(tmp_path: Path) -> None:
    dated, latest = write_report(sample_report(), tmp_path)

    assert dated == tmp_path / "2026" / "09" / "2026-09-14.html"
    assert dated.read_text(encoding="utf-8") == latest.read_text(encoding="utf-8")
