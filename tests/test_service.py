from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from daily_finance_briefing.models import Asset
from daily_finance_briefing.service import build_report, create_snapshot


ASSET = Asset("TEST", "테스트 <지수>", "국내 주가지수", "KRW")


def frame() -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [100, 105, 120], "Close": [105, 110, 130]},
        index=pd.to_datetime(["2026-09-11", "2026-09-14", "2026-09-15"]),
    )


def test_snapshot_uses_only_rows_through_cutoff() -> None:
    snapshot = create_snapshot(ASSET, frame(), date(2026, 9, 14))

    assert snapshot.as_of_date == date(2026, 9, 14)
    assert snapshot.previous_date == date(2026, 9, 11)
    assert snapshot.open == Decimal("105")
    assert snapshot.change == Decimal("5")
    assert snapshot.change_percent == Decimal("100") / Decimal("21")


def test_snapshot_rejects_missing_columns() -> None:
    with pytest.raises(ValueError, match="Close"):
        create_snapshot(ASSET, pd.DataFrame({"Open": [1, 2]}), date(2026, 9, 14))


class StubCollector:
    def fetch(self, asset: Asset, end_date: date) -> pd.DataFrame:
        if asset.symbol == "FAIL":
            raise ConnectionError("provider unavailable")
        return frame()


def test_report_keeps_partial_failures() -> None:
    failed = Asset("FAIL", "실패", "해외 주가지수", "USD")
    report = build_report(
        [ASSET, failed],
        StubCollector(),
        date(2026, 9, 14),
        datetime(2026, 9, 15, 10, tzinfo=ZoneInfo("Asia/Seoul")),
    )

    assert report.report_date == date(2026, 9, 14)
    assert report.failed_count == 1
    assert report.snapshots[1].status == "error"


def test_report_fails_when_all_assets_fail() -> None:
    failed = Asset("FAIL", "실패", "해외 주가지수", "USD")
    with pytest.raises(RuntimeError, match="모든 자산"):
        build_report(
            [failed],
            StubCollector(),
            date(2026, 9, 14),
            datetime(2026, 9, 15, 10, tzinfo=ZoneInfo("Asia/Seoul")),
        )
