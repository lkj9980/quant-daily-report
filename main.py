import datetime
from src.collector import fetch_data
from src.features import build_features
from src.model import generate_signals
from src.reporter import generate_html_report
from src.backtest import run_walk_forward_backtest
from src.ai_rca import generate_rca_report

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Quant Pipeline Execution Started.")
    
    # 1. 데이터 수집 (외부 API 혹은 수집 모듈 활용)
    raw_df = fetch_data(ticker="SPY", period="2y")
    
    # 2. 피처 엔지니어링 및 저주파수 레짐 필터 통합
    features_df = build_features(raw_df)
    
    # 3. 모델 시그널 및 신뢰도 점수 생성
    signaled_df = generate_signals(features_df)
    
    # 4. 백테스트 수치 검증 엔진 실행 (Sharpe, MDD, 승률 계산)
    backtest_metrics = run_walk_forward_backtest(signaled_df)
    
    # 5. AI RCA 진단 엔진 호출 (백테스트 지표와 외부 프롬프트 템플릿 결합)
    rca_briefing = generate_rca_report(backtest_metrics, prompt_template_path="html/rca_prompt_template.txt")
    print(rca_briefing)
    
    # 6. 리포트 생성 및 history 아카이브 (index.html 및 history/ 날짜별 백업)
    success = generate_html_report(signaled_df, now)
    
    if success:
        print(f"[{now}] Pipeline Finished Successfully and index.html generated.")
    else:
        print(f"[{now}] Pipeline Finished with Errors (Report Generation Skipped).")

if __name__ == "__main__":
    main()
