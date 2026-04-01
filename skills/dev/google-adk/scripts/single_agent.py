"""
단일 LlmAgent skeleton 코드를 지정한 경로에 생성한다.

사용법:
    python scripts/single_agent.py --output <생성할 파일 경로>

예시:
    python scripts/single_agent.py --output ./agents/my_agent/agent.py
"""

import argparse
from pathlib import Path

TEMPLATE = '''\
from google.adk.agents import LlmAgent
from google.genai import types

agent = LlmAgent(
    name="my_agent",
    model="gemini-2.5-flash",
    description="이 에이전트의 역할을 한 줄로 설명하라. 멀티 에이전트 라우팅 시 참조된다.",
    instruction="""
    여기에 에이전트의 역할과 행동 지침을 작성하라.
    구체적이고 명확할수록 좋다.
    """,
    tools=[],
    output_key="agent_output",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048,
    ),
)
'''


def main():
    parser = argparse.ArgumentParser(description="단일 LlmAgent skeleton 생성")
    parser.add_argument("--output", required=True, help="생성할 파일 경로 (예: ./agents/my_agent/agent.py)")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(TEMPLATE, encoding="utf-8")
    print(f"생성 완료: {output_path}")


if __name__ == "__main__":
    main()
