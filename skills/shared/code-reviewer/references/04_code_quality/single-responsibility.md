---
---
title: Single Responsibility Principle
impact: HIGH
impactDescription: improves maintainability and testability
tags: solid, srp, clean-code, architecture
---

## Single Responsibility Principle

각 클래스나 함수는 단 하나의 책임만 가져야 합니다.

**Incorrect (여러 책임을 가진 클래스):**

```python
class UserManager:
    def __init__(self, db):
        self.db = db

    def create_user(self, data):
        # 검증
        if not data.get('email'):
            raise ValueError("Email required")

        # 저장
        user = self.db.save(data)

        # 이메일 발송
        send_email(user.email, "Welcome!")

        # 로깅
        log_user_creation(user.id)

        return user
```

**Correct (단일 책임으로 분리):**

```python
class UserValidator:
    @staticmethod
    def validate(data):
        if not data.get('email'):
            raise ValueError("Email required")

class UserRepository:
    def __init__(self, db):
        self.db = db

    def save(self, data):
        return self.db.save(data)

class UserNotifier:
    @staticmethod
    def send_welcome_email(user):
        send_email(user.email, "Welcome!")

class UserService:
    def __init__(self, validator, repository, notifier, logger):
        self.validator = validator
        self.repository = repository
        self.notifier = notifier
        self.logger = logger

    def create_user(self, data):
        self.validator.validate(data)
        user = self.repository.save(data)
        self.notifier.send_welcome_email(user)
        self.logger.log_creation(user.id)
        return user
```

**Note:** 각 클래스가 하나의 변경 이유만 가지도록 설계합니다.
