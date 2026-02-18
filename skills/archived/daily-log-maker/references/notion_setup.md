# Notion API 설정 가이드

이 문서는 daily-log-maker skill을 사용하기 위한 Notion 설정 방법을 안내합니다.

## 1. Notion Integration 생성

1. [Notion Integrations 페이지](https://www.notion.so/my-integrations) 접속
2. "New integration" 클릭
3. 설정:
   - **Name**: "Daily Log Maker" (또는 원하는 이름)
   - **Associated workspace**: 업무 일지를 저장할 워크스페이스 선택
   - **Type**: Internal integration
   - **Capabilities**:
     - ✅ Read content
     - ✅ Insert content
     - ✅ Update content
4. "Submit" 클릭
5. **Internal Integration Token** 복사 (이것이 NOTION_API_TOKEN입니다)
   - 형식: `secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - ⚠️ 이 토큰은 안전하게 보관하세요!

## 2. Notion 데이터베이스 생성

### 2.1 새 데이터베이스 페이지 만들기

1. Notion에서 업무 일지를 저장할 위치로 이동
2. 새 페이지 생성: "업무 일지" (또는 원하는 이름)
3. `/database` 입력하고 "Table - Full page" 선택

### 2.2 데이터베이스 속성 설정

다음 속성(컬럼)들을 추가하세요:

| 속성 이름     | 타입   | 설명                      |
| ------------- | ------ | ------------------------- |
| **작업 요약** | Title  | 페이지 제목 (자동 생성됨) |
| **날짜**      | Date   | 업무 일지 날짜            |
| **커밋 수**   | Number | 해당 날짜의 총 커밋 개수  |

**속성 추가 방법:**

1. 테이블 헤더 오른쪽 끝의 "+" 클릭
2. 속성 타입 선택
3. 속성 이름 입력

### 2.3 Integration에 데이터베이스 접근 권한 부여

1. 데이터베이스 페이지 오른쪽 상단의 "•••" (More) 클릭
2. 하단의 "Connections" 또는 "Add connections" 클릭
3. 앞서 생성한 Integration ("Daily Log Maker") 선택
4. "Confirm" 클릭

⚠️ **중요**: 이 단계를 건너뛰면 API 호출 시 권한 오류가 발생합니다!

### 2.4 데이터베이스 ID 확인

데이터베이스 ID는 Notion 페이지 URL에서 확인할 수 있습니다:

```
https://www.notion.so/[workspace-name]/[DATABASE_ID]?v=[VIEW_ID]
                                        ^^^^^^^^^^^^^^^^
```

**예시:**

```
URL: https://www.notion.so/myworkspace/a1b2c3d4e5f6789012345678?v=...
Database ID: a1b2c3d4e5f6789012345678
```

또는:

1. 데이터베이스 페이지에서 "Share" 클릭
2. "Copy link" 클릭
3. URL에서 `?` 앞의 마지막 32자리가 데이터베이스 ID입니다

## 3. 환경 변수 설정

### 방법 1: .env 파일 사용 (권장)

skill 디렉토리에 `.env` 파일 생성:

```bash
# .env.example 파일 복사
cd daily-log-maker
cp .env.example .env
```

`.env` 파일을 열고 실제 값으로 수정:

```env
NOTION_API_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=a1b2c3d4e5f6789012345678
```

⚠️ **중요**: `.env` 파일은 자동으로 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다!

### 방법 2: 시스템 환경 변수로 설정

**macOS/Linux (.zshrc 또는 .bashrc):**

```bash
export NOTION_API_TOKEN="secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export NOTION_DATABASE_ID="a1b2c3d4e5f6789012345678"
```

설정 후 터미널을 재시작하거나 `source ~/.zshrc` 실행

**Windows (PowerShell):**

```powershell
$env:NOTION_API_TOKEN="secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:NOTION_DATABASE_ID="a1b2c3d4e5f6789012345678"
```

**환경 변수 우선순위:**

1. 시스템 환경 변수 (최우선)
2. skill 디렉토리의 `.env` 파일
3. 명령줄 인자 (--notion-token, --notion-db-id)

## 4. 설정 확인

다음 명령어로 설정이 올바른지 확인할 수 있습니다:

```bash
# .env 파일 확인
cat daily-log-maker/.env

# 또는 환경 변수 확인 (시스템 환경 변수를 사용하는 경우)
echo $NOTION_API_TOKEN
echo $NOTION_DATABASE_ID

# 간단한 테스트 (Python)
python3 << 'EOF'
import os
import urllib.request
import json

token = os.getenv("NOTION_API_TOKEN")
db_id = os.getenv("NOTION_DATABASE_ID")

if not token or not db_id:
    print("❌ 환경 변수가 설정되지 않았습니다.")
else:
    # 데이터베이스 조회 테스트
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28"
    }

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("✅ Notion API 연결 성공!")
            print(f"   데이터베이스: {data['title'][0]['plain_text']}")
    except Exception as e:
        print(f"❌ 오류: {e}")
EOF
```

## 문제 해결

### "Could not find database" 오류

- Integration에 데이터베이스 접근 권한이 부여되었는지 확인
- 데이터베이스 ID가 올바른지 확인

### "Unauthorized" 오류

- API 토큰이 올바른지 확인
- 토큰이 `secret_`으로 시작하는지 확인

### "Invalid request" 오류

- 데이터베이스 속성 이름이 정확한지 확인 ("날짜", "작업 요약", "커밋 수")
- 속성 타입이 올바른지 확인

## 참고 자료

- [Notion API 공식 문서](https://developers.notion.com/)
- [Notion Integration 가이드](https://www.notion.so/help/create-integrations-with-the-notion-api)
- [Notion API Reference](https://developers.notion.com/reference/intro)
