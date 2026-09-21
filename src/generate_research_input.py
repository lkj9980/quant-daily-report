"""
src/generate_research_input.py

Gemini API를 활용하여 최신 거시경제 및 KOSPI 200 관련 딥리서치 인사이트를 생성하고,
정량 파이프라인이 즉시 로드할 수 있도록 data/deep_research/ 디렉토리에 JSON 파일로 저장하는 모듈.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

def generate_deep_research_input(output_dir="data/deep_research"):
    """
    Gemini 모델을 호출하여 시장 딥리서치 분석을 수행하고 JSON 인풋 파일을 생성합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Deep Research Gen] 경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Fallback 구조로 동작합니다.")
        return False

    genai.configure(api_key=api_key)
    
    # 모델 설정 (최신 gemini-2.5-flash 등 활용)
    model_name = "gemini-2.5-flash"
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        print(f"[Deep Research Gen] 모델 로드 실패 ({e}), 기본 모델로 전환합니다.")
        model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = """
    당신은 수석 퀀트 거시경제 애널리스트입니다.
    현재 KOSPI 200 시장 환경(금리, 환율, 반도체 및 주요 대형주 업황, 외국인 수급 등)을 분석하여 아래 JSON 포맷으로만 응답해주세요.
    마크다운 코드블록(```json 등)이나 다른 설명 텍스트 없이 오직 순수 JSON 문자열만 출력해야 합니다.

    {
        "multiplier": 1.05,
        "summary": "현재 시장 분석 핵심 요약 (2~3문장)",
        "risks": ["주요 리스크 1", "주요 리스크 2"],
        "status": "success"
    }
    
    주의사항: 
    - multiplier는 시장 상황이 매우 긍정적이면 1.05~1.10, 중립이면 1.0, 부정적이거나 리스크가 크면 0.90~0.95 사이의 float 값으로 설정하세요.
    - risks는 리스크 요인 2~3개를 문자열 리스트로 작성하세요.
    """

    try:
        print(f"[Deep Research Gen] Gemini({model_name})에 딥리서치 분석 요청 중...")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # 만약 응답에 마크다운 포맷이 포함되어 있다면 제거
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()
            raw_text = raw_text.strip("`").strip()

        research_data = json.loads(raw_text)
        
        # 데이터 정합성 검증 및 기본값 보정
        research_data.setdefault("multiplier", 1.0)
        research_data.setdefault("summary", "딥리서치 요약 정보가 정상 생성되었습니다.")
        research_data.setdefault("risks", [])
        research_data["status"] = "success"

        # 디렉토리 보장 및 저장
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = out_path / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(research_data, f, ensure_ascii=False, indent=4)
            
        print(f"[Deep Research Gen] 성공: 딥리서치 인풋 파일 생성 완료 -> {filename}")
        return True

    except Exception as e:
        print(f"[Deep Research Gen] 에러: 딥리서치 생성 또는 파싱 중 예외 발생 ({e})")
        return False

if __name__ == "__main__":
    generate_deep_research_input()