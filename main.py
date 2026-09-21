"""
main.py

KOSPI 200 Quant Intelligence Pipeline의 6단계 통합 마스터 실행 스크립트.
1. 야후 파이낸스 데이터 수집 (fetch_data)
2. 기술적 지표 및 레짐 필터 빌드 (build_features)
3. 딥리서치 인풋 로드 및 밴드 리밸런싱 시그널 생성 (fetch_research & generate_signals)
4. 워크포워드 백테스트 수행 (run_backtest)
5. AI RCA 진단 및 HTML 리포트 조립 (generate_rca_report)
"""

import sys
from pathlib import Path

# src 패키지 임포트 경로 보장
sys.path.append(str(Path(__file__).parent / "src"))

from fetch_data import fetch_data
from build_features import build_features
from fetch_research import fetch_research
from generate_signals import generate_signals
from run_backtest import run_walk_forward_backtest
from generate_rca_report import generate_rca_report, generate_html_report

def main():
    print("=" * 60)
    print("🚀 KOSPI 200 Quant Intelligence Pipeline 시작")
    print("=" * 60)

    try:
        # [1단계] 야후 파이낸스 데이터 수집 (정량 시세 및 펀더멘털)
        print("\n[Stage 1/6] 야후 파이낸스 데이터 수집 중...")
        df = fetch_data()
        if df is None or df.empty:
            raise ValueError("데이터 수집 실패: 빈 데이터프레임이 반환되었습니다.")

        # [2단계] 기술적 지표 산출 및 레짐 필터 적용
        print("\n[Stage 2/6] 기술적 지표 및 레짐 필터 빌드 중...")
        features_df = build_features(df)

        # [3단계] 딥리서치 인풋 로드 및 시그널 생성 (정성적 멀티플라이어 반영)
        print("\n[Stage 3/6] 외부 딥리서치 인풋 로드 및 밴드 리밸런싱 시그널 생성 중...")
        research_context = fetch_research()
        signals_df = generate_signals(features_df, research_context=research_context)

        # [4단계] 워크포워드 백테스트 엔진 구동
        print("\n[Stage 4/6] 워크포워드 백테스트 성과 측정 중...")
        backtest_results = run_walk_forward_backtest(signals_df)

        # [5단계] AI RCA 진단 브리핑 생성
        print("\n[Stage 5/6] AI RCA 진단 브리핑 생성 중...")
        rca_briefing = generate_rca_report(backtest_results, research_context)

        # [6단계] HTML 리포트 카드 조립 및 아카이브 저장
        print("\n[Stage 6/6] 최종 HTML 리포트 카드 조립 및 동기화 중...")
        generate_html_report(backtest_results, rca_briefing, research_context)

        print("\n" + "=" * 60)
        print("🎉 KOSPI 200 퀀트 인텔리전스 파이프라인이 성공적으로 완료되었습니다!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ [Pipeline Error] 파이프라인 실행 중 치명적인 예외 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()