#!/usr/bin/env python3
"""
Git 커밋 분석 스크립트

지정된 기간의 Git 커밋 메시지와 파일 변경 통계를 분석하여 JSON으로 출력합니다.
"""

import argparse
import json
import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path


def validate_git_repo(repo_path):
    """Git 저장소 유효성 검사"""
    git_dir = Path(repo_path) / '.git'
    if not git_dir.exists():
        print(f"Error: {repo_path}는 유효한 Git 저장소가 아닙니다.", file=sys.stderr)
        sys.exit(1)


def validate_date(date_str):
    """날짜 형식 검증 (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        print(f"Error: 잘못된 날짜 형식입니다: {date_str}. YYYY-MM-DD 형식을 사용하세요.", file=sys.stderr)
        sys.exit(1)


def get_commits(repo_path, start_date, end_date):
    """지정된 기간의 커밋 목록 가져오기"""
    try:
        # git log 명령 실행
        cmd = [
            'git', '-C', repo_path, 'log',
            f'--since={start_date}',
            f'--until={end_date} 23:59:59',
            '--pretty=format:%H|%ai|%s'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout.strip():
            return []

        commits = []
        for line in result.stdout.strip().split('\n'):
            parts = line.split('|', 2)
            if len(parts) == 3:
                commit_hash, date_str, message = parts
                # 날짜를 YYYY-MM-DD 형식으로 변환
                commit_date = date_str.split()[0]
                commits.append({
                    'hash': commit_hash[:7],  # 짧은 해시
                    'date': commit_date,
                    'message': message.strip()
                })

        return commits

    except subprocess.CalledProcessError as e:
        print(f"Error: Git 명령 실행 실패: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: 예상치 못한 오류: {e}", file=sys.stderr)
        sys.exit(1)


def get_commit_stats(repo_path, commit_hash):
    """특정 커밋의 파일 변경 통계 가져오기"""
    try:
        cmd = [
            'git', '-C', repo_path, 'show',
            '--stat', '--format=', commit_hash
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        stats_text = result.stdout.strip()
        if not stats_text:
            return {'files_changed': 0, 'insertions': 0, 'deletions': 0}

        # 마지막 줄에서 통계 파싱
        # 예: " 3 files changed, 45 insertions(+), 12 deletions(-)"
        lines = stats_text.split('\n')
        last_line = lines[-1].strip()

        files_changed = 0
        insertions = 0
        deletions = 0

        # 파일 수 추출
        files_match = re.search(r'(\d+) files? changed', last_line)
        if files_match:
            files_changed = int(files_match.group(1))

        # insertions 추출
        insertions_match = re.search(r'(\d+) insertions?\(\+\)', last_line)
        if insertions_match:
            insertions = int(insertions_match.group(1))

        # deletions 추출
        deletions_match = re.search(r'(\d+) deletions?\(-\)', last_line)
        if deletions_match:
            deletions = int(deletions_match.group(1))

        return {
            'files_changed': files_changed,
            'insertions': insertions,
            'deletions': deletions
        }

    except subprocess.CalledProcessError:
        # 통계를 가져올 수 없는 경우 0으로 처리
        return {'files_changed': 0, 'insertions': 0, 'deletions': 0}
    except Exception as e:
        print(f"Warning: 커밋 {commit_hash} 통계 파싱 실패: {e}", file=sys.stderr)
        return {'files_changed': 0, 'insertions': 0, 'deletions': 0}


def analyze_repository(repo_path, start_date, end_date):
    """저장소 분석 메인 함수"""
    validate_git_repo(repo_path)
    validate_date(start_date)
    validate_date(end_date)

    # 커밋 목록 가져오기
    commits = get_commits(repo_path, start_date, end_date)

    if not commits:
        return {
            'commits': [],
            'summary': {
                'total_commits': 0,
                'total_files_changed': 0,
                'total_insertions': 0,
                'total_deletions': 0
            }
        }

    # 각 커밋의 통계 수집
    total_files = 0
    total_insertions = 0
    total_deletions = 0

    for commit in commits:
        stats = get_commit_stats(repo_path, commit['hash'])
        commit.update(stats)

        total_files += stats['files_changed']
        total_insertions += stats['insertions']
        total_deletions += stats['deletions']

    return {
        'commits': commits,
        'summary': {
            'total_commits': len(commits),
            'total_files_changed': total_files,
            'total_insertions': total_insertions,
            'total_deletions': total_deletions
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Git 커밋 분석 도구 - 지정된 기간의 커밋 정보를 JSON으로 출력합니다.'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='Git 저장소 경로'
    )
    parser.add_argument(
        '--start',
        required=True,
        help='시작 날짜 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end',
        required=True,
        help='종료 날짜 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='들여쓰기된 JSON 출력'
    )

    args = parser.parse_args()

    # 분석 실행
    result = analyze_repository(args.repo, args.start, args.end)

    # JSON 출력
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))


if __name__ == '__main__':
    main()
