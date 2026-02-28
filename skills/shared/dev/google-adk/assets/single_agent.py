"""
단일 LlmAgent 기본 skeleton.

사용법:
1. agent의 name, instruction, tools를 목적에 맞게 수정한다.
2. model과 generate_content_config를 조정한다.
3. runner_setup.py와 함께 사용한다.
"""

from google.adk.agents import LlmAgent
from google.genai import types

# 커스텀 툴 정의 (필요에 따라 추가/제거)
def example_tool(input: str) -> dict:
    """
    예시 툴. 실제 구현으로 교체하라.

    Args:
        input: 처리할 입력값

    Returns:
        처리 결과를 포함한 딕셔너리
    """
    return {"result": input}


# 에이전트 정의
agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    instruction="""
    여기에 에이전트의 역할과 행동 지침을 작성하라.
    구체적이고 명확할수록 좋다.
    """,
    tools=[example_tool],
    output_key="agent_output",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
    ),
)
