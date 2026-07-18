# 용어

기계 식별자(파일명·JSON 필드·토큰·명령)는 영문 고정, 산문은 아래 통일어를 쓴다. 사람 접점 발화에서의 표기(화면 라벨)는 `gate-views.md`가 따로 정한다 — 내부 통일어를 화면에 그대로 노출하지 않는다.

- **착수 게이트 ① / 검수 게이트 ③** — 사람 판정 지점 2개. **②는 존재하지 않는다**(번호는 설계 이력).
- **동결(lock)** — ①에서 brief·plan·검증 구성(verify cmd·상한·검수 체크리스트)을 통째로 굳히는 사건. 부분 동결 없음. `lock`은 state.json 키. clarify 최종 상태 스냅샷(mode `scored/override/adhoc` · guard · brief-check · 판본 일치)도 함께 동결 — 경고는 `clarify-status`가 산출해 ① 뷰에 고지(기록+고지, 차단 아님).
- **상태 파일** — `state.json`. 판정·라이프사이클만(진단 정보 금지).
- **상시 단계** — clarify·explore·기준 설계·plan. 항상 존재하되 수렴하면 비용이 0으로 접힌다.
- **선택 단계** — refactor(및 향후 judge). ① 동결에서 사이클별 on/off.
- **흐릿한 완성 그림** — 사용자가 갖고 오는 미완의 의도상.
- **매듭** — 수렴 중 결정·제약·제외가 확정돼 사용자 확인을 받는 단위. 확인된 결정은 transcript `[refined]`(+출처 태그)로만 남긴다 — journal `문답`은 ③ 검수 전용.
- **transcript** — clarify Q/A 원문 정본(`transcript.md`). `interview-log` 경유 append 전용, lock 후 불변. 인터뷰 중 영속 정본은 이것뿐 — brief는 종료 시 1회 생성.
- **채점 루프** — 외부 격리 채점기(rubric 기본 4축: 문제·성공·보존·비목표)가 매 라운드 transcript 전문을 재채점해 약한 축을 지목. floor(전 축 4점) + 2연속 streak = 수렴(`CONVERGED`). R3까지 무채점, 판정은 core.sh 토큰 소유. 신규 작업(greenfield)은 보존 축을 축 집합에서 제외 — 축 구성이 과제 성격을 따르고, 구성 변경 시 streak 리셋.
- **Acceptance Guard** — 종료 직전 관문. 발견자 2(contrarian·gap_hunter) 독립 병렬 → closer 종합 → 코드 규칙(`closer not_ready OR high≥1 → BLOCK` + streak 리셋). floor 통과는 종료를 감사할 허가이지 종료할 허가가 아니다.
- **restate** — guard 통과 후 한 문장 목표 재진술 → 사용자 승인 → brief 1회 생성.
- **brief-check** — brief 생성 직후 전사 대조 관문(`core.sh brief-check`). 기계 태그 검사(출처 태그·R 범위) + 대조 lane(누락·왜곡·무단추가·재등장), 코드 규칙 `verdict fail OR high≥1 → FAIL`. 사용자가 승인한 매듭·restate와 brief 전문 사이의 전사 오류를 동결 전에 잡는다. 양 모드 공통.
- **출처 태그** — brief·transcript 확정 항목의 `[from-code]`(explorer 조사) / `[from-user]`(사람 판단) + `[R<n>]`(transcript 라운드 역링크). 미해결 큐의 `[코드]/[사용자]`(누가 답하나)와는 축이 다르다(이건 "어디서 왔나").
- **실패 먼저 보기** — 변경 전 실패를 목격하는 것(구 red). **통과 상태** — 구 green.
- **걸음 확인** — 걸음별 증거(`verify --step`, 라운드 미카운트). **최종 검증** — `verify`(FAIL 시 라운드 소모).
- **이월** — 이번 사이클이 답하지 않고 다음으로 넘기는 것. 수렴 중에는 답이 달라져도 이번 G-·C-·N-·걸음 구조가 그대로인 질문만 이월 가능.
- **이월 그릇(handoff)** — 사이클 폴더의 `handoff.md`. ③의 이월 판정분을 `H-` 항목으로 담아 다음 사이클로 넘긴다. 상태 `대기 → 소진(채택 사이클 기록)`. close 후 유일 가변(consume 하나, 래퍼 경유).
- **완료 보고(report)** — `core.sh report`가 매번 조합하는 뷰(저장 없음). ③ 검수 재료 겸 사후 감사. 유도: checklist 중 handoff 미편입 = 검수에서 확인.
- **게으른 경로 검사** — 최종 검증은 통과하지만 의도는 미달성인 경로(하드코딩·스텁·기준의 빈틈)를 기준 설계 시점에 점검.
- **웨이브** — 동시에 도는 걸음 묶음. `depends_on`에서 파생(`wave(S)=1+max(wave(deps))`), 명기하지 않는다.
- **라운드** — 최종 검증 누적 FAIL 횟수(PASS·ERROR는 미소모). 상한 도달 시 `LIMIT`. 상한은 래퍼 소유, ①에서 확정(기본 3).

## ID 체계
- brief: `G-`(성공) · `C-`(보존) · `N-`(비목표) · `A-`(전제) · `Q-`(미해결)
- transcript: `R<n>`(라운드) — 출처 태그 `[R<n>]`의 역링크 앵커
- plan: `S-`(걸음) · `W-`(웨이브, 파생)
- handoff: `H-`(이월 항목)
- **ID 불변**: 확정 항목의 내용 변경은 수정이 아니라 폐기(삭선 유지) + 신규 발번.

## journal 태그
`발견`(generator 간 상속 통로) · `이월` · `blocked` · `문답`(③ 검수 전용 — clarify 결정은 transcript `[refined]`) · `결정`. actor: `main` · `explorer` · `planner` · `generator:S-n` · `refactorer`.
