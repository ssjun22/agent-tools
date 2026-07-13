---
cycle: <cycle-id>
repo: <repo-slug>
base_commit: <hash>
type: <feat|fix|refactor|chore|docs|test>
slug: <kebab-case-30자내>
---

# Plan

<!--
산문 = 서사(왜 이렇게 자르나), 아래 ```json steps``` 블록 = 기계 정본(래퍼·에이전트 배정은 블록만 읽음).
이중 작성 금지: 산문과 JSON의 겹침은 id·제목뿐. type 생략 시 사이클 유형(frontmatter type) 상속.
같은 웨이브(= depends_on에서 파생, 명기하지 않음)는 files 소유권이 서로소여야 한다.
-->

## 개요
<!-- 채택한 하나의 접근(2~5줄) + 선택 단계(refactor 등) 권장 on/off. -->

## 걸음
<!--
S-1 · <하는 일> — 완료 조건: <끝났음을 아는 방법> — 담당: G-1, C-2
S-2 · …
의존이 없는데 순서를 강제한다면 "순서 강제: <사유>" 한 줄 의무.
-->

## 이월
<!-- 이번 사이클이 답하지 않고 다음으로 넘기는 것(있으면). -->

```json steps
{
  "steps": [
    {
      "id": "S-1",
      "title": "<커밋 subject용 한 줄 제목>",
      "type": "feat",
      "files": ["src/foo.ts"],
      "depends_on": [],
      "check": "<걸음 확인 명령 — 없으면 이 필드 생략, human_check로>",
      "human_check": "<사람만 판정 가능한 항목 — 없으면 생략>",
      "grounds": ["G-1"]
    }
  ]
}
```

<!--
json steps 필드:
  id         : S-n (고유)
  title      : 커밋 subject 제목 (subject = "<type>: <title>")
  type       : 생략 시 frontmatter type 상속
  files      : write 소유 파일 — 순수 경로만((new) 등 주석 금지)
  depends_on : 선행 걸음 id 배열 (웨이브는 여기서 파생)
  check      : `core.sh verify --step`이 실행할 걸음 확인 명령(라운드 미카운트)
  human_check: 사람 검수 항목(기계 판정 불가) + 확인 방법 — ① lock `--check "항목 :: 방법"`으로 승격
  grounds    : 이 걸음이 담당하는 brief ID(G-/C-)
걸음마다 check 또는 human_check 중 최소 하나는 있어야 한다(① lock에서 래퍼가 검증).
-->
