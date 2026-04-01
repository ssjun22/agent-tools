"""
SequentialAgent 파이프라인 skeleton 코드를 지정한 경로에 생성한다.

사용법:
    python scripts/sequential_pipeline.py --output <생성할 파일 경로>

예시:
    python scripts/sequential_pipeline.py --output ./agents/pipeline/agent.py
"""

import argparse
from pathlib import Path

TEMPLATE = '''\
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
'''


def main():
    parser = argparse.ArgumentParser(description="SequentialAgent 파이프라인 skeleton 생성")
    parser.add_argument("--output", required=True, help="생성할 파일 경로 (예: ./agents/pipeline/agent.py)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(TEMPLATE, encoding="utf-8")
    print(f"생성 완료: {output_path}")


if __name__ == "__main__":
    main()
