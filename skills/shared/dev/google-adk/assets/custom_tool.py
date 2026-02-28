"""
커스텀 툴 정의 패턴 skeleton.

두 가지 패턴을 포함한다:
1. 함수형 툴 (동기)
2. 외부 API 연동 툴 (비동기)

목적에 맞게 수정하고 에이전트의 tools 리스트에 추가하라.
"""

import httpx
import os


# 패턴 1: 함수형 툴 (동기)
def process_data(input_text: str, mode: str = "summary") -> dict:
    """
    데이터를 처리하고 결과를 반환한다.

    Args:
        input_text: 처리할 텍스트 데이터
        mode: 처리 방식 ("summary" 또는 "extract")

    Returns:
        처리 결과와 상태를 포함한 딕셔너리
    """
    # 실제 처리 로직으로 교체하라
    if mode == "summary":
        result = f"요약: {input_text[:100]}..."
    else:
        result = f"추출: {input_text}"

    return {
        "status": "success",
        "mode": mode,
        "result": result,
    }


# 패턴 2: 외부 API 연동 툴 (비동기)
async def call_external_api(query: str, max_results: int = 5) -> list[dict]:
    """
    외부 API를 호출하여 데이터를 가져온다.

    Args:
        query: 검색할 키워드 또는 질의
        max_results: 반환할 최대 결과 수 (기본값: 5)

    Returns:
        결과 항목들의 리스트. 각 항목은 id, title, content를 포함한다.
    """
    api_url = os.getenv("EXTERNAL_API_URL", "https://api.example.com/search")
    api_key = os.getenv("EXTERNAL_API_KEY", "")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            api_url,
            params={"q": query, "limit": max_results},
            headers={"Authorization": f"Bearer {api_key}"},
        )
        response.raise_for_status()
        data = response.json()

    return data.get("items", [])


# 에이전트에 등록할 때:
# from google.adk.agents import LlmAgent
#
# agent = LlmAgent(
#     name="my_agent",
#     model="gemini-2.5-flash",
#     instruction="...",
#     tools=[process_data, call_external_api],
# )
