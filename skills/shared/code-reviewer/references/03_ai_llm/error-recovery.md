---
title: Error Recovery Strategy
impact: MEDIUM
impactDescription: improves reliability and user experience
tags: error-handling, retry, fallback
---

## Error Recovery Strategy

LLM 호출 실패 시 재시도 및 fallback 로직을 구현합니다.

**Incorrect (실패 시 재시도 없음):**

```python
async def generate_summary(text: str):
    response = await llm.generate(f"Summarize: {text}")
    return response
    # 네트워크 오류나 rate limit 시 실패
```

**Correct (Fallback 및 retry 로직):**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def generate_summary(text: str) -> str:
    try:
        response = await llm.generate(f"Summarize: {text}")

        if not response:
            raise ValueError("Empty response")

        return response

    except Exception as e:
        logger.error(f"LLM generation failed: {e}")
        raise

async def safe_generate_summary(text: str) -> str:
    try:
        return await generate_summary(text)
    except Exception as e:
        logger.error(f"All retries failed: {e}")

        # Fallback: 간단한 요약
        sentences = text.split('.')
        return '. '.join(sentences[:3]) + '...'
```

**Note:** Exponential backoff를 사용하면 rate limit 문제를 완화할 수 있습니다.
