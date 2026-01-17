# 파일 구조 및 Colocation Pattern

## Progressive Lifting 원칙

컴포넌트는 사용 범위에 따라 배치하며, 필요할 때 점진적으로 상위로 이동합니다.

**CRITICAL: 항상 사용 위치에 가장 가까운 곳에서 시작하세요 (single page), 필요할 때만 상위로 올리세요.**

### 배치 규칙

- **1개 페이지만 사용** → `app/[section]/[route]/_components/`
- **같은 섹션 내 여러 곳** → `app/[section]/_components/`
- **student & teacher 모두 사용** → `app/_components/` (flat, no domain folders)
- **완전 범용 UI** → `components/ui/`

### 예시

```
app/dashboard/overview/_components/stats-card.tsx    # Single page
app/dashboard/overview/_hooks/use-stats.ts           # Hooks grouped in _hooks/
app/dashboard/_components/sidebar.tsx                # Section-wide
app/_components/user-avatar.tsx                      # Cross-section (flat)
components/ui/button.tsx                             # Universal UI
```

## 관련 파일 그룹화

### Hooks
- `_hooks/` 디렉토리에 그룹화
- Progressive Lifting 규칙 동일 적용

### Schemas (Form Validation)
- `_schemas/` 디렉토리에 그룹화
- Form 컴포넌트와 colocation

### Utilities
- Domain 로직: `lib/{domain}-utils.ts`
- 범용 유틸: `lib/utils.ts`

## tRPC 파일 구조

### 3계층 분리
```
src/
  server/
    routers/
      user.ts              # tRPC router - procedures only
    services/
      user.service.ts      # Business logic
  types/
    dto/
      user.ts              # DTOs and types
```
