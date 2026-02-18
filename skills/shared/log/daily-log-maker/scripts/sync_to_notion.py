#!/usr/bin/env python3
"""
Daily Log Maker - Git 커밋을 Notion에 자동 기록

이 스크립트는:
1. Git 저장소에서 지정 날짜의 커밋 메시지를 수집
2. Notion API를 통해 데이터베이스에 업무 일지 항목 추가

참고: AI 요약은 이 skill을 실행하는 Claude가 직접 수행합니다.
"""

import os
import sys
import subprocess
from datetime import datetime
from typing import List, Dict
import json
import urllib.request
import urllib.error
from pathlib import Path


def load_env_file():
    """
    .env 파일에서 환경 변수 로드
    스크립트 디렉토리의 상위 디렉토리(skill 루트)에서 .env 파일 찾기
    """
    # 스크립트 파일의 상위 디렉토리 (skill 루트)
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / ".env"

    if not env_file.exists():
        return

    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 빈 줄이나 주석 무시
                if not line or line.startswith('#'):
                    continue

                # KEY=VALUE 형식 파싱
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # 따옴표 제거 (있는 경우)
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # 기존 환경 변수가 없을 때만 설정
                    if key and not os.getenv(key):
                        os.environ[key] = value
    except Exception as e:
        print(f"⚠️  Warning: .env 파일 로드 실패: {e}", file=sys.stderr)


# 스크립트 시작 시 .env 파일 로드
load_env_file()


class GitCommitCollector:
    """Git 커밋 수집기"""

    @staticmethod
    def get_current_git_user() -> str:
        """
        현재 Git 사용자 이름 가져오기

        Returns:
            Git 사용자 이름 (git config user.name)
        """
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    @staticmethod
    def get_commits(date: str = None, author: str = None, all_authors: bool = False) -> List[Dict[str, str]]:
        """
        지정된 날짜의 Git 커밋 메시지 수집

        Args:
            date: YYYY-MM-DD 형식 (기본값: 오늘)
            author: Git author 이름/이메일 (기본값: 현재 Git 사용자)
            all_authors: True면 모든 작성자의 커밋 포함 (기본값: False)

        Returns:
            커밋 정보 리스트 [{"hash": ..., "message": ..., "time": ...}, ...]
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # author 파라미터가 명시되지 않았고 all_authors도 False면 현재 사용자로 설정
        if author is None and not all_authors:
            author = GitCommitCollector.get_current_git_user()
            if author:
                print(f"ℹ️  현재 Git 사용자의 커밋만 수집합니다: {author}", file=sys.stderr)
            else:
                print("⚠️  Warning: Git 사용자 이름을 가져올 수 없습니다. 모든 작성자의 커밋을 수집합니다.", file=sys.stderr)

        # 날짜 범위 설정 (해당 날짜 00:00 ~ 23:59)
        start_date = f"{date} 00:00:00"
        end_date = f"{date} 23:59:59"

        # Git log 명령어 구성
        cmd = [
            "git", "log",
            f"--since={start_date}",
            f"--until={end_date}",
            "--pretty=format:%H|||%s|||%ai|||%an",  # hash|||message|||timestamp|||author
        ]

        if author and not all_authors:
            cmd.extend([f"--author={author}"])

        current_dir = os.getcwd()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                cwd=current_dir
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|||")
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0][:7],  # 짧은 해시
                        "message": parts[1],
                        "time": parts[2],
                        "author": parts[3]
                    })

            return commits

        except subprocess.CalledProcessError as e:
            stderr = e.stderr if e.stderr else ""
            if "not a git repository" in stderr.lower():
                print(f"❌ Error: 현재 디렉토리가 Git 저장소가 아닙니다.")
                print(f"   현재 위치: {current_dir}")
                print(f"   Git 저장소 내에서 이 스크립트를 실행해주세요.")
            else:
                print(f"❌ Error: Git 명령어 실행 실패: {e}")
                print(f"   현재 위치: {current_dir}")
            return []
        except FileNotFoundError:
            print("❌ Error: Git이 설치되지 않았습니다.")
            print(f"   현재 위치: {current_dir}")
            print("   Git을 설치한 후 다시 시도해주세요.")
            return []


class NotionClient:
    """Notion API 클라이언트"""

    def __init__(self, token: str, database_id: str):
        """
        Args:
            token: Notion Integration API 토큰
            database_id: 대상 데이터베이스 ID
        """
        self.token = token
        self.database_id = database_id
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_daily_log(self, date: str, summary: str, commit_count: int) -> Dict:
        """
        Notion 데이터베이스에 업무 일지 항목 생성

        Args:
            date: YYYY-MM-DD 형식
            summary: 업무 요약 내용 (마크다운 형식 지원)
            commit_count: 커밋 개수

        Returns:
            생성된 페이지 정보 ({"success": bool, "url": str, "error": str})
        """
        url = "https://api.notion.com/v1/pages"

        # 요약 내용을 Notion 블록으로 변환
        blocks = self._markdown_to_blocks(summary)

        # Notion 페이지 데이터 구성
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "날짜": {
                    "date": {"start": date}
                },
                "작업 요약": {
                    "title": [
                        {
                            "text": {
                                "content": f"{date} 업무 일지"
                            }
                        }
                    ]
                },
                "커밋 수": {
                    "number": commit_count
                }
            },
            "children": blocks
        }

        try:
            # JSON 데이터를 바이트로 인코딩
            json_data = json.dumps(data).encode('utf-8')

            # HTTP 요청 생성
            req = urllib.request.Request(
                url,
                data=json_data,
                headers=self.headers,
                method='POST'
            )

            # API 호출
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return {
                    "success": True,
                    "url": response_data.get("url", ""),
                    "error": None
                }

        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            error_msg = f"Notion API 오류: {e.code} {e.reason}\n응답: {error_body}"
            return {
                "success": False,
                "url": None,
                "error": error_msg
            }
        except urllib.error.URLError as e:
            return {
                "success": False,
                "url": None,
                "error": f"네트워크 오류: {e.reason}"
            }
        except Exception as e:
            return {
                "success": False,
                "url": None,
                "error": f"예상치 못한 오류: {e}"
            }

    def _markdown_to_blocks(self, text: str) -> List[Dict]:
        """
        마크다운 텍스트를 Notion 블록으로 변환

        간단한 변환만 지원:
        - 일반 문단
        - 불릿 포인트 (-, *)
        - 번호 리스트 (1., 2., ...)
        """
        blocks = []
        lines = text.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 불릿 포인트
            if line.startswith("- ") or line.startswith("* "):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            # 번호 리스트
            elif len(line) > 2 and line[0].isdigit() and line[1:3] in [". ", ") "]:
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            # 일반 문단
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })

        return blocks if blocks else [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        }]


def main():
    """CLI 진입점 - Claude가 이 스크립트를 호출합니다"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Git 커밋을 수집하거나 Notion에 업무 일지 작성"
    )

    subparsers = parser.add_subparsers(dest="command", help="명령어")

    # collect 명령어: 커밋 수집
    collect_parser = subparsers.add_parser("collect", help="Git 커밋 수집")
    collect_parser.add_argument(
        "--date",
        help="날짜 (YYYY-MM-DD 형식, 기본값: 오늘)",
        default=None
    )
    collect_parser.add_argument(
        "--author",
        help="특정 Git author 이름/이메일 (기본값: 현재 Git 사용자)",
        default=None
    )
    collect_parser.add_argument(
        "--all-authors",
        action="store_true",
        help="모든 작성자의 커밋 포함 (기본값: 현재 사용자만)"
    )

    # create 명령어: Notion 항목 생성
    create_parser = subparsers.add_parser("create", help="Notion에 업무 일지 생성")
    create_parser.add_argument(
        "--date",
        required=True,
        help="날짜 (YYYY-MM-DD)"
    )
    create_parser.add_argument(
        "--summary",
        required=True,
        help="업무 요약 내용"
    )
    create_parser.add_argument(
        "--commit-count",
        type=int,
        required=True,
        help="커밋 개수"
    )
    create_parser.add_argument(
        "--notion-token",
        help="Notion API 토큰 (또는 NOTION_API_TOKEN 환경변수)",
        default=os.getenv("NOTION_API_TOKEN")
    )
    create_parser.add_argument(
        "--notion-db-id",
        help="Notion 데이터베이스 ID (또는 NOTION_DATABASE_ID 환경변수)",
        default=os.getenv("NOTION_DATABASE_ID")
    )

    args = parser.parse_args()

    if args.command == "collect":
        # Git 커밋 수집
        commits = GitCommitCollector.get_commits(
            date=args.date,
            author=args.author,
            all_authors=args.all_authors
        )
        # JSON으로 출력 (Claude가 파싱)
        print(json.dumps(commits, ensure_ascii=False, indent=2))

    elif args.command == "create":
        # Notion 항목 생성
        if not args.notion_token or not args.notion_db_id:
            print("❌ Error: Notion API 토큰 또는 데이터베이스 ID가 설정되지 않았습니다.")
            print("   --notion-token 또는 NOTION_API_TOKEN 환경변수 필요")
            print("   --notion-db-id 또는 NOTION_DATABASE_ID 환경변수 필요")
            sys.exit(1)

        client = NotionClient(args.notion_token, args.notion_db_id)
        result = client.create_daily_log(
            date=args.date,
            summary=args.summary,
            commit_count=args.commit_count
        )

        if result["success"]:
            print(f"✅ 성공! Notion URL: {result['url']}")
        else:
            print(f"❌ 실패: {result['error']}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
