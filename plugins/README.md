# Plugins

플러그인은 스킬·에이전트·규칙·훅을 묶어 배포하는 의존성 매니페스트다.
파일을 직접 담지 않고 `plugin.json`의 `depends`로 선언하며,
`agent-plugin-manager` 스킬이 `agent-tools` 원본에서 해석해 대상 레포에 심링크한다.

## Available Plugins

### karpathy-coding-guide

LLM 코딩 실수를 줄이기 위한 Karpathy 행동 가이드라인.

- skills: `dev/karpathy-guidelines`
- rules: `karpathy-skills`

[자세한 내용 →](karpathy-coding-guide/README.md)

---

플러그인 구조 규약은 `skills/meta/agent-plugin-manager/references/plugin-structure-guide.md` 참조.
