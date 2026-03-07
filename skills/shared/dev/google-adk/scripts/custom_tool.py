"""
커스텀 툴 skeleton 코드를 지정한 경로에 생성한다.

두 가지 패턴을 포함한다:
- 함수형 툴 (동기)
- 외부 API 연동 툴 (비동기)

툴 작성 시 주의사항:
- 독스트링의 Args, Returns를 반드시 명시하라 — LLM이 툴을 올바르게 사용하는 데 직결된다
- 반환값은 직렬화 가능한 타입 (dict, list, str, int 등)으로 반환하라
- 에러 발생 시 예외를 raise하지 말고 에러 정보를 dict로 반환하는 것을 고려하라
- 비동기 API 호출은 async def로 정의하라
- 민감한 정보(API Key 등)는 환경변수로 관리하라

사용법:
    python scripts/custom_tool.py --output <생성할 파일 경로>

예시:
    python scripts/custom_tool.py --output ./agents/my_agent/tools.py
"""

import argparse
from pathlib import Path

TEMPLATE = '''\
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
'''


def main():
    parser = argparse.ArgumentParser(description="커스텀 툴 skeleton 생성")
    parser.add_argument("--output", required=True, help="생성할 파일 경로 (예: ./agents/my_agent/tools.py)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(TEMPLATE, encoding="utf-8")
    print(f"생성 완료: {output_path}")


if __name__ == "__main__":
    main()
