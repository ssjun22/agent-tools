---
title: Few-shot Learning Examples
impact: MEDIUM
impactDescription: improves output quality and consistency
tags: prompt, few-shot, examples, llm
---

## Few-shot Learning Examples

명확한 입출력 예제를 제공하여 원하는 형식의 응답을 유도합니다.

**Incorrect (예제 없이 지시만):**

```python
async def extract_entities(text: str):
    prompt = f"Extract all entities from: {text}. Return as JSON."
    response = await llm.generate(prompt)
    return response
```

**Correct (명확한 입출력 예제 포함):**

```python
async def extract_entities(text: str):
    messages = [
        {
            "role": "system",
            "content": "Extract entities (person, organization, location) from text."
        },
        {
            "role": "user",
            "content": "Apple announced Tim Cook will visit Seoul."
        },
        {
            "role": "assistant",
            "content": '{"persons": ["Tim Cook"], "organizations": ["Apple"], "locations": ["Seoul"]}'
        },
        {
            "role": "user",
            "content": text
        }
    ]

    return await llm.chat(messages)
```

**Note:** 2-3개의 예제면 대부분의 경우 충분합니다.
