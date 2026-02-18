---
title: Token Usage Optimization
impact: MEDIUM
impactDescription: reduces cost and improves latency
tags: prompt, tokens, optimization, cost
---

## Token Usage Optimization

불필요하게 긴 컨텍스트 대신 필요한 정보만 간결하게 포함합니다.

**Incorrect (불필요하게 긴 컨텍스트):**

```python
async def summarize_pr(pr_data: Dict):
    # 전체 diff를 그대로 포함
    prompt = f"""
Summarize: {json.dumps(pr_data, indent=2)}
All commits: {json.dumps(pr_data['commits'], indent=2)}
All file changes: {pr_data['diff']}
Please summarize.
"""
    return await llm.generate(prompt)
```

**Correct (필요한 정보만 간결하게):**

```python
async def summarize_pr(pr_data: Dict):
    changed_files = [f['filename'] for f in pr_data['files']]
    additions = sum(f['additions'] for f in pr_data['files'])
    deletions = sum(f['deletions'] for f in pr_data['files'])

    significant = [
        f"{f['filename']}: +{f['additions']} -{f['deletions']}"
        for f in pr_data['files']
        if f['additions'] + f['deletions'] > 10
    ]

    prompt = f"""
Summarize this PR:

**Title:** {pr_data['title']}
**Files:** {len(changed_files)} (+{additions} -{deletions})
**Key changes:** {', '.join(significant[:5])}
**Description:** {pr_data['body'][:300]}

Provide a 2-3 sentence summary.
"""
    return await llm.generate(prompt)
```

**Note:** 입력 토큰을 줄이면 비용과 지연시간이 감소합니다.
