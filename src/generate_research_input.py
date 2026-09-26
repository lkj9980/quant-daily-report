"""
src/generate_research_input.py

DuckDuckGo와 BeautifulSoup을 활용한 외부 설정 파일 기반 다중 검색어 딥리서치 인풋 생성 모듈.
config/research_queries.json에서 쿼리 리스트를 동적으로 로드하여 순차 탐색합니다.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from google import genai

# 공통 유틸리티 임포트
from utils import call_gemini_with_retry
from config import DEEP_RESEARCH_MODEL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def load_research_queries(queries_path="templates/research_queries.json"):
    """
    config/ 디렉토리의 JSON 파일에서 딥리서치 검색 쿼리 리스트를 로드합니다.
    """
    path = Path(queries_path)
    if not path.exists():
        logger.warning(f"[Deep Research Gen] 경고: 쿼리 설정 파일을 찾을 수 없습니다 ({config_path}). 기본 쿼리를 사용합니다.")
        return [
            "KOSPI 200 거시경제 전망 금리 환율",
            "반도체 업황 슈퍼사이클 외국인 순매수 수급 동향",
            "국내 증시 주요 리스크 요인 2026"
        ]
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            queries = data.get("queries", [])
            if queries:
                logger.info(f"[Deep Research Gen] 성공: {len(queries)}개의 쿼리를 설정 파일에서 로드했습니다.")
                return queries
    except Exception as e:
        logger.warning(f"[Deep Research Gen] 쿼리 파일 로드 중 에러 발생 ({e}). 기본 쿼리로 대체합니다.")
        
    return [
        "KOSPI 200 거시경제 전망 금리 환율",
        "반도체 업황 슈퍼사이클 외국인 순매수 수급 동향",
        "국내 증시 주요 리스크 요인 2026"
    ]

def search_web_links(query, max_results=2):
    """
    DuckDuckGo를 이용해 특정 쿼리의 관련 링크를 검색합니다.
    """
    logger.info(f"[Deep Research] 다중 검색 쿼리 실행 -> '{query}'")
    links = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            for r in results:
                if 'href' in r:
                    links.append(r['href'])
    except Exception as e:
        logger.warning(f"[Deep Research] 검색 에러 발생 ({query}): {e}")
    return links

def scrape_text_from_url(url):
    """
    BeautifulSoup으로 특정 URL의 본문 텍스트를 스크래핑합니다.
    """
    import requests
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return text[:3000] # 토큰 최적화
    except Exception as e:
        logger.warning(f"[Deep Research] 스크래핑 실패 ({url}): {e}")
    return ""

def load_prompt_template(template_path="templates/deep_research_prompt_template.txt"):
    """
    templates/ 디렉토리에 격리된 프롬프트 템플릿 파일을 읽어옵니다.
    """
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"[Deep Research Gen] 에러: 프롬프트 템플릿을 찾을 수 없습니다 -> {template_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_deep_research_input(output_dir="data/deep_research", template_path="templates/deep_research_prompt_template.txt", config_path="config/research_queries.json"):
    """
    외부 설정 파일에서 여러 검색어를 읽어와 다중 웹 수집을 수행한 뒤, 
    Gemini 모델을 통해 최종 딥리서치 JSON 인풋 파일을 생성합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_DEEP_RESEARCH_API_KEY")
    if not api_key:
        logger.warning("[Deep Research Gen] 경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. 기본 Fallback 데이터를 생성합니다.")
        return save_fallback_research(output_dir)

    try:
        template_content = load_prompt_template(template_path)
    except Exception as e:
        logger.error(f"[Deep Research Gen] 에러: {e}")
        return save_fallback_research(output_dir)

    # 쿼리 설정 파일 연동
    queries = load_research_queries(config_path)

    combined_texts = ""
    collected_links_count = 0

    for query in queries:
        links = search_web_links(query, max_results=2)
        for link in links:
            collected_links_count += 1
            logger.info(f"[Deep Research] 페이지 본문 수집 중 [{collected_links_count}]: {link}")
            page_text = scrape_text_from_url(link)
            if page_text:
                combined_texts += f"\n\n--- 출처 ({link}) ---\n{page_text}"
            time.sleep(1)

    if not combined_texts:
        logger.warning("[Deep Research Gen] 수집된 웹 본문이 없습니다. Fallback 데이터로 대체합니다.")
        return save_fallback_research(output_dir)

    try:
        topic_str = "KOSPI 200 거시경제, 반도체 업황 및 외국인 수급 복합 분석"
        prompt = template_content.replace("{topic}", topic_str).replace("{combined_texts}", combined_texts)

        client = genai.Client(api_key=api_key)
        model_name = DEEP_RESEARCH_MODEL

        logger.info(f"[Deep Research Gen] Gemini({model_name}) 모델로 다중 수집 자료 분석 및 리서치 JSON 생성 중...")
        
        response = call_gemini_with_retry(
            client=client,
            model_name=model_name,
            prompt_text=prompt,
            max_retries=3,
            delay=10
        )
        
        raw_text = response.text.strip()
        
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()
            raw_text = raw_text.strip("`").strip()

        research_data = json.loads(raw_text)
        
        research_data.setdefault("multiplier", 1.0)
        research_data.setdefault("summary", "딥리서치 요약 정보가 정상 생성되었습니다.")
        research_data.setdefault("risks", [])
        research_data["status"] = "success"

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = out_path / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(research_data, f, ensure_ascii=False, indent=4)
            
        logger.info(f"[Deep Research Gen] 성공: 다중 검색 실시간 딥리서치 인풋 파일 생성 완료 -> {filename}")
        return True

    except Exception as e:
        logger.error(f"[Deep Research Gen] 에러: 딥리서치 생성 또는 파싱 중 예외 발생 ({e}). Fallback 데이터로 대체합니다.")
        return save_fallback_research(output_dir)

def save_fallback_research(output_dir="data/deep_research"):
    """
    API 장애 또는 키 미설정 시 안전한 Fallback JSON 파일을 생성합니다.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    fallback_data = {
        "multiplier": 1.0,
        "summary": "외부 딥리서치 API 호출 실패로 기본 정량 스코어를 유지합니다.",
        "risks": ["특이사항 없음 (Fallback 모드)"],
        "status": "fallback"
    }
    
    filename = out_path / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(fallback_data, f, ensure_ascii=False, indent=4)
    logger.info(f"[Deep Research Gen] Fallback 딥리서치 인풋 파일 생성 완료 -> {filename}")
    return True

if __name__ == "__main__":
    generate_deep_research_input()
