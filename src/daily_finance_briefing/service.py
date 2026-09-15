from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import pandas as pd

from .collector import Collector
from .models import Asset, DailyReport, MarketSnapshot


def _decimal(value: object) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"숫자로 변환할 수 없는 값입니다: {value}") from exc
    if not result.is_finite():
        raise ValueError(f"유효하지 않은 숫자입니다: {value}")
    return result


def create_snapshot(
    asset: Asset,
    frame: pd.DataFrame,
    cutoff_date: date,
    stale_after_days: int = 4,
) -> MarketSnapshot:
    required = {"Open", "Close"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"필수 컬럼 누락: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("조회된 데이터가 없습니다.")

    normalized = frame.copy()
    normalized.index = pd.to_datetime(normalized.index, errors="coerce")
    normalized = normalized[~normalized.index.isna()]
    normalized = normalized[normalized.index.date <= cutoff_date]
    normalized = normalized[~normalized.index.duplicated(keep="last")].sort_index()
    normalized = normalized.dropna(subset=["Open", "Close"])
    if len(normalized) < 2:
        raise ValueError("변동률 계산에 필요한 두 거래일 데이터가 없습니다.")

    previous, current = normalized.iloc[-2], normalized.iloc[-1]
    previous_close = _decimal(previous["Close"])
    current_open = _decimal(current["Open"])
    current_close = _decimal(current["Close"])
    if previous_close == 0:
        raise ValueError("직전 종가가 0이어서 등락률을 계산할 수 없습니다.")

    as_of_date = normalized.index[-1].date()
    change = current_close - previous_close
    status = "stale" if (cutoff_date - as_of_date).days > stale_after_days else "ok"
    return MarketSnapshot(
        asset=asset,
        status=status,
        as_of_date=as_of_date,
        previous_date=normalized.index[-2].date(),
        open=current_open,
        close=current_close,
        change=change,
        change_percent=(change / previous_close) * Decimal("100"),
        message="최신 데이터가 오래되었습니다." if status == "stale" else None,
    )


def build_report(
    assets: list[Asset],
    collector: Collector,
    cutoff_date: date,
    generated_at: datetime,
) -> DailyReport:
    snapshots: list[MarketSnapshot] = []
    for asset in assets:
        try:
            snapshots.append(create_snapshot(asset, collector.fetch(asset, cutoff_date), cutoff_date))
        except Exception as exc:
            snapshots.append(MarketSnapshot(asset=asset, status="error", message=str(exc)))

    successful_dates = [item.as_of_date for item in snapshots if item.as_of_date is not None]
    if not successful_dates:
        raise RuntimeError("모든 자산 데이터 수집에 실패했습니다.")
    return DailyReport(
        report_date=max(successful_dates),
        generated_at=generated_at,
        snapshots=tuple(snapshots),
    )
