# PR Review Examples

실제 PR 리뷰 코멘트 예시입니다.

## Example 1: Testing Issue

```markdown
## PR #123 코드 리뷰

라우터 테스트 추가 및 AI 피드백 기능 구현. 전반적으로 잘 구조화되어 있으나, 테스트 격리 문제와 에러 핸들링 개선이 필요합니다.

---

### ✅ Strengths

- ✨ 깔끔한 데이터베이스 스키마 및 마이그레이션 (db.ts:15-42)
- ✨ 포괄적인 테스트 커버리지 (18개 테스트, 모든 엣지 케이스 포함)
- ✨ 우수한 에러 핸들링 및 폴백 처리 (summarizer.ts:85-92)

---

### Issues

#### ⚠️ Critical (Must Fix)

**1. 테스트 격리 보장 필요**

**파일:**
- `ai-feedback.router.test.ts:10-25`
- `submissions.router.test.ts:15-30`

**현재 코드:**

```typescript
describe("aiFeedbackRouter", () => {
  it("create는 서비스 createAIFeedback을 호출한다", async () => {
    // beforeEach 없이 바로 테스트 시작
    mocks.createAIFeedback.mockResolvedValue(mockFeedback);
    // ...
  });
});
```

**문제:**

현재 `beforeEach`가 없어서 각 테스트가 실행될 때 mock이 리셋되지 않습니다. 이전 테스트의 mock 호출 이력이 남아있어서 테스트 실행 순서에 따라 결과가 달라질 수 있습니다 (flaky test 위험).

**개선 방법:**

```typescript
describe("aiFeedbackRouter", () => {
  beforeEach(() => {
    mocks.createAIFeedback.mockReset();
    mocks.generateOverallFeedback.mockReset();
    mocks.paragraphFeedback.mockReset();
  });

  it("create는 서비스 createAIFeedback을 호출한다", async () => {
    // ...
  });
});
```

---

#### 💡 Important (Should Fix)

**2. CLI 래퍼에 help 텍스트 누락**

**파일:**
- `index-conversations.ts:1-31`

**문제:**

`--help` 플래그가 없어서 사용자가 `--concurrency` 옵션을 발견하기 어렵습니다.

**개선 방법:**

```typescript
if (args.includes('--help')) {
  console.log(`
Usage: npm run index-conversations [options]

Options:
  --concurrency <number>  Number of concurrent operations (default: 5)
  --help                  Show this help message
  `);
  process.exit(0);
}
```

**3. 날짜 검증 누락**

**파일:**
- `search.ts:25-27`

**문제:**

잘못된 날짜 형식이 입력되면 조용히 결과 없음을 반환합니다. 사용자가 왜 검색이 실패했는지 알 수 없습니다.

**개선 방법:**

```typescript
function validateISODate(date: string) {
  const isoRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!isoRegex.test(date)) {
    throw new Error(`Invalid date format: ${date}. Expected ISO format (YYYY-MM-DD)`);
  }
}
```

---

#### 🔧 Minor (Nice to Have)

**4. 진행 상황 표시 개선**

**파일:**
- `indexer.ts:130`

**문제:**

긴 작업 수행 시 "X of Y" 카운터가 없어서 사용자가 얼마나 기다려야 할지 알 수 없습니다.

---

### Recommendations

- 사용자 경험을 위해 진행 상황 리포팅 추가 고려
- 제외할 프로젝트 목록을 설정 파일로 관리하면 이식성 향상

---

### Assessment

**Ready to merge:** With fixes

**Reasoning:** 핵심 구현은 견고하며 아키텍처와 테스트가 우수합니다. Important 이슈(help 텍스트, 날짜 검증)는 쉽게 수정 가능하며 핵심 기능에는 영향을 주지 않습니다.
```

---

## Example 2: Frontend Performance Issue

```markdown
## PR #456 코드 리뷰

사용자 프로필 페이지 리팩토링. 컴포넌트 구조는 개선되었으나 성능 이슈가 있습니다.

---

### ✅ Strengths

- ✨ 컴포넌트 계층 구조가 명확하고 재사용 가능 (UserProfile.tsx)
- ✨ TypeScript 타입 정의가 포괄적 (types/user.ts)

---

### Issues

#### ⚠️ Critical (Must Fix)

**1. API 호출 Waterfall 제거**

**파일:**
- `components/UserProfile.tsx:45-47`

**현재 코드:**

```typescript
const user = await fetchUser(id);
const posts = await fetchPosts(id);
```

**문제:**

두 개의 독립적인 API 호출이 순차적으로 실행되어 불필요한 대기 시간이 발생합니다. 첫 번째 요청이 완료될 때까지 두 번째 요청이 대기하므로, 전체 로딩 시간이 증가합니다 (200ms + 150ms = 350ms → 200ms로 단축 가능).

**개선 방법:**

```typescript
const [user, posts] = await Promise.all([fetchUser(id), fetchPosts(id)]);
```

---

#### 💡 Important (Should Fix)

**2. 불필요한 'use client' 지시어**

**파일:**
- `components/UserHeader.tsx:1`

**문제:**

이 컴포넌트는 상호작용이 없고 서버에서 렌더링 가능하지만, 'use client'로 인해 클라이언트 번들에 포함됩니다.

**개선 방법:**

'use client' 지시어를 제거하여 서버 컴포넌트로 전환

---

### Assessment

**Ready to merge:** No

**Reasoning:** API waterfall은 사용자 경험에 직접적인 영향을 주는 성능 문제로 반드시 수정 필요합니다.
```

---

## Example 3: Code Quality Issue

```markdown
## PR #789 코드 리뷰

사용자 관리 서비스 개선. 기능은 정상 작동하나 코드 구조 개선이 필요합니다.

---

### ✅ Strengths

- ✨ Pydantic을 사용한 철저한 입력 검증 (models/user.py:10-25)
- ✨ 포괄적인 단위 테스트 (test_user_service.py)

---

### Issues

#### 💡 Important (Should Fix)

**1. 함수 책임 분리 (Single Responsibility Principle)**

**파일:**
- `services/user.service.ts:120-180`

**현재 코드:**

```typescript
async function processUserData(data: UserInput) {
  // validation
  if (!data.email) throw new Error("Invalid email");

  // transformation
  const normalized = data.email.toLowerCase();

  // save to DB
  await db.user.create({ email: normalized });

  // send notification
  await emailService.send(normalized, "Welcome!");
}
```

**문제:**

`processUserData` 함수가 데이터 검증, 변환, 저장, 알림 전송을 모두 담당하고 있어 테스트와 유지보수가 어렵습니다. 각 책임이 강하게 결합되어 있어서 독립적으로 변경하기 어렵습니다.

**개선 방법:**

```typescript
async function processUserData(data: UserInput) {
  const validated = validateUserData(data);
  const transformed = transformUserData(validated);
  const saved = await saveUser(transformed);
  await sendNotification(saved);
  return saved;
}
```

---

#### 🔧 Minor (Nice to Have)

**2. 매직 넘버 상수화**

**파일:**
- `utils/pagination.ts:15`

**문제:**

`const pageSize = 20;` 같은 매직 넘버를 상수로 추출하면 가독성이 향상됩니다.

---

### Assessment

**Ready to merge:** With fixes

**Reasoning:** 기능은 정상 작동하며 테스트 커버리지도 좋습니다. SRP 위반은 향후 유지보수성에 영향을 주므로 개선 권장하지만, 현재 기능에는 문제없습니다.
```
