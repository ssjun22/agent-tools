#!/usr/bin/env python3
"""
Sync Manager for task-manager skill
Handles bidirectional sync between tasks.md and Jira
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from jira_client import JiraClient, load_config


class TaskParser:
    """Parse tasks.md file"""

    @staticmethod
    def parse_tasks_md(file_path: Path) -> List[Dict[str, Any]]:
        """
        Parse tasks.md and extract task data using stateful parsing.

        Returns:
            List of task dicts with fields: index, title, assignee, priority, status, jira_key, description, etc.
        """
        if not file_path.exists():
            return []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        tasks = []
        current_task = None
        in_description = False

        # Pattern for task header: ### [#N] or ### [#완료N]
        task_header_re = re.compile(r'^###\s+\[#(완료)?(\d+)\]\s+(.+)')
        # Pattern for fields: - **Name**: Value
        field_re = re.compile(r'^\s*-\s+\*\*(.+?)\*\*:\s*(.*)')

        for line in lines:
            header_match = task_header_re.match(line)
            if header_match:
                if current_task:
                    tasks.append(current_task)
                
                current_task = {
                    'index': header_match.group(2),
                    'is_completed': header_match.group(1) is not None,
                    'title': header_match.group(3).strip(),
                    'assignee': None,
                    'reporter': None,
                    'priority': None,
                    'status': None,
                    'jira_key': None,
                    'description': [],
                    '작업 기한': None,
                    'Jira Parent': None,
                    '연관 업무': None
                }
                in_description = False
                continue

            if current_task:
                # If we are in the description block, everything indented belongs here
                if in_description:
                    if line.startswith('  ') or line.startswith('\t') or line.strip() == "":
                        current_task['description'].append(line.rstrip('\r\n'))
                        continue
                    # Non-indented line might be a new top-level field or end of description
                    # We continue to field checking below

                field_match = field_re.match(line)
                # Ensure it's a top-level field (starts with '-')
                if field_match and line.lstrip().startswith('-'):
                    field_name = field_match.group(1)
                    field_value = field_match.group(2).strip()
                    
                    if field_name == '담당자':
                        current_task['assignee'] = field_value
                    elif field_name == '보고자':
                        current_task['reporter'] = field_value
                    elif field_name == '우선순위':
                        current_task['priority'] = field_value
                    elif field_name == '상태':
                        current_task['status'] = field_value
                    elif field_name == 'Jira Key':
                        current_task['jira_key'] = field_value
                    elif field_name == '작업 기한':
                        current_task['작업 기한'] = field_value
                    elif field_name == 'Jira Parent':
                        current_task['Jira Parent'] = field_value
                    elif field_name == '연관 업무':
                        current_task['연관 업무'] = field_value
                    
                    if field_name == '설명':
                        in_description = True
                        if field_value:
                            current_task['description'].append(field_value)
                    else:
                        in_description = False
                    continue
                
                # If no field match and we are in description, it might be a multi-line wrap
                if in_description:
                    current_task['description'].append(line.rstrip('\r\n'))

        if current_task:
            tasks.append(current_task)

        # Post-process description: join and cleaned
        for task in tasks:
            # Drop empty strings from start/end
            desc_lines = task['description']
            while desc_lines and not desc_lines[0].strip():
                desc_lines.pop(0)
            while desc_lines and not desc_lines[-1].strip():
                desc_lines.pop()
            
            task['description'] = "\n".join(desc_lines)

        return tasks

    @staticmethod
    def update_task_field(
        file_path: Path,
        task_index: str,
        field_name: str,
        new_value: str
    ) -> bool:
        """
        Update a specific field in tasks.md

        Args:
            file_path: Path to tasks.md
            task_index: Task index (e.g., "3")
            field_name: Field name (e.g., "상태", "Jira Key")
            new_value: New field value

        Returns:
            True on success
        """
        if not file_path.exists():
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find task and update field
        # Pattern: ### [#3] ... \n- **상태**: 대기
        task_pattern = rf'(###\s+\[#{task_index}\].+?)(- \*\*{re.escape(field_name)}\*\*:\s*)(.+?)(\n)'

        def replacer(match):
            return f"{match.group(1)}{match.group(2)}{new_value}{match.group(4)}"

        updated_content, count = re.subn(task_pattern, replacer, content, flags=re.MULTILINE | re.DOTALL)

        if count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            return True

        return False


class SyncManager:
    """Manage sync between tasks.md and Jira"""

    def __init__(self, tasks_md_path: Path):
        self.tasks_md_path = tasks_md_path
        self.jira_client = JiraClient()
        self.config = load_config()
        self.parser = TaskParser()

    def pull_from_jira(self) -> Dict[str, Any]:
        """
        Pull changes from Jira and update tasks.md
        Jira takes precedence in case of conflicts

        Returns:
            Summary dict with updated tasks
        """
        tasks = self.parser.parse_tasks_md(self.tasks_md_path)

        updated_tasks = []
        errors = []

        for task in tasks:
            if not task['jira_key']:
                continue

            # Fetch from Jira
            jira_issue = self.jira_client.get_issue(task['jira_key'])

            if not jira_issue:
                errors.append(f"[#{task['index']}] Failed to fetch {task['jira_key']}")
                continue

            # Map Jira status to local status
            jira_status_local = self._map_jira_status_to_local(jira_issue['status'])

            # Check for conflicts
            changes = []

            if task['status'] != jira_status_local:
                changes.append(f"상태: {task['status']} → {jira_status_local}")
                self.parser.update_task_field(
                    self.tasks_md_path,
                    task['index'],
                    '상태',
                    jira_status_local
                )

            # Map Jira reporter back to local key
            jira_reporter_local = self._map_jira_user_to_local(jira_issue.get('reporter_id'), jira_issue.get('reporter'))
            if task['reporter'] != jira_reporter_local and jira_reporter_local is not None:
                changes.append(f"보고자: {task['reporter']} → {jira_reporter_local}")
                self.parser.update_task_field(
                    self.tasks_md_path,
                    task['index'],
                    '보고자',
                    jira_reporter_local
                )

            # Link Sync (Jira -> Local)
            jira_links = jira_issue.get('issuelinks', [])
            related_keys = []
            for link in jira_links:
                if link.get('type', {}).get('name') == 'Relates':
                    # Extract key from inward or outward issue
                    other_key = link.get('inwardIssue', {}).get('key') or link.get('outwardIssue', {}).get('key')
                    if other_key:
                        related_keys.append(other_key)
            
            if related_keys:
                resolved_indices = self._resolve_jira_keys_to_local_indices(related_keys, tasks)
                current_local_links = self._parse_local_indices(task.get('연관 업무', ''))
                
                # Merge new indices from Jira
                new_indices = sorted(list(set(current_local_links) | set(resolved_indices)))
                new_value = ", ".join([f"#{idx}" for idx in new_indices]) if new_indices else "없음"
                
                if set(current_local_links) != set(new_indices):
                    changes.append(f"연관 업무: {task.get('연관 업무', '없음')} → {new_value}")
                    self.parser.update_task_field(
                        self.tasks_md_path,
                        task['index'],
                        '연관 업무',
                        new_value
                    )

            if changes:
                updated_tasks.append({
                    'index': task['index'],
                    'title': task['title'],
                    'jira_key': task['jira_key'],
                    'changes': changes
                })

        return {
            'updated_count': len(updated_tasks),
            'updated_tasks': updated_tasks,
            'errors': errors
        }

    def push_to_jira_links(self) -> Dict[str, Any]:
        """
        Push local links (연관 업무) to Jira 'Relates' links
        """
        tasks = self.parser.parse_tasks_md(self.tasks_md_path)
        linked_count = 0
        errors = []

        # Create mapping of local index to jira key
        index_to_key = {t['index']: t['jira_key'] for t in tasks if t['jira_key']}

        for task in tasks:
            if not task['jira_key'] or not task.get('연관 업무'):
                continue
            
            indices = self._parse_local_indices(task['연관 업무'])
            for idx in indices:
                target_key = index_to_key.get(idx)
                if target_key:
                    # Create link in Jira
                    success = self.jira_client.create_issue_link(task['jira_key'], target_key)
                    if success:
                        linked_count += 1
                    else:
                        errors.append(f"Failed to link {task['jira_key']} to {target_key}")

        return {
            'linked_count': linked_count,
            'errors': errors
        }

    def _parse_local_indices(self, value: str) -> List[str]:
        """Parse #1, #2 from string"""
        if not value or value == "없음":
            return []
        return re.findall(r'#(\d+)', value)

    def _resolve_jira_keys_to_local_indices(self, keys: List[str], tasks: List[Dict[str, Any]]) -> List[str]:
        """Resolve Jira keys to local indices from current tasks list"""
        key_to_index = {t['jira_key']: t['index'] for t in tasks if t['jira_key']}
        return [key_to_index[k] for k in keys if k in key_to_index]

    def _map_jira_user_to_local(self, accountId: Optional[str], displayName: Optional[str] = None) -> Optional[str]:
        """Map Jira AccountId back to .env key (e.g. JIRA_ASSIGNEE_D)"""
        if not accountId:
            return "없음"
        
        # Reverse mapping: find key in assignee_mapping that matches this accountId
        for key, val in self.jira_client.assignee_mapping.items():
            if val == accountId:
                # We prefer keys like 'JIRA_ASSIGNEE_D' but also 'D' or 'me'
                # If there are multiple keys, let's pick the one starting with JIRA_ASSIGNEE_ for consistency
                if key.startswith('JIRA_ASSIGNEE_'):
                    return key
        
        # Fallback to displayName if no mapping found
        return displayName if displayName else "알 수 없음"

    def _map_jira_status_to_local(self, jira_status: str) -> str:
        """Map Jira status to local status (direct match now)"""
        return jira_status


def main():
    """CLI for testing sync manager"""
    import sys

    # Find tasks.md
    script_dir = Path(__file__).parent.parent
    tasks_md = script_dir / "tasks.md"

    if not tasks_md.exists():
        print("tasks.md not found")
        sys.exit(1)

    manager = SyncManager(tasks_md)

    if len(sys.argv) < 2:
        print("Usage: python sync_manager.py <command>")
        print("Commands: pull, push_links")
        sys.exit(1)

    command = sys.argv[1]

    if command == "pull":
        result = manager.pull_from_jira()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif command == "push_links":
        result = manager.push_to_jira_links()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
