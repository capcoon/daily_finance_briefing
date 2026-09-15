from __future__ import annotations

import time
from datetime import date, timedelta
from typing import Protocol

import FinanceDataReader as fdr
import pandas as pd

from .models import Asset


class Collector(Protocol):
    def fetch(self, asset: Asset, end_date: date) -> pd.DataFrame: ...


class FinanceDataReaderCollector:
    def __init__(self, lookback_days: int = 14, retries: int = 3) -> None:
        self.lookback_days = lookback_days
        self.retries = retries

    def fetch(self, asset: Asset, end_date: date) -> pd.DataFrame:
        start_date = end_date - timedelta(days=self.lookback_days)
        error: Exception | None = None
        for attempt in range(self.retries):
            try:
                return fdr.DataReader(
                    asset.symbol,
                    start_date.isoformat(),
                    (end_date + timedelta(days=1)).isoformat(),
                )
            except Exception as exc:  # 외부 제공처의 오류 유형은 일관적이지 않다.
                error = exc
                if attempt + 1 < self.retries:
                    time.sleep(2**attempt)
        assert error is not None
        raise error
