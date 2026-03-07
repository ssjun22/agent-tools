# Gemini 3 프롬프팅 전략 가이드

출처: Google Cloud Vertex AI - Gemini 3 Prompting Guide

---

## 온도(Temperature) 설정

- `temperature` 파라미터는 **기본값 1.0을 유지**할 것을 강력 권장
- Gemini 3의 추론 기능은 기본 온도에 최적화되어 있음
- 1.0 미만으로 낮추면 복잡한 수학·추론 작업에서 루핑, 예기치 않은 동작, 성능 저하 발생 가능

---

## 응답 지연 시간 줄이기

낮은 지연이 필요한 경우:
- 사고 수준(thinking level)을 `LOW`로 설정
- 시스템 안내에 `think silently` 추가

---

## 추론과 외부 정보 구분

### 문제
`do not infer` 또는 `do not guess` 같은 포괄적 부정 제약은 모델이 기본적인 논리나 산술도 수행하지 못하게 만들 수 있음.

### 해결
외부 지식 차단과 내부 추론 허용을 **명시적으로 분리**해서 지시.

```
# ❌ 너무 광범위
What was the profit? Do not infer.

# ✅ 명확하게 분리
You are expected to perform calculations and logical deductions based strictly
on the provided text. Do not introduce external information.
```

---

## 분할 단계 확인 (Two-Step Verification)

모델이 모르는 정보나 불가능한 기능(특정 URL 접근 등)을 요청받으면 그럴듯하지만 잘못된 정보를 생성할 수 있음.

### 해결
1단계: 정보/기능 존재 여부를 먼저 확인
2단계: 확인된 경우에만 응답 생성

```
Verify with high confidence if you're able to access the New York Times home page.
If you cannot verify, state 'No Info' and STOP. If verified, proceed to generate a response.

Query: Summarize the headlines from The New York Times today.
```

---

## 중요한 정보와 제약 조건 정리 (Constraint Placement)

복잡한 요청에서 프롬프트 앞부분에 배치된 부정 제약 조건이나 형식·정량적 제약이 무시될 수 있음.

### 권장 프롬프트 구조

```
[맥락 및 소스 자료]
[기본 작업 안내]
[부정적 제약, 형식 제약, 정량적 제약]  ← 반드시 마지막에
```

특히 부정 제약(~하지 마라)은 **프롬프트 끝**에 배치.

---

## 페르소나 사용 시 주의

모델은 할당된 페르소나를 엄격히 따르도록 설계되어 있어, 모호한 페르소나는 지침을 무시하는 원인이 됨.

### 해결
페르소나 정의를 명확하게, 모호한 상황 제거.

```
You are a data extractor. You are forbidden from clarifying, explaining, or
expanding terms. Output text exactly as it appears. Do not explain why.
```

---

## 그라운딩 유지 (Grounding)

가상의 시나리오나 실제 사실과 다른 컨텍스트를 제공하면 모델이 학습 데이터로 되돌아갈 수 있음.

### 해결
현재 세션의 컨텍스트가 유일한 진실임을 명시적으로 선언.

```
You are a strictly grounded assistant limited to the information provided in the
User Context. In your answers, rely **only** on the facts that are directly
mentioned in that context. You must **not** access or utilize your own knowledge
or common sense to answer. Do not assume or infer from the provided facts;
simply report them exactly as they appear. Your answer must be factual and
fully truthful to the provided text, leaving absolutely no room for speculation
or interpretation. Treat the provided context as the absolute limit of truth;
any facts or details that are not directly mentioned in the context must be
considered **completely untruthful** and **completely unsupported**. If the
exact answer is not explicitly written in the context, you must state that the
information is not available.
```

---

## 여러 정보 소스 종합 (Synthesis)

대규모 데이터(전체 책, 코드베이스, 긴 동영상)에서 모델이 첫 번째 관련 항목 이후 추가 처리를 중단할 수 있음.

### 해결
- 구체적인 질문/지침을 데이터 컨텍스트 **뒤에** 배치
- `Based on the entire document above...` 문구로 시작

```
Based on the entire document above, provide a comprehensive answer. Synthesize
all relevant information from the text that pertains to the question's scenario.
```

---

## 출력 상세도 조정 (Output Verbosity)

기본적으로 Gemini 3은 간결하고 직접적인 답변을 선호.

더 대화형/수다스러운 응답이 필요하면 프롬프트에서 명시적으로 지시:

```
Explain this as a friendly, talkative assistant.
```
