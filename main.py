import os
import datetime
import markdown
from src.collector import fetch_data
from src.features import build_features
from src.model import generate_signals
from src.reporter import generate_html_report

def main():
    print("1. 데이터 수집 중...")
    # raw_data = fetch_data()
    
    print("2. 인풋 피처 및 레짐 필터 적용 중...")
    # features = build_features(...)
    
    print("3. 아웃풋 확률 분포 및 신뢰도 검사 중...")
    # signals = generate_signals(...)
    
    print("4. 일일 퀀트 리포트 HTML 생성 완료.")
    # generate_dashboard(signals)
    generate_dashboard()
    

def read_markdown_content():
    # 마크다운 소스 파일을 읽어옵니다. (없으면 기본 텍스트 반환)
    md_path = "report_content.md"
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return "# 🚀 일일 퀀트 리포트\n\n- report_content.md 파일을 찾을 수 없습니다."

def generate_dashboard():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 1. 순수 마크다운 콘텐츠 로드
    md_text = read_markdown_content()
    
    # 2. 마크다운을 HTML로 변환 (파이썬 코드 내에 HTML 텍스트를 직접 하드코딩하지 않음)
    body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    
    # 3. 외부 전용 뼈대(Template) 파일이 있다면 로드하여 변환 수행
    template_path = "template.html"
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        final_html = template.format(timestamp=now, content=body_html)
    else:
        # 템플릿도 없다면 마크다운 변환 결과만 단독 저장
        final_html = f"<div><small>{now}</small>{body_html}</div>"
    
    # 최종 index.html 배포 파일 쓰기
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print("HTML 하드코딩 없이 마크다운 및 템플릿 연동으로 index.html 생성 완료!")

if __name__ == "__main__":
    main()
