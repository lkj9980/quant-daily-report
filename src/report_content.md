## 📊 퀀트 파이프라인 일일 실행 결과 요약

- **분석 기준일:** {latest.get('Date', 'N/A').strftime('%Y-%m-%d') if hasattr(latest.get('Date'), 'strftime') else 'Latest'}
- **종가 (Close):** `{latest.get('Close', 0):.2f}`
- **20일 이평선:** `{latest.get('ma_20', 0):.2f}`
- **최종 시그널:** **{latest.get('signal', 'N/A')}** (신뢰도: `{latest.get('confidence', 0)*100:.1f}%`)

### 🔍 금일 시장 레짐 및 포지션 가이드
모델은 현재 시장의 변동성과 모멘텀 강도를 측정하여 무매매 구간(`HOLD_CASH`) 여부를 판단합니다. 상세한 백테스트 내역은 아래 로그를 참조하세요.
