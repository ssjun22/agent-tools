---
title: Function Size and Complexity
impact: MEDIUM
impactDescription: improves readability and maintainability
tags: clean-code, functions, complexity
---

## Function Size and Complexity

함수는 한 가지 일만 하도록 작게 유지합니다.

**Incorrect (100줄 이상의 긴 함수):**

```typescript
async function processOrder(orderId: string) {
  // 주문 조회
  const order = await db.query(`SELECT * FROM orders WHERE id = ${orderId}`)
  if (!order) throw new Error('Order not found')

  // 재고 확인
  for (const item of order.items) {
    const stock = await db.query(`SELECT * FROM inventory WHERE id = ${item.productId}`)
    if (stock.quantity < item.quantity) {
      throw new Error(`Insufficient stock for ${item.productId}`)
    }
  }

  // 재고 차감
  for (const item of order.items) {
    await db.query(`UPDATE inventory SET quantity = quantity - ${item.quantity} WHERE id = ${item.productId}`)
  }

  // 결제 처리
  const payment = await processPayment(order.totalAmount)
  if (!payment.success) {
    // 재고 롤백
    for (const item of order.items) {
      await db.query(`UPDATE inventory SET quantity = quantity + ${item.quantity} WHERE id = ${item.productId}`)
    }
    throw new Error('Payment failed')
  }

  // 이메일 발송
  await sendEmail(order.customerEmail, 'Order Confirmed')

  // 상태 업데이트
  await db.query(`UPDATE orders SET status = 'completed' WHERE id = ${orderId}`)

  return { success: true }
}
```

**Correct (작은 함수들로 분리):**

```typescript
async function processOrder(orderId: string) {
  const order = await getOrder(orderId)
  await validateInventory(order.items)

  try {
    await deductInventory(order.items)
    await processPayment(order.totalAmount)
    await notifyCustomer(order.customerEmail)
    await updateOrderStatus(orderId, 'completed')

    return { success: true }
  } catch (error) {
    await rollbackInventory(order.items)
    throw error
  }
}

async function getOrder(orderId: string) {
  const order = await db.query(`SELECT * FROM orders WHERE id = ?`, [orderId])
  if (!order) throw new Error('Order not found')
  return order
}

async function validateInventory(items: OrderItem[]) {
  for (const item of items) {
    const stock = await getStock(item.productId)
    if (stock.quantity < item.quantity) {
      throw new Error(`Insufficient stock for ${item.productId}`)
    }
  }
}

async function deductInventory(items: OrderItem[]) {
  for (const item of items) {
    await updateStock(item.productId, -item.quantity)
  }
}
```

**Note:** 각 함수는 한 가지 추상화 수준에서 작동해야 합니다.
