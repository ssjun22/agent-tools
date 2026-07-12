#!/usr/bin/env python3
"""
daily-work-log 이월 스크립트 — 어제(또는 최근) 일지에서 미완료 항목을
결정론으로 이월해 오늘 일지 초안을 생성한다.

역할 분담: 파싱·날짜 연산·backlog 분류·트리 이동은 이 스크립트가 전담하고,
LLM은 실행 결과(JSON)의 예외 상황 판단만 맡는다.

Usage:
    python3 migrate.py [--config CONFIG_PATH] [--write] [--force]

    (기본)    dry-run — 오늘 파일 초안과 요약을 JSON으로 출력
    --write   디렉토리 생성 + 오늘 파일 저장 (이미 존재하면 거부)
    --force   --write 시 기존 파일 덮어쓰기 허용

Output(JSON):
    {"summary": {...}, "today_path": "...", "draft": "<전체 초안>", "written": bool}
    오류 시 {"error": "..."} + exit 1, 파일 존재 거부는 {"error": "EXISTS", ...} + exit 3

이월 규칙(정본 — SKILL.md는 이 규칙을 재서술하지 않는다):
  - 대상 섹션: TODOs / Backlogs / Issues / Notes. Meetings·Articles·Retrospect는 이월하지 않음.
  - 미완료([ ]) 항목만 이월. [x]는 미완료 자식이 있을 때만 컨텍스트로 보존.
  - origin date: [ ] 항목에 (M/D~)가 없으면 소스 파일 날짜를 부여, 있으면 보존.
  - 날짜 표시 계층 규칙: 가장 가까운 미완료 조상과 같은 날짜면 생략(부모에만 표시).
  - backlog 분류: TODOs의 최상위 [ ] 트리 중 origin date가 오늘 기준 14일 이상
    경과한 것은 트리째 Backlogs로 이동. [x] 루트 트리는 이동하지 않는다.
    소스의 기존 Backlogs 항목은 그대로 Backlogs에 남는다.
  - 연도 추론: (M/D~)가 미래가 되면 작년으로 해석.
  - 템플릿 문구(placeholder) 항목은 이월하지 않는다.
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from date_helper import get_daily_paths  # noqa: E402

BACKLOG_AGE_DAYS = 14
TAB = "\t"

PLACEHOLDER_PATTERNS = [
    "오늘 할 일을 작성하세요",
    "발생한 문제를 기록하세요",
    "발생한 이슈를 기록하세요",
    "자유롭게 메모를 작성하세요",
    "회의 내용을 기록하세요",
    "관심있는 기사 URL을 입력하세요",
]

DATE_RE = re.compile(r"\s*\((\d{1,2})/(\d{1,2})~\)\s*$")
CHECKBOX_RE = re.compile(r"^- \[([ xX])\] (.*)$")
BULLET_RE = re.compile(r"^- (.*)$")


class Node:
    def __init__(self, depth, checked, text):
        self.depth = depth          # 0-based
        self.checked = checked      # None=plain bullet, False=[ ], True=[x]
        self.text = text            # 날짜 annotation 제거된 본문
        self.own_date = None        # "M/D" (원본 표기 보존, 0패딩 없음)
        self.children = []


def indent_width(raw):
    """탭=4로 환산한 들여쓰기 폭."""
    width = 0
    for ch in raw:
        if ch == "\t":
            width += 4
        elif ch == " ":
            width += 1
        else:
            break
    return width


def parse_items(lines):
    """섹션 본문 라인들을 Node 트리(루트 리스트)로 파싱."""
    roots, stack = [], []  # stack: [(width, node)]
    for line in lines:
        if not line.strip():
            continue
        stripped = line.lstrip(" \t")
        width = indent_width(line)
        m = CHECKBOX_RE.match(stripped)
        if m:
            checked = m.group(1) in ("x", "X")
            body = m.group(2)
        else:
            m2 = BULLET_RE.match(stripped)
            if not m2:
                continue  # bullet이 아닌 산문 라인은 무시
            checked, body = None, m2.group(1)
        node = Node(0, checked, body)
        dm = DATE_RE.search(body)
        if dm:
            node.own_date = f"{int(dm.group(1))}/{int(dm.group(2))}"
            node.text = DATE_RE.sub("", body)
        while stack and stack[-1][0] >= width:
            stack.pop()
        if stack:
            parent = stack[-1][1]
            node.depth = parent.depth + 1
            parent.children.append(node)
        else:
            roots.append(node)
        stack.append((width, node))
    return roots


def split_sections(text):
    """'## 헤딩' 기준으로 {섹션명: [본문 라인]} 분리."""
    sections, current, buf = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = buf
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = buf
    return sections


def is_placeholder(text):
    return any(p in text for p in PLACEHOLDER_PATTERNS)


def prune(node, section):
    """이월 대상만 남긴다. 반환: 유지된 Node 또는 None."""
    kept_children = [c for c in (prune(c, section) for c in node.children) if c]
    node.children = kept_children
    if is_placeholder(node.text):
        return None
    if section == "Issues" and "(예:" in node.text:
        return None
    if node.checked is False:
        return node
    # [x]·plain bullet은 미완료 자손이 있을 때만 컨텍스트로 유지
    return node if kept_children else None


def stamp_dates(node, source_md, ancestor_date=None):
    """미완료 항목에 origin date 부여.

    기존 날짜는 보존하고, 없는 항목은 가장 가까운 미완료 조상의 날짜를
    상속한다(조상도 없으면 소스 파일 날짜). 조상보다 새 날짜가 찍혀
    계층 표시가 깨지는 것을 막는다.
    """
    next_ancestor = ancestor_date
    if node.checked is False:
        if node.own_date is None:
            node.own_date = ancestor_date or source_md
        next_ancestor = node.own_date
    for c in node.children:
        stamp_dates(c, source_md, next_ancestor)


def parse_md_date(md, today):
    m, d = (int(x) for x in md.split("/"))
    try:
        candidate = date(today.year, m, d)
    except ValueError:
        return None
    if candidate > today:
        candidate = date(today.year - 1, m, d)
    return candidate


def age_days(node, today):
    if node.own_date is None:
        return 0
    parsed = parse_md_date(node.own_date, today)
    return (today - parsed).days if parsed else 0


def render(node, depth, ancestor_date, out):
    """트리를 탭 들여쓰기로 재조립. 날짜는 계층 규칙에 따라 표시."""
    if node.checked is None:
        line = f"- {node.text}"
        next_ancestor = ancestor_date
    else:
        mark = "x" if node.checked else " "
        show = node.checked is False and node.own_date and node.own_date != ancestor_date
        suffix = f" ({node.own_date}~)" if show else ""
        line = f"- [{mark}] {node.text}{suffix}"
        next_ancestor = node.own_date if node.checked is False else ancestor_date
    out.append(TAB * depth + line)
    for c in node.children:
        render(c, depth + 1, next_ancestor, out)


def render_groups(groups):
    """[(프로젝트 헤더 or None, [트리])] → 라인 리스트."""
    out = []
    for header, trees in groups:
        if not trees:
            continue
        if header is not None:
            out.append(f"- {header}")
            for t in trees:
                render(t, 1, None, out)
        else:
            for t in trees:
                render(t, 0, None, out)
    return out


def group_by_project(roots):
    """TODO 섹션 루트를 (프로젝트 헤더, 하위 트리)로 재구성."""
    groups = []
    for r in roots:
        if r.checked is None:
            groups.append((r.text, r.children))
        else:
            groups.append((None, [r]))
    return groups


def classify_backlog(groups, today):
    """프로젝트 그룹별로 (todos, backlogs) 분리. 이동은 트리 단위."""
    todo_groups, backlog_groups, moved = [], [], []
    for header, trees in groups:
        stay, move = [], []
        for t in trees:
            if t.checked is False and age_days(t, today) >= BACKLOG_AGE_DAYS:
                move.append(t)
                moved.append(t.text)
            else:
                stay.append(t)
        if stay:
            todo_groups.append((header, stay))
        if move:
            backlog_groups.append((header, move))
    return todo_groups, backlog_groups, moved


def build_draft(paths, migrated):
    """assets/default-template.md 골격에 이월 결과를 채운다."""
    template = (SKILL_DIR / "assets" / "default-template.md").read_text(encoding="utf-8")
    projects = paths["config"]["project_sections"]
    meetings_projects = [p for p in projects if p != "기타"]

    if migrated and migrated["todos"]:
        todos = "\n".join(render_groups(migrated["todos"]))
    else:
        todos = "\n\n".join(
            f"- {p}\n{TAB}- [ ] (오늘 할 일을 작성하세요)" for p in projects)
    meetings = "\n\n".join(
        f"- {p}\n{TAB}- (회의 내용을 기록하세요)" for p in meetings_projects) \
        or "- (회의 내용을 기록하세요)"

    text = template.replace("{PROJECT_TODOS}", todos)
    text = text.replace("{PROJECT_MEETINGS}", meetings)

    if migrated:
        if migrated["issues"]:
            body = []
            for t in migrated["issues"]:
                render(t, 0, None, body)
            text = replace_section(text, "Issues", "\n".join(body))
        if migrated["notes"]:
            body = []
            for t in migrated["notes"]:
                render(t, 0, None, body)
            text = replace_section(text, "Notes", "\n".join(body))
        if migrated["backlogs"]:
            text = text.rstrip() + "\n\n## Backlogs\n" + \
                "\n".join(render_groups(migrated["backlogs"])) + "\n"
    return text


def replace_section(text, name, body):
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        out.append(lines[i])
        if lines[i].strip() == f"## {name}":
            out.append(body)
            out.append("")
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        i += 1
    return "\n".join(out) + "\n"


def count_unchecked(trees):
    n = 0
    for t in trees:
        if t.checked is False:
            n += 1
        n += count_unchecked(t.children)
    return n


def migrate(source_path, source_date_str, today):
    text = Path(source_path).read_text(encoding="utf-8")
    sections = split_sections(text)
    sd = datetime.strptime(source_date_str, "%Y-%m-%d").date()
    source_md = f"{sd.month}/{sd.day}"

    def parse_and_prep(name):
        roots = parse_items(sections.get(name, []))
        kept = [r for r in (prune(r, name) for r in roots) if r]
        for r in kept:
            stamp_dates(r, source_md)
        return kept

    todo_groups = group_by_project(parse_and_prep("TODOs"))
    old_backlog_groups = group_by_project(parse_and_prep("Backlogs"))
    todo_groups, new_backlog_groups, moved = classify_backlog(todo_groups, today)

    # 기존 Backlogs 뒤에 신규 이동분을 프로젝트 헤더 기준으로 병합
    merged = {h: list(ts) for h, ts in old_backlog_groups}
    order = [h for h, _ in old_backlog_groups]
    for h, ts in new_backlog_groups:
        if h in merged:
            merged[h].extend(ts)
        else:
            merged[h] = list(ts)
            order.append(h)
    backlog_groups = [(h, merged[h]) for h in order]

    return {
        "todos": todo_groups,
        "backlogs": backlog_groups,
        "issues": parse_and_prep("Issues"),
        "notes": parse_and_prep("Notes"),
        "moved_to_backlog": moved,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(SKILL_DIR / "config.json"))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    try:
        paths = get_daily_paths(args.config)
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    today = datetime.strptime(paths["today"]["date"], "%Y-%m-%d").date()
    today_path = Path(paths["today"]["path"])

    source = None
    if paths["yesterday"]["exists"]:
        source = (paths["yesterday"]["path"], paths["yesterday"]["date"])
    elif paths["recent"]["exists"]:
        source = (paths["recent"]["path"], paths["recent"]["date"])

    migrated = None
    if source:
        try:
            migrated = migrate(source[0], source[1], today)
        except Exception as e:
            print(json.dumps(
                {"error": f"이월 파싱 실패({source[0]}): {e}"}, ensure_ascii=False))
            sys.exit(1)

    draft = build_draft(paths, migrated)

    written = False
    if args.write:
        if today_path.exists() and not args.force:
            print(json.dumps({
                "error": "EXISTS",
                "message": "오늘 파일이 이미 존재합니다. 덮어쓰려면 --force.",
                "today_path": str(today_path),
            }, ensure_ascii=False))
            sys.exit(3)
        today_path.parent.mkdir(parents=True, exist_ok=True)
        today_path.write_text(draft, encoding="utf-8")
        written = True

    summary = {
        "today": paths["today"]["date"],
        "source": source[1] if source else None,
        "source_kind": ("yesterday" if source and paths["yesterday"]["exists"]
                        else "recent" if source else "template"),
        "counts": {
            "todos": count_unchecked([t for _, ts in migrated["todos"] for t in ts]) if migrated else 0,
            "backlogs": count_unchecked([t for _, ts in migrated["backlogs"] for t in ts]) if migrated else 0,
            "issues": count_unchecked(migrated["issues"]) if migrated else 0,
            "notes": count_unchecked(migrated["notes"]) if migrated else 0,
        },
        "moved_to_backlog": migrated["moved_to_backlog"] if migrated else [],
    }
    print(json.dumps({
        "summary": summary,
        "today_path": str(today_path),
        "draft": draft,
        "written": written,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
