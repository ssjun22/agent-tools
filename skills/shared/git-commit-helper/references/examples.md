# Git Commit Message Examples

## Type별 예시

### feat - 새 기능

```
feat: DatePicker 컴포넌트 추가 및 Button 리팩토링

- DatePicker, Calendar, Popover UI 컴포넌트 추가
- Button 컴포넌트에 cva 패턴 적용하여 variant 관리 개선
- 과제 폼에서 제목 입력 필드 제거
```

```
feat: 평가 항목 저장 및 조회 기능 구현

- 평가 항목을 데이터베이스에 저장하고 조회할 수 있는 API 엔드포인트 추가
- 사용자가 작성한 평가 내용을 영구적으로 보관
```

### fix - 버그 수정

```
fix: 과제 평가 페이지 디자인 수정

- 평가 항목 입력 폼의 레이아웃이 깨지는 문제 해결
- 반응형 디자인이 모바일에서 올바르게 작동하도록 수정
```

### refactor - 리팩토링

```
refactor: 인증 모듈 구조 개선

- 컨트롤러의 인증 로직을 서비스 레이어로 이동
- 검증 로직을 별도 validator로 분리
- 새 구조에 맞게 테스트 업데이트
```

```
refactor: 데이터베이스 쿼리 로직 개선

- 중복된 쿼리 패턴을 재사용 가능한 함수로 추출
- 코드 가독성 향상 및 유지보수성 개선
```

### chore - 유지보수

```
chore: env 포맷 파일 추가

- 환경 변수 설정을 위한 .env.example 파일 추가
- 필수 환경 변수 목록 및 설명 포함
```

### 한 줄 예시 (본문 없이)

- `feat: 대시보드에 로딩 스피너 추가`
- `fix: 이메일 형식 검증 오류 수정`
- `docs: API 사용 가이드 문서 작성`
- `style: 코드 포맷팅 및 린트 규칙 적용`
- `test: 사용자 인증 통합 테스트 추가`
- `chore: Node 버전을 20으로 업데이트`

---

## GOOD vs BAD

**GOOD - bullet point 형식:**

```
feat: DatePicker 컴포넌트 추가

- DatePicker, Calendar, Popover UI 컴포넌트 추가
- Button 컴포넌트에 cva 패턴 적용하여 variant 관리 개선
```

**BAD - 문단형 + 마침표:**

```
feat: DatePicker 컴포넌트 추가

DatePicker, Calendar, Popover UI 컴포넌트를 추가했습니다.
Button 컴포넌트에 cva 패턴을 적용하여 variant 관리를 개선했습니다.
```
