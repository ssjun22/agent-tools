---
title: Open/Closed Principle
impact: MEDIUM
impactDescription: enables extensibility without modifying existing code
tags: solid, ocp, extensibility
---

## Open/Closed Principle

확장에는 열려있고 수정에는 닫혀있어야 합니다.

**Incorrect (수정을 위해 기존 코드 변경):**

```typescript
class PaymentProcessor {
  processPayment(amount: number, method: string) {
    if (method === 'credit_card') {
      return this.processCreditCard(amount)
    } else if (method === 'paypal') {
      return this.processPayPal(amount)
    } else if (method === 'crypto') {
      // 새로운 결제 방식 추가 시 기존 코드 수정 필요
      return this.processCrypto(amount)
    }
    throw new Error('Unknown payment method')
  }
}
```

**Correct (확장 가능하도록 설계):**

```typescript
interface PaymentMethod {
  process(amount: number): Promise<PaymentResult>
}

class CreditCardPayment implements PaymentMethod {
  async process(amount: number) {
    // 신용카드 결제 로직
    return { success: true, transactionId: 'cc-123' }
  }
}

class PayPalPayment implements PaymentMethod {
  async process(amount: number) {
    // PayPal 결제 로직
    return { success: true, transactionId: 'pp-456' }
  }
}

// 새로운 결제 방식 추가 시 기존 코드 수정 없음
class CryptoPayment implements PaymentMethod {
  async process(amount: number) {
    return { success: true, transactionId: 'crypto-789' }
  }
}

class PaymentProcessor {
  constructor(private paymentMethod: PaymentMethod) {}

  async processPayment(amount: number) {
    return await this.paymentMethod.process(amount)
  }
}
```

**Note:** 추상화와 인터페이스를 활용하여 확장성을 확보합니다.
