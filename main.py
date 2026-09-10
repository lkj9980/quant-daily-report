import datetime
from src.collector import fetch_data
from src.features import build_features
from src.model import generate_signals
from src.reporter import generate_html_report

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Quant Pipeline Execution Started.")
    
    # 1. 데이터 수집 (외부 API 혹은 수집 모듈 활용)
    raw_df = fetch_data(ticker="SPY", period="2y")
    
    # 2. 피처 엔지니어링 및 저주파수 레짐 필터 통합
    features_df = build_features(raw_df)
    
    # 3. 모델 시그널 및 신뢰도 점수 생성
    signaled_df = generate_signals(features_df)
    
    # 4. 리포트 생성 (외부 마크다운 및 템플릿 파일 연동, HTML 하드코딩 없음)
    success = generate_html_report(signaled_df, now)
    
    if success:
        print(f"[{now}] Pipeline Finished Successfully and index.html generated.")
    else:
        print(f"[{now}] Pipeline Finished with Errors (Report Generation Skipped).")

if __name__ == "__main__":
    main()
