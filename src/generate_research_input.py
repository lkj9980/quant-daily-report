"""
src/generate_research_input.py

Gemini API의 웹 검색(Search Grounding) 기능을 활성화하여,
실시간 KOSPI 200 거시경제, 외국인/기관 수급, 환율 및 반도체 업황 최신 이슈를 딥리서치하고
정량 파이프라인이 즉시 로드할 수 있도록 data/deep_research/ 디렉토리에 JSON 파일로 저장하는 모듈.
외부로 격리된 프롬프트 템플릿(templates/deep_research_prompt_template.txt)을 읽어와 사용합니다.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

def load_prompt_template(template_path="templates/deep_research_prompt_template.txt"):
    """
    templates/ 디렉토리에 격리된 프롬프트 템플릿 파일을 읽어옵니다.
    """
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"[Deep Research Gen] 에러: 프롬프트 템플릿을 찾을 수 없습니다 -> {template_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_deep_research_input(output_dir="data/deep_research", template_path="templates/deep_research_prompt_template.txt"):
    """
    Gemini 모델에 Search Grounding 툴을 부여하여 실시간 딥리서치 분석을 수행하고 JSON 인풋 파일을 생성합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[Deep Research Gen] 경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. Fallback 구조로 동작합니다.")
        return False

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"

    try:
        # 외부 격리된 프롬프트 템플릿 로드
        prompt = load_prompt_template(template_path)
    except Exception as e:
        print(f"[Deep Research Gen] 에러: {e}")
        return False

    try:
        print(f"[Deep Research Gen] Gemini({model_name}) + Search Grounding을 통한 실시간 딥리서치 수행 중...")
        
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[{"google_search": {}}],  # 실시간 웹 검색 그라운딩 활성화
                temperature=0.2,
            )
        )
        
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

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = out_path / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(research_data, f, ensure_ascii=False, indent=4)
            
        print(f"[Deep Research Gen] 성공: 실시간 딥리서치 인풋 파일 생성 완료 -> {filename}")
        return True

    except Exception as e:
        print(f"[Deep Research Gen] 에러: 딥리서치 생성 또는 파싱 중 예외 발생 ({e})")
        return False

if __name__ == "__main__":
    generate_deep_research_input()