# Karpathy Coding Guide

## Overview

LLM 코딩 실수를 줄이기 위한 행동 가이드라인 플러그인. Andrej Karpathy의 관찰을 기반으로 한 4가지 원칙(Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution)을 적용한다.

## When to Use

- 코드 작성·리뷰·리팩토링 시 과잉 복잡화를 방지하고 싶을 때
- AI 에이전트의 코딩 품질 기준을 프로젝트에 적용하고 싶을 때

## Dependencies

`plugin.json` 참조. 1개 스킬 + 1개 룰로 구성.

## Usage

```bash
python3 scripts/apply_to_repo.py karpathy-coding-guide --repo /path/to/project --dry-run
```
