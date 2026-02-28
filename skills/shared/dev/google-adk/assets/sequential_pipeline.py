"""
SequentialAgent 파이프라인 skeleton.

각 에이전트의 output_key 결과가 다음 에이전트의 instruction에서 참조된다.
단계 수와 역할을 목적에 맞게 수정하라.
"""

from google.adk.agents import LlmAgent, SequentialAgent
from google.genai import types


# 1단계 에이전트
step1_agent = LlmAgent(
    name="step1_agent",
    model="gemini-2.5-flash",
    instruction="""
    1단계 작업을 수행하라.
    결과를 명확하게 정리하여 출력하라.
    """,
    tools=[],
    output_key="step1_result",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
    ),
)

# 2단계 에이전트 (step1_result를 참조)
step2_agent = LlmAgent(
    name="step2_agent",
    model="gemini-2.5-flash",
    instruction="""
    이전 단계의 결과를 바탕으로 2단계 작업을 수행하라.
    이전 결과: {step1_result}
    """,
    tools=[],
    output_key="step2_result",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
    ),
)

# 3단계 에이전트 (step2_result를 참조)
step3_agent = LlmAgent(
    name="step3_agent",
    model="gemini-2.5-flash",
    instruction="""
    최종 단계 작업을 수행하라.
    이전 결과: {step2_result}
    """,
    tools=[],
    output_key="final_result",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
    ),
)

# 파이프라인 조립
pipeline = SequentialAgent(
    name="my_pipeline",
    sub_agents=[step1_agent, step2_agent, step3_agent],
)
