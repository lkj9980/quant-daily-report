import datetime
from src.collector import fetch_data
from src.features import build_features
from src.model import generate_signals
from src.backtest import run_walk_forward_backtest
from src.ai_rca import generate_rca_report
from src.reporter import generate_html_report

def main():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Quant Pipeline Execution Started.")
    
    # 1. 데이터 수집
    #raw_df = fetch_data(ticker="SPY", period="2y")
    # 원하는 종목 심볼을 전달합니다 ("NASDAQ100", "KOSPI200", "KOSDAQ150" 또는 야후파이낸스 티커)
    #raw_df = fetch_data(ticker="KOSPI200", period="2y")
    print("--- Testing fetch_data Module ---")
    sample_df = fetch_data(ticker="KOSPI200", period="6mo")
    print(sample_df.tail())
    
    # 2. 피처 엔지니어링 및 레짐 필터 통합
    features_df = build_features(sample_df)
    
    # 3. 모델 시그널 및 신뢰도 점수 생성
    signaled_df = generate_signals(features_df)
    
    # 4. 백테스트 수치 검증 엔진 실행
    backtest_metrics = run_walk_forward_backtest(signaled_df)
    
    # 5. AI RCA 진단 엔진 호출 (중앙 경로 설정 활용)
    rca_briefing = generate_rca_report(backtest_metrics)
    print(rca_briefing)
    
    # 6. 리포트 생성 및 history 아카이브 (rca_briefing 전달)
    success = generate_html_report(signaled_df, now, rca_briefing=rca_briefing)
    
    if success:
        print(f"[{now}] Pipeline Finished Successfully and index.html generated.")
    else:
        print(f"[{now}] Pipeline Finished with Errors (Report Generation Skipped).")

if __name__ == "__main__":
    main()
