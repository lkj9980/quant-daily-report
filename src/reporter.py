import os
import markdown

def generate_html_report(df, timestamp):
    # html/ 폴더 안의 파일들을 안전하게 타겟팅
    md_filepath = os.path.join("html", "report_content.md")
    template_path = os.path.join("html", "template.html")
    
    if not os.path.exists(md_filepath) or not os.path.exists(template_path):
        print("Error: Required files in 'html/' folder not found.")
        return False
        
    with open(md_filepath, "r", encoding="utf-8") as f:
        raw_md = f.read()
        
    # 데이터 바인딩 및 변환 로직 수행...
    # (최종 index.html은 GitHub Pages 배포를 위해 반드시 루트 최상단에 생성됩니다)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
        
    return True
    
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
