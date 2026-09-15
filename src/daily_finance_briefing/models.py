from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class Asset:
    symbol: str
    name: str
    category: str
    currency: str


@dataclass(frozen=True)
class MarketSnapshot:
    asset: Asset
    status: str
    as_of_date: date | None = None
    previous_date: date | None = None
    open: Decimal | None = None
    close: Decimal | None = None
    change: Decimal | None = None
    change_percent: Decimal | None = None
    message: str | None = None


@dataclass(frozen=True)
class DailyReport:
    report_date: date
    generated_at: datetime
    snapshots: tuple[MarketSnapshot, ...]

    @property
    def failed_count(self) -> int:
        return sum(item.status == "error" for item in self.snapshots)

    @property
    def stale_count(self) -> int:
        return sum(item.status == "stale" for item in self.snapshots)
