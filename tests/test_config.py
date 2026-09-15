from pathlib import Path

import pytest

from daily_finance_briefing.config import load_assets


def test_load_assets(tmp_path: Path) -> None:
    config = tmp_path / "assets.yaml"
    config.write_text(
        "assets:\n  - symbol: TEST\n    name: 테스트\n    category: 지수\n    currency: KRW\n",
        encoding="utf-8",
    )

    assets = load_assets(config)

    assert assets[0].symbol == "TEST"


def test_duplicate_symbols_are_rejected(tmp_path: Path) -> None:
    config = tmp_path / "assets.yaml"
    config.write_text(
        "assets:\n"
        "  - {symbol: TEST, name: 하나, category: 지수, currency: KRW}\n"
        "  - {symbol: TEST, name: 둘, category: 지수, currency: KRW}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="중복"):
        load_assets(config)


def test_default_assets_include_japanese_stock_market() -> None:
    assets = load_assets(Path("config/assets.yaml"))

    nikkei = next(asset for asset in assets if asset.symbol == "N225")
    assert nikkei.name == "닛케이 225"
    assert nikkei.category == "해외 주가지수"
    assert nikkei.currency == "JPY"
