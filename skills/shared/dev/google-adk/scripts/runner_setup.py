"""
Runner + Session 초기화 skeleton 코드를 지정한 경로에 생성한다.

사용법:
    python scripts/runner_setup.py --output <생성할 파일 경로>

예시:
    python scripts/runner_setup.py --output ./agents/my_agent/runner.py
"""

import argparse
from pathlib import Path

TEMPLATE = '''\
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 실행할 에이전트를 import하여 교체하라
# from agent import agent
# from agent import pipeline as agent
# from agent import root_agent as agent


async def run_agent(user_message: str, agent, session_id: str = "session_001") -> str:
    """
    에이전트를 실행하고 최종 응답을 반환한다.

    Args:
        user_message: 사용자 입력 메시지
        agent: 실행할 ADK 에이전트
        session_id: 세션 식별자

    Returns:
        에이전트의 최종 응답 텍스트
    """
    session_service = InMemorySessionService()
    session_service.create_session(
        app_name="my_app",
        user_id="user_001",
        session_id=session_id,
    )

    runner = Runner(
        agent=agent,
        app_name="my_app",
        session_service=session_service,
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    final_response = ""
    async for event in runner.run_async(
        user_id="user_001",
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    return final_response


if __name__ == "__main__":
    # 사용 예시
    # from agent import agent
    # result = asyncio.run(run_agent("안녕하세요, 도움이 필요합니다.", agent))
    # print(result)
    pass
'''


def main():
    parser = argparse.ArgumentParser(description="Runner + Session 초기화 skeleton 생성")
    parser.add_argument("--output", required=True, help="생성할 파일 경로 (예: ./agents/my_agent/runner.py)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(TEMPLATE, encoding="utf-8")
    print(f"생성 완료: {output_path}")


if __name__ == "__main__":
    main()
