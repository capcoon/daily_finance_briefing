from __future__ import annotations

from pathlib import Path

import yaml

from .models import Asset


def load_assets(path: Path) -> list[Asset]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = raw.get("assets")
    if not isinstance(entries, list) or not entries:
        raise ValueError("설정 파일에 하나 이상의 assets 항목이 필요합니다.")

    assets: list[Asset] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("각 assets 항목은 객체여야 합니다.")
        try:
            asset = Asset(
                symbol=str(entry["symbol"]).strip(),
                name=str(entry["name"]).strip(),
                category=str(entry["category"]).strip(),
                currency=str(entry["currency"]).strip(),
            )
        except KeyError as exc:
            raise ValueError(f"자산 설정 필드가 누락되었습니다: {exc.args[0]}") from exc
        if not all((asset.symbol, asset.name, asset.category, asset.currency)):
            raise ValueError("자산 설정 필드는 비어 있을 수 없습니다.")
        if asset.symbol in seen:
            raise ValueError(f"중복된 자산 심볼입니다: {asset.symbol}")
        seen.add(asset.symbol)
        assets.append(asset)
    return assets
