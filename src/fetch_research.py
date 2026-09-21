"""
src/fetch_research.py
---------------------
외부 딥리서치 인풋(JSON 또는 Markdown 파일)을 로드하고 파싱하여,
정량 파이프라인(시그널 및 RCA 리포트)에 전달할 정성적 멀티플라이어 및 컨텍스트를 추출하는 모듈.
파일 부재 또는 파싱 에러 시 기본값(Multiplier 1.0)을 반환하여 파이프라인의 안전성을 보장합니다.
"""

import os
import json
from pathlib import Path

def fetch_research(data_dir="data/deep_research"):
    """
    data/deep_research 디렉토리에서 최신 딥리서치 결과 파일을 탐색하여 로드합니다.
    
    Returns:
        dict: {
            "multiplier": float (기본 1.0, 정성적 가중치 조정용),
            "summary": str (AI RCA 및 대시보드에 주입할 핵심 요약),
            "risks": list (주요 리스크 요인 리스트),
            "status": str ("success" 또는 "fallback")
        }
    """
    research_path = Path(data_dir)
    fallback_data = {
        "multiplier": 1.0,
        "summary": "외부 딥리서치 인풋이 감지되지 않았거나 파싱에 실패하여, 기존 정량 시그널 스코어를 그대로 유지합니다.",
        "risks": ["특이사항 없음 (정량 모델 단독 구동)"],
        "status": "fallback"
    }

    if not research_path.exists():
        print(f"[Fetch Research] 경고: 딥리서치 경로({data_dir})가 존재하지 않습니다. 기본값을 반환합니다.")
        return fallback_data

    # .json 파일 중 가장 최근에 수정된 파일 탐색
    json_files = list(research_path.glob("*.json"))
    if not json_files:
        print(f"[Fetch Research] 경고: {data_dir} 내에 딥리서치 JSON 파일이 없습니다. 기본값을 반환합니다.")
        return fallback_data

    latest_file = max(json_files, key=os.path.getmtime)
    
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            content = json.load(f)
            
        # 필수 키 검증 및 방어
        multiplier = float(content.get("multiplier", 1.0))
        summary = content.get("summary", "딥리서치 요약 정보가 누락되었습니다.")
        risks = content.get("risks", [])
        
        print(f"[Fetch Research] 성공: {latest_file.name} 로드 완료 (Multiplier: {multiplier})")
        return {
            "multiplier": multiplier,
            "summary": summary,
            "risks": risks,
            "status": "success"
        }
        
    except Exception as e:
        print(f"[Fetch Research] 에러: 딥리서치 파일 파싱 중 예외 발생 ({e}). 기본값으로 우회합니다.")
        return fallback_data

if __name__ == "__main__":
    # 단독 테스트 코드
    res = fetch_research()
    print("테스트 결과:", res)