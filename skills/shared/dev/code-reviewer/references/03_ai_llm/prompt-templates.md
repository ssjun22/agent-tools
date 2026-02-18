---
---
title: Structured Prompt Templates
impact: HIGH
impactDescription: enables maintainable and reusable prompts
tags: prompt, template, maintainability, llm
---

## Structured Prompt Templates

하드코딩된 프롬프트 대신 템플릿 변수를 활용하여 구조화된 프롬프트를 작성합니다.

**Incorrect (하드코딩된 프롬프트):**

```python
async def analyze_code(code: str):
    prompt = f"Analyze this code and tell me if it's good: {code}"
    response = await llm.generate(prompt)
    return response

async def review_pr(pr_title: str, pr_description: str):
    prompt = f"Review this PR. Title: {pr_title}. Description: {pr_description}. Tell me if it's okay."
    response = await llm.generate(prompt)
    return response
```

**Correct (템플릿 변수를 활용한 구조화):**

```python
from typing import Dict, Any

class PromptTemplate:
    CODE_ANALYSIS = """
You are an expert code reviewer. Analyze the following code:

**Code:**
```{language}
{code}
```

**Analysis Guidelines:**
- Code quality
- Potential bugs
- Performance issues
- Security vulnerabilities

Provide a structured analysis.
"""

    PR_REVIEW = """
You are reviewing a pull request.

**PR Title:** {title}
**PR Description:** {description}

Review criteria:
- Code quality
- Tests included
- Documentation updated

Provide your assessment.
"""

async def analyze_code(code: str, language: str = "python"):
    prompt = PromptTemplate.CODE_ANALYSIS.format(
        code=code,
        language=language
    )
    response = await llm.generate(prompt)
    return response
```

**Note:** 템플릿을 별도로 관리하면 프롬프트 개선과 유지보수가 쉬워집니다.
