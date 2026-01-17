---
title: Meaningful Test Names
impact: MEDIUM
impactDescription: improves test documentation and debugging
tags: testing, naming, documentation
---

## Meaningful Test Names

테스트 이름은 무엇을 테스트하는지 명확히 드러내야 합니다.

**Incorrect (모호한 테스트 이름):**

```python
def test_user():
    user = User("john@test.com")
    assert user is not None

def test_user2():
    user = User("")
    assert user is None

def test_user3():
    user = User("invalid")
    with pytest.raises(ValueError):
        user.save()
```

**Correct (설명적인 테스트 이름):**

```python
def test_creates_user_with_valid_email():
    user = User("john@test.com")
    assert user is not None
    assert user.email == "john@test.com"

def test_returns_none_when_email_is_empty():
    user = User("")
    assert user is None

def test_raises_error_when_email_format_is_invalid():
    user = User("invalid-email")
    with pytest.raises(ValueError, match="Invalid email format"):
        user.save()

def test_prevents_duplicate_email_registration():
    User("john@test.com").save()

    with pytest.raises(ValueError, match="Email already exists"):
        User("john@test.com").save()
```

**Note:** 테스트 이름만 봐도 실패 원인을 유추할 수 있어야 합니다.
