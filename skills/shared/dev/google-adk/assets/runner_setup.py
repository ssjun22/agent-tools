"""
Agent Runner + Session 초기화 skeleton.

에이전트를 실행하기 위한 기본 설정.
agent 변수에 실제 에이전트(또는 루트 에이전트)를 연결하여 사용하라.

사용 예:
    from single_agent import agent  # 또는 pipeline, root_agent 등
    # 아래 코드에서 agent 변수를 교체한다.
"""

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 실행할 에이전트를 import하여 교체하라
# from single_agent import agent
# from sequential_pipeline import pipeline as agent
# from parallel_pipeline import root_agent as agent


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
    session = session_service.create_session(
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
    # 사용 예시 (agent를 위에서 import한 에이전트로 교체하라)
    # result = asyncio.run(run_agent("안녕하세요, 도움이 필요합니다.", agent))
    # print(result)
    pass
