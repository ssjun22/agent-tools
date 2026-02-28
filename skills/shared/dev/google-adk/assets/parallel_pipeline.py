"""
ParallelAgent + SequentialAgent 조합 skeleton.

독립적인 작업을 병렬로 수행한 후, 결과를 종합하는 패턴.
병렬로 실행될 에이전트들과 종합 에이전트를 목적에 맞게 수정하라.
"""

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.genai import types


# 병렬 실행 에이전트 A
worker_a = LlmAgent(
    name="worker_a",
    model="gemini-2.5-flash",
    instruction="""
    소스 A에서 정보를 수집하라.
    """,
    tools=[],
    output_key="result_a",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
    ),
)

# 병렬 실행 에이전트 B
worker_b = LlmAgent(
    name="worker_b",
    model="gemini-2.5-flash",
    instruction="""
    소스 B에서 정보를 수집하라.
    """,
    tools=[],
    output_key="result_b",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
    ),
)

# 병렬 실행 단계
parallel_gather = ParallelAgent(
    name="parallel_gather",
    sub_agents=[worker_a, worker_b],
)

# 종합 에이전트 (result_a, result_b를 모두 참조)
synthesize_agent = LlmAgent(
    name="synthesize_agent",
    model="gemini-2.5-flash",
    instruction="""
    수집된 결과들을 종합하여 최종 답변을 작성하라.
    결과 A: {result_a}
    결과 B: {result_b}
    """,
    tools=[],
    output_key="final_result",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.5,
        max_output_tokens=2048,
    ),
)

# 병렬 수집 → 종합 순서 보장
root_agent = SequentialAgent(
    name="parallel_then_synthesize",
    sub_agents=[parallel_gather, synthesize_agent],
)
