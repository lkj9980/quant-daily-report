import os
import markdown

def read_markdown_content(md_filepath=os.path.join("html", "report_content.md")):
    """
    외부 마크다운 파일을 읽어옵니다. 없으면 None을 반환합니다.
    """
    if not os.path.exists(md_filepath):
        print(f"Error: External markdown file '{md_filepath}' not found.")
        return None
        
    with open(md_filepath, "r", encoding="utf-8") as f:
        return f.read()

def generate_html_report(df, timestamp, md_filepath=os.path.join("html", "report_content.md")):
    """
    데이터프레임 최신 값을 마크다운 템플릿에 바인딩하고 HTML 대시보드로 컴파일합니다.
    history/ 폴더에 날짜별 아카이브 백업을 자동으로 생성합니다.
    """
    print("Compiling final dashboard report from external markdown template...")
    
    # 1. 외부 마크다운 파일 읽어오기
    raw_md = read_markdown_content(md_filepath)
    if raw_md is None:
        return False
        
    latest = df.iloc[-1] if not df.empty else {}

    # 2. 데이터 포맷팅 및 바인딩
    date_val = latest.get('Date', 'N/A')
    if hasattr(date_val, 'strftime'):
        date_str = date_val.strftime('%Y-%m-%d')
    else:
        date_str = str(date_val)
        
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
    
    # 4. 외부 template.html과 결합
    template_path = os.path.join("html", "template.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        final_html = template.format(timestamp=timestamp, content=body_html)
    else:
        print("Error: template.html not found in html/ directory.")
        return False
        
    # 5. 최종 index.html 저장 (루트 최상단)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
        
    # 6. history/ 폴더에 날짜별 아카이브 백업 생성 (자동 아카이빙)
    history_dir = "history"
    os.makedirs(history_dir, exist_ok=True)
    archive_filename = f"{date_str}_report.html"
    archive_path = os.path.join(history_dir, archive_filename)
    
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(final_html)
    print(f"Archived a copy of the report to {archive_path}")
        
    print("index.html successfully generated and compiled!")
    return True
