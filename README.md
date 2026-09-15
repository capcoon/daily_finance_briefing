# Daily Finance Briefing

FinanceDataReader로 주요 국내외 주가지수, 외환 및 원자재의 최근 완료 거래일 정보를 수집해 독립 실행형 HTML 보고서를 생성합니다.

## 보고서 기준

- 예약 실행 시각은 매일 오전 10시 KST(UTC 01:00)입니다.
- 기본 조회 종료일은 실행 시각의 KST 기준 전일입니다.
- 달력상 전일을 거래일로 가정하지 않고, 각 자산에서 조회된 마지막 두 유효 거래일을 사용합니다.
- 시가와 종가는 최근 유효 거래일 값이며 변동은 `최근 종가 - 직전 종가`, 등락률은 `(최근 종가 / 직전 종가 - 1) × 100`입니다.
- 일부 종목 조회가 실패해도 보고서를 생성하고 오류를 해당 행에 표시합니다. 모든 종목이 실패하면 실행도 실패합니다.

기본 심볼은 [`config/assets.yaml`](config/assets.yaml)에 있습니다. 원자재 등 일부 심볼은 FinanceDataReader가 사용하는 외부 제공처의 정책에 따라 달라질 수 있으므로 운영 전 실제 조회 여부를 확인하세요.

## 설치 및 실행

Python 3.11 이상이 필요합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
python -m daily_finance_briefing
```

기본 결과는 다음 위치에 기록됩니다.

```text
reports/
├── latest.html
└── YYYY/
    └── MM/
        └── YYYY-MM-DD.html
```

조회 종료일, 설정 및 출력 위치를 지정할 수 있습니다.

```bash
python -m daily_finance_briefing \
  --date 2026-09-14 \
  --config config/assets.yaml \
  --output-dir reports \
  --timezone Asia/Seoul
```

## GitHub Actions

`.github/workflows/daily-report.yml`은 다음 경우에 실행됩니다.

- 매일 `01:00 UTC`, 즉 `10:00 KST`
- Actions 화면에서 수동 실행

GitHub 예약 작업은 정각 실행을 보장하지 않으므로 몇 분 이상 지연될 수 있습니다. workflow는 생성된 `reports/` 변경분만 `github-actions[bot]` 이름으로 현재 브랜치에 커밋합니다. 동일한 보고서가 이미 있으면 빈 커밋을 생성하지 않습니다.

자동 커밋에는 workflow의 `contents: write` 권한과 저장소 설정에서 Actions의 쓰기 허용이 필요합니다. 보호 브랜치가 직접 push를 차단한다면 보고서 전용 브랜치 또는 GitHub Pages artifact 배포 방식으로 바꿔야 합니다. 자동화에서는 강제 push를 사용하지 않습니다.

수동 실행 시 `report_date`에 `YYYY-MM-DD` 값을 넣어 과거 보고서를 다시 생성할 수 있습니다.

## 테스트

```bash
pytest
```

단위 테스트는 외부 금융 제공처를 호출하지 않습니다. 실제 심볼과 네트워크 상태 확인은 별도의 운영 전 점검으로 수행해야 합니다.

## 운영 시 유의사항

- 시장마다 휴장일이 달라 보고서의 대표 기준일과 개별 자산 기준일이 다를 수 있습니다.
- 조회 종료일보다 데이터가 4일 넘게 오래되면 해당 행을 `지연` 상태로 표시합니다.
- Git에 HTML을 장기간 누적하면 저장소가 커지므로 보존 기간이나 GitHub Pages·외부 스토리지 전환을 검토하세요.
- 데이터 제공처의 이용 및 재배포 조건을 확인하세요.
- 이 보고서는 참고용이며 투자 조언이 아닙니다.
