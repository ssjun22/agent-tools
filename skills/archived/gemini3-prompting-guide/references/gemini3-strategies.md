# Gemini 3 프롬프팅 전략 가이드

출처: Google Cloud Vertex AI - Gemini 3 Prompting Guide
원본: https://cloud.google.com/vertex-ai/generative-ai/docs/prompting-strategies

---

## 1. 온도(Temperature) 설정

> **Gemini 3 특성**: Gemini 3의 추론 기능은 `temperature=1.0`에 최적화되어 있음. 1.0 미만으로 낮추면 복잡한 수학·추론 작업에서 루핑, 예기치 않은 동작, 성능 저하가 발생하며, 이는 다른 모델에서 온도를 낮춰 안정성을 얻는 패턴과 반대됨.

- `temperature` 파라미터는 **기본값 1.0을 유지**할 것을 강력 권장

---

## 2. 응답 지연 시간 줄이기

> **Gemini 3 특성**: Gemini 3의 thinking 기능은 품질을 높이지만 지연 시간을 증가시킴. thinking level 조정과 `think silently` 지시를 조합하여 지연을 제어할 수 있음.

낮은 지연이 필요한 경우:
- 사고 수준(thinking level)을 `LOW`로 설정
- 시스템 안내에 `think silently` 추가

---

## 3. 추론과 외부 정보 구분

> **Gemini 3 특성**: Gemini 3은 포괄적 부정 제약에 과도하게 반응하여 기본 산술/논리까지 거부하는 경향이 다른 모델보다 강함.

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

## 4. 분할 단계 확인 (Two-Step Verification)

> **Gemini 3 특성**: Gemini 3은 자신이 수행할 수 없는 기능(URL 접근, 실시간 데이터 등)에 대해 그럴듯한 응답을 생성하는 경향이 강함. 명시적 STOP 조건 없이는 환각률이 높아짐.

### 해결
1단계: 정보/기능 존재 여부를 먼저 확인
2단계: 확인된 경우에만 응답 생성

```
Verify with high confidence if you're able to access the New York Times home page.
If you cannot verify, state 'No Info' and STOP. If verified, proceed to generate a response.

Query: Summarize the headlines from The New York Times today.
```

---

## 5. 중요한 정보와 제약 조건 정리 (Constraint Placement)

> **Gemini 3 특성**: Gemini 3은 긴 프롬프트에서 앞부분의 제약 조건을 무시하는 recency bias가 다른 모델보다 두드러짐. 제약 배치 순서가 출력 품질에 직접적 영향.

### 권장 프롬프트 구조

```
[맥락 및 소스 자료]
[기본 작업 안내]
[부정적 제약, 형식 제약, 정량적 제약]  ← 반드시 마지막에
```

특히 부정 제약(~하지 마라)은 **프롬프트 끝**에 배치.

---

## 6. 페르소나 사용 시 주의

> **Gemini 3 특성**: Gemini 3은 페르소나 adherence가 매우 강해, 모호한 페르소나 정의 시 다른 시스템 지침까지 무시하는 비율이 다른 모델 대비 높음.

### 해결
페르소나 정의를 명확하게, 모호한 상황 제거.

```
You are a data extractor. You are forbidden from clarifying, explaining, or
expanding terms. Output text exactly as it appears. Do not explain why.
```

---

## 7. 그라운딩 유지 (Grounding)

> **Gemini 3 특성**: Gemini 3은 가상 시나리오에서 학습 데이터의 실제 사실로 되돌아가는 경향이 강함. 명시적 그라운딩 선언 없이는 제공된 컨텍스트를 무시하고 자체 지식을 우선할 수 있음.

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

## 8. 여러 정보 소스 종합 (Synthesis)

> **Gemini 3 특성**: Gemini 3은 대규모 컨텍스트에서 첫 번째 관련 항목을 찾으면 나머지 처리를 조기 중단하는 경향이 있음. 질문 배치 위치가 종합 분석 품질에 직접적 영향.

### 해결
- 구체적인 질문/지침을 데이터 컨텍스트 **뒤에** 배치
- `Based on the entire document above...` 문구로 시작

```
Based on the entire document above, provide a comprehensive answer. Synthesize
all relevant information from the text that pertains to the question's scenario.
```

---

## 9. 출력 상세도 조정 (Output Verbosity)

> **Gemini 3 특성**: Gemini 3은 다른 모델 대비 기본 출력이 간결하고 직접적임. 상세 응답이 필요한 경우 명시적 지시 없이는 충분한 설명을 생성하지 않음.

더 대화형/수다스러운 응답이 필요하면 프롬프트에서 명시적으로 지시:

```
Explain this as a friendly, talkative assistant.
```
