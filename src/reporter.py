import os
import markdown

def generate_html_report(df, timestamp):
    """
    데이터프레임과 마크다운 내용을 취합하여 template.html을 통해 최종 index.html을 빌드합니다.
    """
    print("Compiling final dashboard report...")
    
    # 최신 데이터 요약 텍스트 구성
    latest = df.iloc[-1]
    md_content = f"""
## 📊 퀀트 파이프라인 일일 실행 결과 요약

- **분석 기준일:** {latest.get('Date', 'N/A').strftime('%Y-%m-%d') if hasattr(latest.get('Date'), 'strftime') else 'Latest'}
- **종가 (Close):** `{latest.get('Close', 0):.2f}`
- **20일 이평선:** `{latest.get('ma_20', 0):.2f}`
- **최종 시그널:** **{latest.get('signal', 'N/A')}** (신뢰도: `{latest.get('confidence', 0)*100:.1f}%`)

---

### 🔍 금일 시장 레짐 및 포지션 가이드
모델은 현재 시장의 변동성과 모멘텀 강도를 측정하여 무매매 구간(`HOLD_CASH`) 여부를 판단합니다. 상세한 백테스트 내역은 아래 로그를 참조하세요.
"""

    body_html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    template_path = "template.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        final_html = template.format(timestamp=timestamp, content=body_html)
    else:
        final_html = f"<div><small>{timestamp}</small>{body_html}</div>"
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print("index.html successfully generated!")
