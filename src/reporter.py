import os
import markdown

def generate_html_report(df, timestamp, md_filepath="report_content.md"):
    """
    외부 마크다운 파일(report_content.md)이 존재하지 않을 경우 기본 폴백 없이 즉시 중단합니다.
    """
    print("Compiling final dashboard report from external markdown template...")
    
    # 1. 외부 마크다운 파일 읽어오기 (없으면 즉시 리턴)
    if not os.path.exists(md_filepath):
        print(f"Error: External markdown file '{md_filepath}' not found. Skipping report generation.")
        return False
        
    with open(md_filepath, "r", encoding="utf-8") as f:
        raw_md = f.read()
    
    # 최신 데이터 요약 추출
    latest = df.iloc[-1] if not df.empty else {}

    # 2. 동적 데이터 바인딩 (데이터프레임 최신 값 포맷팅)
    date_str = latest.get('Date', 'N/A')
    if hasattr(date_str, 'strftime'):
        date_str = date_str.strftime('%Y-%m-%d')
        
    close_val = float(latest.get('Close', 0))
    ma20_val = float(latest.get('ma_20', 0))
    signal_val = str(latest.get('signal', 'N/A'))
    conf_val = float(latest.get('confidence', 0)) * 100

    formatted_md = raw_md.format(
        date=date_str,
        close=close_val,
        ma_20=ma20_val,
        signal=signal_val,
        confidence=conf_val
    )

    # 3. 마크다운을 HTML로 변환
    body_html = markdown.markdown(formatted_md, extensions=['tables', 'fenced_code'])
    
    # 4. template.html과 결합
    template_path = "template.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        final_html = template.format(timestamp=timestamp, content=body_html)
    else:
        print("Error: template.html not found.")
        return False
        
    # 5. 최종 index.html 저장
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print("index.html successfully generated using external markdown content!")
    return True
