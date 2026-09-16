import os

# 프로젝트 루트 디렉토리 기준 고정 (유지보수 시 경로 변경은 오직 이 파일에서만 수행)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모든 파일 및 폴더 경로를 한 곳에서 총괄 관리 (함수 뒤질 필요 없음)
PATHS = {
    "template_html": os.path.join(BASE_DIR, "html", "template.html"),
    "report_content_md": os.path.join(BASE_DIR, "html", "report_content.md"),
    "rca_prompt_txt": os.path.join(BASE_DIR, "html", "rca_prompt_template.txt"),
    "processed_data": os.path.join(BASE_DIR, "data", "processed_data.csv"),
    "history_dir": os.path.join(BASE_DIR, "history"),
    "output_html": os.path.join(BASE_DIR, "index.html")
}
