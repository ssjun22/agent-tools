---
title: Testing Error Cases
impact: HIGH
impactDescription: ensures robustness and error handling
tags: testing, error-handling, edge-cases
---

## Testing Error Cases

Happy path뿐만 아니라 에러 케이스와 엣지 케이스도 테스트합니다.

**Incorrect (Happy path만 테스트):**

```python
def test_divide():
    result = divide(10, 2)
    assert result == 5
```

**Correct (Edge case와 에러 케이스 포함):**

```python
def test_divide_positive_numbers():
    result = divide(10, 2)
    assert result == 5

def test_divide_by_zero_raises_error():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers():
    result = divide(-10, 2)
    assert result == -5

def test_divide_returns_float():
    result = divide(7, 2)
    assert result == 3.5

def test_divide_with_zero_numerator():
    result = divide(0, 5)
    assert result == 0

def test_divide_large_numbers():
    result = divide(1e10, 1e5)
    assert result == 1e5

def test_divide_invalid_input_types():
    with pytest.raises(TypeError):
        divide("10", 2)
```

**Note:** 에러 케이스를 테스트하면 예상치 못한 버그를 예방할 수 있습니다.
