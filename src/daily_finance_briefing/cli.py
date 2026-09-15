from __future__ import annotations

import argparse
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .collector import FinanceDataReaderCollector
from .config import load_assets
from .report import write_report
from .service import build_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="일일 금융시장 HTML 보고서를 생성합니다.")
    parser.add_argument("--date", type=date.fromisoformat, help="데이터 조회 종료일(YYYY-MM-DD), 기본값은 KST 기준 전일")
    parser.add_argument("--config", type=Path, default=Path("config/assets.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    parser.add_argument("--timezone", default="Asia/Seoul")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args(argv)
    try:
        timezone = ZoneInfo(args.timezone)
        generated_at = datetime.now(timezone)
        cutoff_date = args.date or (generated_at.date() - timedelta(days=1))
        assets = load_assets(args.config)
        report = build_report(assets, FinanceDataReaderCollector(), cutoff_date, generated_at)
        dated_path, latest_path = write_report(report, args.output_dir)
    except Exception:
        logging.exception("보고서 생성에 실패했습니다.")
        return 1

    logging.info(
        "보고서 생성 완료: date=%s assets=%d failed=%d stale=%d path=%s latest=%s",
        report.report_date,
        len(report.snapshots),
        report.failed_count,
        report.stale_count,
        dated_path,
        latest_path,
    )
    return 0
