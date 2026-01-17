---
title: KISS (Keep It Simple)
impact: MEDIUM
impactDescription: reduces complexity and cognitive load
tags: clean-code, kiss, simplicity
---

## KISS (Keep It Simple)

불필요하게 복잡한 구조 대신 간단하고 명확한 해결책을 선택합니다.

**Incorrect (불필요하게 복잡한 구조):**

```typescript
class DataProcessorFactory {
  createProcessor(type: string): IDataProcessor {
    const processorMap = new Map<string, () => IDataProcessor>()
    processorMap.set('json', () => new JSONDataProcessor())
    processorMap.set('xml', () => new XMLDataProcessor())

    const factory = processorMap.get(type)
    if (!factory) {
      throw new Error(`Unknown processor type: ${type}`)
    }

    return factory()
  }
}

interface IDataProcessor {
  process(data: any): any
}

class JSONDataProcessor implements IDataProcessor {
  process(data: any) {
    return JSON.parse(data)
  }
}
```

**Correct (간단하고 명확한 해결책):**

```typescript
function parseData(data: string, type: 'json' | 'xml') {
  if (type === 'json') {
    return JSON.parse(data)
  }

  if (type === 'xml') {
    return parseXML(data)
  }

  throw new Error(`Unknown type: ${type}`)
}
```

**Note:** 필요하지 않다면 디자인 패턴을 억지로 적용하지 마세요.
