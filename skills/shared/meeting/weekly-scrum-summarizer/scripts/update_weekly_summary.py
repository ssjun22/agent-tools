#!/usr/bin/env python3
"""
주간 요약 문서 업데이트 스크립트
슬랙 텍스트를 파싱하여 Obsidian 주간 요약 문서를 생성/업데이트
"""

import os
import re
import sys
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# 스킬 베이스 디렉토리
SKILL_DIR = Path(__file__).parent.parent

def load_config() -> dict:
    """config.yaml 로드"""
    config_path = SKILL_DIR / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_week_info(date: Optional[datetime] = None) -> Tuple[int, int, str, str]:
    """
    주차 정보 계산
    Returns: (month, week, start_date, end_date)
    """
    if date is None:
        date = datetime.now()

    month = date.month
    day = date.day

    # 주차 계산: 매월 1일이 속한 주 = 1주차
    week = (day - 1) // 7 + 1

    # 해당 주의 월요일과 금요일 계산
    first_day = datetime(date.year, month, 1)
    week_start_offset = (week - 1) * 7
    week_start = first_day + timedelta(days=week_start_offset)

    # 월요일로 조정
    while week_start.weekday() != 0:  # 0 = 월요일
        week_start += timedelta(days=1)

    week_end = week_start + timedelta(days=4)  # 금요일

    start_str = week_start.strftime("%Y-%m-%d")
    end_str = week_end.strftime("%Y-%m-%d")

    return month, week, start_str, end_str

def extract_keywords(text: str) -> set:
    """작업 항목에서 핵심 키워드 추출"""
    text = text.lower().lstrip('-').strip()

    # 상태 단어 제거
    for word in ['완료', '마무리', '배포', '수정됨', '수정', '진행', '중']:
        text = text.replace(word, '')

    # 일반 단어 제거 (더 많은 단어 추가)
    for word in ['기능', '작업', '개발', '구현', '관련', '문서', '읽기', '조사',
                 '테스트', '설정', '추가', '수정', '개선', '확인', '미팅', '회의',
                 '버그', '이슈', '기술', '성능', 'api', 'ui', 'ux', '부하', '벤치마크',
                 '작성', '통일', '준비', '대응', 'stg', '오토스케일링', '모니터링',
                 '프롬프트', '에이전트', '버튼', '파일', '음성', '인식']:
        text = text.replace(word, '')

    # 키워드 추출 (2자 이상)
    keywords = set()
    for word in text.split():
        word = word.strip()
        if len(word) >= 2:
            keywords.add(word)

    return keywords

def calculate_similarity(text1: str, text2: str) -> float:
    """두 작업 항목의 유사도 계산 (Jaccard)"""
    keywords1 = extract_keywords(text1)
    keywords2 = extract_keywords(text2)

    if not keywords1 or not keywords2:
        return 0.0

    intersection = keywords1 & keywords2
    union = keywords1 | keywords2

    return len(intersection) / len(union) if union else 0.0

def parse_slack_text(text: str, config: dict) -> Dict[str, Dict[str, List[str]]]:
    """
    슬랙 텍스트 파싱
    Returns: {member_name: {section: [items]}}
    """
    members = {}
    current_member = None
    current_section = None

    section_headers = config['parsing']['section_headers']
    team_members = set(config['team']['members'])

    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 팀원 이름 감지 (한글 2-4자)
        name_match = re.match(r'^([가-힣]{2,4})\s*$', line)
        if name_match:
            name = name_match.group(1)
            if name in team_members:
                current_member = name
                if current_member not in members:
                    members[current_member] = {}
                current_section = None
                continue

        # 섹션 헤더 감지
        if current_member:
            # 한 주 요약
            for header in section_headers['weekly_plan']:
                if header in line:
                    current_section = 'weekly_plan'
                    members[current_member][current_section] = []
                    break

            # 어제 한 일
            for header in section_headers['yesterday']:
                if header in line:
                    current_section = 'yesterday'
                    members[current_member][current_section] = []
                    break

            # 오늘 할 일
            for header in section_headers['today']:
                if header in line:
                    current_section = 'today'
                    members[current_member][current_section] = []
                    break

        # 작업 항목 추가
        if current_member and current_section and line and not any(h in line for h in
            section_headers['weekly_plan'] + section_headers['yesterday'] + section_headers['today']):
            # 개인 일정 필터링
            if not any(keyword in line for keyword in ['반차', '휴가', '병가', '연차']):
                members[current_member][current_section].append(line)

    return members

def classify_by_project(items: List[str], member: str, config: dict) -> Dict[str, List[str]]:
    """작업 항목을 프로젝트별로 분류"""
    if member not in config['team']['projects']:
        return {'_no_project': items}

    projects = config['team']['projects'][member]

    # 프로젝트가 1개면 분류 안 함
    if len(projects) <= 1:
        return {'_no_project': items}

    project_keywords = config['team'].get('project_keywords', {})
    classified = {proj: [] for proj in projects}
    classified['_no_project'] = []

    for item in items:
        matched = False
        for proj in projects:
            if proj in project_keywords:
                keywords = project_keywords[proj]
                if any(keyword in item for keyword in keywords):
                    classified[proj].append(item)
                    matched = True
                    break

        if not matched:
            classified['_no_project'].append(item)

    # 빈 프로젝트 제거
    return {k: v for k, v in classified.items() if v}

def match_to_main_item(sub_item: str, main_items: List[str]) -> Optional[str]:
    """
    하위 항목을 메인 항목과 매칭
    Returns: 매칭된 메인 항목 또는 None
    """
    best_match = None
    best_similarity = 0.0

    for main_item in main_items:
        similarity = calculate_similarity(sub_item, main_item)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = main_item

    # 30% 이상 유사하면 매칭 (핵심 키워드만 남기므로 낮은 임계값 사용)
    if best_similarity >= 0.3:
        return best_match
    return None


def check_duplicate_in_subs(new_item: str, existing_subs: List[str]) -> Tuple[bool, Optional[str]]:
    """
    새 항목이 기존 하위 항목과 중복인지 체크
    Returns: (is_duplicate, existing_item_if_duplicate)
    """
    for existing in existing_subs:
        # 완료 마커 제거하고 비교
        existing_clean = existing.replace(' (완료)', '').strip()
        new_clean = new_item.replace(' (완료)', '').strip()

        similarity = calculate_similarity(new_clean, existing_clean)

        # 70% 이상: 확실한 중복
        if similarity >= 0.7:
            return True, existing

        # 30-69%: 애매한 경우 - 사용자에게 물어봄
        if similarity >= 0.3:
            print(f"\n⚠️  비슷한 항목 발견 (유사도: {similarity:.0%})")
            print(f"   기존: \"{existing_clean}\"")
            print(f"   새로: \"{new_clean}\"")
            print(f"\n   같은 작업인가요?")
            print(f"   [y] 예 - 중복으로 처리 (추가 안 함)")
            print(f"   [n] 아니요 - 별개 작업으로 추가")

            choice = input("\n   선택: ").strip().lower()

            if choice == 'y' or choice == 'yes' or choice == '예':
                return True, existing
            else:
                print(f"   → 별개 작업으로 추가합니다.\n")
                return False, None

    return False, None

def create_document(members_data: Dict[str, Dict[str, List[str]]], config: dict,
                   target_date: Optional[datetime] = None) -> str:
    """새 주간 요약 문서 생성 (한 주 요약)"""
    month, week, start_date, end_date = get_week_info(target_date)

    doc = f"# 주간 작업 요약 (2026년 {month}월 {week}주차)\n\n"
    doc += f"> 작성 기간: {start_date} ~ {end_date}\n\n"
    doc += "---\n\n"
    doc += "## 👥 팀원별 작업 현황\n\n"

    team_members = config['team']['members']
    missing_members = []

    for member in team_members:
        doc += f"### {member}\n\n"
        doc += "#### 📋 진행 중인 작업\n"

        if member in members_data and 'weekly_plan' in members_data[member]:
            items = members_data[member]['weekly_plan']
            classified = classify_by_project(items, member, config)

            if '_no_project' in classified and len(classified) == 1:
                # 프로젝트 구분 없음 - 메인 항목만 추가
                for item in classified['_no_project']:
                    doc += f"- {item}\n"
            else:
                # 프로젝트별 구분 - 메인 항목만 추가
                for project, proj_items in classified.items():
                    if project == '_no_project':
                        # 프로젝트 미분류 항목
                        for item in proj_items:
                            doc += f"- {item}\n"
                    else:
                        # 프로젝트 항목
                        doc += f"**{project}**\n"
                        for item in proj_items:
                            doc += f"- {item}\n"
                        doc += "\n"
        else:
            doc += "-\n"
            missing_members.append(member)

        doc += "\n---\n\n"

    # 참고 사항
    doc += "## 📝 참고 사항\n\n"
    if missing_members:
        doc += "⚠️ **한 주 요약 미참여:**\n"
        for member in missing_members:
            doc += f"- {member} 내용이 없습니다.\n"
        doc += "\n"

    doc += "---\n\n"
    doc += f"_마지막 업데이트: {datetime.now().strftime('%Y-%m-%d (%a)')}_\n"

    return doc

def update_document(doc_path: str, members_data: Dict[str, Dict[str, List[str]]],
                   update_type: str, config: dict) -> str:
    """
    기존 문서 업데이트 (수/금 업데이트) - 메인-하위 구조
    update_type: 'wednesday' or 'friday'
    """
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    updated_lines = []

    team_members = config['team']['members']
    updated_members = list(members_data.keys())
    missing_members = [m for m in team_members if m not in updated_members]

    i = 0
    while i < len(lines):
        line = lines[i]

        # 팀원 섹션 시작
        if line.strip().startswith('### ') and '팀원별 작업 현황' not in line:
            current_member = line.strip().replace('###', '').strip()
            updated_lines.append(line)

            # 해당 팀원의 업데이트 처리
            if current_member in members_data:
                i += 1
                # "📋 진행 중인 작업" 섹션 찾기
                while i < len(lines) and '📋 진행 중인 작업' not in lines[i]:
                    updated_lines.append(lines[i])
                    i += 1

                if i < len(lines) and '📋 진행 중인 작업' in lines[i]:
                    updated_lines.append(lines[i])
                    i += 1

                    # 기존 메인 항목과 하위 항목 파싱
                    main_items = {}  # {main_item: [sub_items]}
                    current_main = None
                    current_project = None

                    while i < len(lines) and not lines[i].strip().startswith('#'):
                        stripped = lines[i].strip()

                        if not stripped or stripped == '-':
                            i += 1
                            continue

                        # 프로젝트 헤더
                        if stripped.startswith('**') and stripped.endswith('**'):
                            current_project = stripped
                            i += 1
                            continue

                        # 메인 항목 (들여쓰기 없음)
                        if stripped.startswith('- ') and not lines[i].startswith('  '):
                            current_main = stripped[2:]  # "- " 제거
                            key = (current_project, current_main) if current_project else (None, current_main)
                            if key not in main_items:
                                main_items[key] = []
                            i += 1
                            continue

                        # 하위 항목 (탭 또는 2 spaces 들여쓰기)
                        if (lines[i].startswith('\t- ') or lines[i].startswith('  - ')) and current_main:
                            sub_item = lines[i].strip()[2:]  # "- " 제거
                            key = (current_project, current_main) if current_project else (None, current_main)
                            main_items[key].append(sub_item)
                            i += 1
                            continue

                        i += 1

                    # 새 작업 항목 매칭 및 추가
                    yesterday_items = members_data[current_member].get('yesterday', [])
                    today_items = members_data[current_member].get('today', [])

                    # 메인 항목 리스트 추출 (매칭용)
                    all_main_items = [main for (_, main) in main_items.keys()]

                    # 매칭되지 않은 항목은 "기타"에 추가
                    etc_items = []

                    for item in yesterday_items:
                        matched_main = match_to_main_item(item, all_main_items)
                        if matched_main:
                            # 매칭된 메인 항목 찾기
                            for key in main_items:
                                if key[1] == matched_main:
                                    # 중복 체크
                                    is_dup, existing = check_duplicate_in_subs(
                                        item,
                                        main_items[key]
                                    )

                                    if not is_dup:
                                        # 중복 아님: 추가
                                        main_items[key].append(item)
                                    break
                        else:
                            etc_items.append(item)

                    for item in today_items:
                        matched_main = match_to_main_item(item, all_main_items)
                        if matched_main:
                            # 매칭된 메인 항목 찾기
                            for key in main_items:
                                if key[1] == matched_main:
                                    # 중복 체크
                                    is_dup, _ = check_duplicate_in_subs(item, main_items[key])

                                    if not is_dup:
                                        # 중복 아님: 추가
                                        main_items[key].append(item)
                                    break
                        else:
                            etc_items.append(item)

                    # "기타" 항목 추가 (매칭 안 된 경우)
                    if etc_items:
                        etc_key = (None, '기타')
                        if etc_key not in main_items:
                            main_items[etc_key] = []

                        # "기타" 항목도 중복 체크
                        for item in etc_items:
                            is_dup, existing = check_duplicate_in_subs(item, main_items[etc_key])

                            if not is_dup:
                                # 중복 아님: 추가
                                main_items[etc_key].append(item)

                    # 프로젝트별 분류 적용
                    main_items_by_project = {}
                    for (project, main), subs in main_items.items():
                        if project not in main_items_by_project:
                            main_items_by_project[project] = []
                        main_items_by_project[project].append((main, subs))

                    # 출력
                    projects = list(main_items_by_project.keys())
                    has_multiple_projects = len([p for p in projects if p is not None]) > 1

                    for project in projects:
                        # 프로젝트 헤더 (복수 프로젝트이고 None이 아닌 경우)
                        if project and has_multiple_projects:
                            updated_lines.append(f"{project}")

                        # 메인 항목과 하위 항목
                        for main, subs in main_items_by_project[project]:
                            updated_lines.append(f"- {main}")
                            for sub in subs:
                                updated_lines.append(f"\t- {sub}")

                        # 프로젝트 구분을 위한 빈 줄
                        if project and has_multiple_projects:
                            updated_lines.append("")

                    # 섹션 끝에 빈 줄 추가 (다음 섹션과 구분)
                    updated_lines.append("")

                continue
            else:
                # 업데이트 없는 팀원 - 기존 내용 유지
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('###'):
                    if '## 📝 참고 사항' in lines[i]:
                        break
                    updated_lines.append(lines[i])
                    i += 1
                continue

        # 참고 사항 업데이트
        elif '## 📝 참고 사항' in line:
            updated_lines.append(line)
            updated_lines.append("")

            # 기존 참고 사항 읽기 (보존)
            i += 1
            existing_notes = []
            while i < len(lines) and not lines[i].strip().startswith('---'):
                if lines[i].strip():  # 빈 줄 제외
                    existing_notes.append(lines[i])
                i += 1

            # 기존 참고 사항 유지
            for note in existing_notes:
                updated_lines.append(note)

            # 새 참고 사항 추가
            if missing_members:
                if existing_notes:  # 기존 내용이 있으면 빈 줄 추가
                    updated_lines.append("")
                day_name = '수요일' if update_type == 'wednesday' else '금요일'
                updated_lines.append(f"⚠️ **{day_name} 업데이트 미참여:**")
                for member in missing_members:
                    updated_lines.append(f"- {member} 내용이 없습니다.")
                updated_lines.append("")

            continue

        # 마지막 업데이트 시간
        elif line.strip().startswith('_마지막 업데이트:'):
            updated_lines.append(f"_마지막 업데이트: {datetime.now().strftime('%Y-%m-%d (%a)')}_")
            i += 1
            continue

        updated_lines.append(line)
        i += 1

    return '\n'.join(updated_lines)

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("Usage: python update_weekly_summary.py <slack_text_file> [YYYY-MM-DD]")
        print("  slack_text_file: 슬랙 텍스트 파일 경로")
        print("  YYYY-MM-DD: 선택적으로 기준 날짜 지정 (기본: 오늘)")
        sys.exit(1)

    slack_text_file = sys.argv[1]

    # 날짜 지정 옵션
    target_date = None
    if len(sys.argv) >= 3:
        try:
            target_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
            print(f"📅 지정된 날짜: {target_date.strftime('%Y-%m-%d')}")
        except ValueError:
            print("❌ 날짜 형식 오류. YYYY-MM-DD 형식으로 입력하세요.")
            sys.exit(1)

    # 설정 로드
    config = load_config()

    # 슬랙 텍스트 읽기
    with open(slack_text_file, 'r', encoding='utf-8') as f:
        slack_text = f.read()

    # 파싱
    members_data = parse_slack_text(slack_text, config)

    if not members_data:
        print("❌ 팀원 정보를 파싱할 수 없습니다.")
        sys.exit(1)

    # 업데이트 타입 판단
    has_weekly_plan = any('weekly_plan' in data for data in members_data.values())
    has_yesterday = any('yesterday' in data for data in members_data.values())

    # 파일 경로 (날짜 지정 옵션 적용)
    month, week, _, _ = get_week_info(target_date)
    vault_path = config['obsidian']['vault_path']
    weekly_folder = config['obsidian']['weekly_folder']

    # 연도 폴더 추가
    year = target_date.year if target_date else datetime.now().year
    doc_path = Path(vault_path) / weekly_folder / str(year) / f"{month}월 {week}주차.md"

    print(f"📂 대상 파일: {year}/{month}월 {week}주차.md")

    # 문서 생성 또는 업데이트
    if has_weekly_plan:
        # 새 문서 생성 (한 주 요약) - 파일이 있어도 덮어쓰기
        content = create_document(members_data, config, target_date)
        mode = "생성"
    elif has_yesterday and doc_path.exists():
        # 기존 문서 업데이트 (수/금)
        update_type = 'wednesday'  # 요일 감지 로직 추가 가능
        content = update_document(str(doc_path), members_data, update_type, config)
        mode = "업데이트"
    else:
        print("❌ 문서 모드를 판단할 수 없습니다.")
        print("힌트: '진행 중인 주요 작업' 또는 '어제 한 일' 섹션이 필요합니다.")
        sys.exit(1)

    # 저장
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 주간 요약 문서 {mode} 완료!")
    print(f"\n📄 파일: {doc_path}")
    print(f"📅 업데이트 날짜: {datetime.now().strftime('%Y-%m-%d (%a)')}")
    print(f"\n✏️ 업데이트된 팀원 ({len(members_data)}명):")
    for member in members_data.keys():
        print(f"- {member}")

if __name__ == "__main__":
    main()
