---
title: JSON Response Parsing
impact: HIGH
impactDescription: ensures reliable structured outputs
tags: prompt, json, parsing, validation
---

## JSON Response Parsing

JSON schema를 명시하고 응답을 검증하여 안정적인 구조화된 출력을 보장합니다.

**Incorrect (자유 형식 응답):**

```python
async def analyze_sentiment(text: str):
    prompt = f"Analyze sentiment of: {text}"
    response = await llm.generate(prompt)
    return response  # 형식 불확실
```

**Correct (JSON schema 지정 및 검증):**

```python
from pydantic import BaseModel, Field
from typing import Literal
import json

class SentimentAnalysis(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float = Field(ge=0, le=1)
    reasoning: str

async def analyze_sentiment(text: str) -> SentimentAnalysis:
    prompt = f"""
Analyze sentiment of: "{text}"

Respond ONLY with valid JSON:
{{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}
"""

    response = await llm.generate(prompt)

    try:
        data = json.loads(response)
        return SentimentAnalysis(**data)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Invalid response: {e}")
```

**Note:** Pydantic 모델을 사용하면 타입 안전성과 자동 검증을 얻을 수 있습니다.
