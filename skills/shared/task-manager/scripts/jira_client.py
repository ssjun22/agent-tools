#!/usr/bin/env python3
"""
Jira API Client for task-manager skill
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path


def load_env():
    """Load .env file from skill root directory"""
    script_dir = Path(__file__).parent.parent
    env_file = script_dir / ".env"

    if not env_file.exists():
        return False

    # Simple .env parser (key=value format)
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
    return True


def load_config() -> Dict[str, Any]:
    """Load config.json for status/priority mappings"""
    script_dir = Path(__file__).parent.parent
    config_file = script_dir / "config.json"

    if not config_file.exists():
        # Default mappings
        return {
            "jira": {
                "project_key": "GLENS",
                "status_mapping": {
                    "대기": "To Do",
                    "진행중": "In Progress",
                    "완료": "Done"
                },
                "priority_mapping": {
                    "높음": "High",
                    "중간": "Medium",
                    "낮음": "Low"
                }
            }
        }

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


class JiraClient:
    def __init__(self):
        load_env()
        self.config = load_config()

        self.base_url = os.getenv('JIRA_URL')
        self.email = os.getenv('JIRA_EMAIL')
        self.api_token = os.getenv('JIRA_API_TOKEN')
        self.project_key = os.getenv('JIRA_PROJECT_KEY', self.config['jira'].get('project_key', 'GLENS'))

        # Load labels from ENV (comma separated)
        labels_env = os.getenv('JIRA_LABELS', '')
        self.labels = [l.strip() for l in labels_env.split(',') if l.strip()] if labels_env else self.config['jira'].get('labels', [])

        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError("Jira credentials not configured. Check .env file.")

        self.auth = (self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Load assignee mapping from ENV (JIRA_ASSIGNEE_*)
        self.assignee_mapping = {}
        for key, value in os.environ.items():
            if key.startswith('JIRA_ASSIGNEE_'):
                # Extract the name (e.g., ME, A, B, 최영준)
                name = key[len('JIRA_ASSIGNEE_'):]
                # Store both the full key and the name part
                self.assignee_mapping[key] = value
                
                if name.upper() == 'ME':
                    self.assignee_mapping['me'] = value
                else:
                    self.assignee_mapping[name] = value

    def _markdown_to_adf(self, text: str) -> dict:
        """
        Convert Markdown to Atlassian Document Format (ADF) with nested list support.
        """
        if not text:
            return {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": []}]
            }

        import re
        text = text.replace('\\n', '\n')
        lines = text.split('\n')
        
        doc_content = []
        list_stack = [] # Stack of (type, indent_level, list_node)

        def create_text_nodes(t: str):
            parts = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*)', t)
            nodes = []
            for part in parts:
                if not part: continue
                node = {"type": "text", "text": part}
                if part.startswith('**') and part.endswith('**') and len(part) > 4:
                    node["text"] = part[2:-2]; node["marks"] = [{"type": "strong"}]
                elif part.startswith('*') and part.endswith('*') and len(part) > 2:
                    node["text"] = part[1:-1]; node["marks"] = [{"type": "em"}]
                nodes.append(node)
            return nodes or [{"type": "text", "text": ""}]

        def close_lists_to_level(level):
            while list_stack and list_stack[-1][1] > level:
                list_stack.pop()

        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                close_lists_to_level(-1)
                continue

            indent = len(line) - len(stripped)
            bullet_match = re.match(r'^([-*]|\d+\.)\s+(.*)', stripped)
            
            if bullet_match:
                marker = bullet_match.group(1)
                content = bullet_match.group(2)
                list_type = "orderedList" if marker.endswith('.') else "bulletList"
                
                # Check if we need to close nested lists
                close_lists_to_level(indent)
                
                # Check if we need to start a new list or use existing
                if not list_stack or list_stack[-1][1] < indent or list_stack[-1][0] != list_type:
                    new_list = {"type": list_type, "content": []}
                    if not list_stack:
                        doc_content.append(new_list)
                    else:
                        # Append to last item of parent list
                        parent_list = list_stack[-1][2]
                        if parent_list["content"]:
                            parent_list["content"][-1]["content"].append(new_list)
                        else:
                            # Edge case: empty bullet point followed by indent
                            parent_list["content"].append({"type": "listItem", "content": [new_list]})
                    list_stack.append((list_type, indent, new_list))
                
                # Add list item
                item_node = {
                    "type": "listItem",
                    "content": [{"type": "paragraph", "content": create_text_nodes(content)}]
                }
                list_stack[-1][2]["content"].append(item_node)
            else:
                close_lists_to_level(-1)
                doc_content.append({"type": "paragraph", "content": create_text_nodes(stripped)})

        return {"type": "doc", "version": 1, "content": doc_content}

    def create_issue(
        self,
        summary: str,
        description: str,
        assignee: str,
        priority: str,
        status: str,
        parent: Optional[str] = None,
        duedate: Optional[str] = None,
        reporter: Optional[str] = None
    ) -> Optional[str]:
        """
        Create Jira issue and return issue key (e.g., GLENS-123)
        """
        url = f"{self.base_url}/rest/api/3/issue"

        # Strip [#N] or [#완료N] from summary
        import re
        clean_summary = re.sub(r'^\[#.*?\]\s*', '', summary)

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": clean_summary,
                "description": self._markdown_to_adf(description),
                "issuetype": {"name": "Task"}
            }
        }

        if parent:
            payload["fields"]["parent"] = {"key": parent}

        if duedate:
            payload["fields"]["duedate"] = duedate

        # Add priority if provided
        if priority:
            jira_priority = self.config['jira']['priority_mapping'].get(priority, 'Medium')
            payload["fields"]["priority"] = {"name": jira_priority}

        # Add labels if configured
        if self.labels:
            payload["fields"]["labels"] = self.labels

        # Add assignee if mapping exists
        if assignee in self.assignee_mapping:
            payload["fields"]["assignee"] = {"accountId": self.assignee_mapping[assignee]}

        # Add reporter if mapping exists
        if reporter and reporter in self.assignee_mapping:
            payload["fields"]["reporter"] = {"accountId": self.assignee_mapping[reporter]}

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                auth=self.auth,
                timeout=10
            )
            response.raise_for_status()
            issue_key = response.json().get('key')
            return issue_key
        except requests.exceptions.RequestException as e:
            print(f"Error creating Jira issue: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def update_issue(
        self,
        issue_key: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        duedate: Optional[str] = None,
        reporter: Optional[str] = None
    ) -> bool:
        """
        Update Jira issue fields

        Args:
            issue_key: Jira issue key (GLENS-XXX)
            status: New status (대기/진행중/완료)
            priority: New priority (높음/중간/낮음)
            assignee: New assignee name
            duedate: New due date (YYYY-MM-DD)

        Returns:
            True on success, False on failure
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        fields = {}

        if priority:
            jira_priority = self.config['jira']['priority_mapping'].get(priority, 'Medium')
            fields['priority'] = {'name': jira_priority}

        if assignee:
            if assignee in self.assignee_mapping:
                fields['assignee'] = {'accountId': self.assignee_mapping[assignee]}

        if duedate:
            fields['duedate'] = duedate

        if reporter:
            if reporter in self.assignee_mapping:
                fields['reporter'] = {'accountId': self.assignee_mapping[reporter]}

        if fields:
            try:
                response = requests.put(
                    url,
                    json={"fields": fields},
                    headers=self.headers,
                    auth=self.auth,
                    timeout=10
                )
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error updating Jira issue {issue_key}: {e}")
                return False

        # Handle status transition separately
        if status:
            status_list = self.config['jira'].get('status_list', [])
            if status in status_list:
                return self._transition_issue(issue_key, status)
            else:
                print(f"Warning: Status '{status}' not in approved status_list. Attempting direct transition.")
                return self._transition_issue(issue_key, status)

        return True

    def get_transitions(self, issue_key: str) -> Optional[list]:
        """Get available transitions for an issue"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        try:
            response = requests.get(url, headers=self.headers, auth=self.auth, timeout=10)
            response.raise_for_status()
            return response.json().get('transitions', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transitions for {issue_key}: {e}")
            return None

    def _transition_issue(self, issue_key: str, target_status: str) -> bool:
        """Transition issue to target status"""
        transitions = self.get_transitions(issue_key)
        if not transitions:
            return False

        # Find transition ID for target status
        transition_id = None
        for t in transitions:
            if t['to']['name'] == target_status:
                transition_id = t['id']
                break

        if not transition_id:
            print(f"No transition found to '{target_status}' for {issue_key}")
            print(f"Available: {[t['to']['name'] for t in transitions]}")
            return False

        # Perform transition
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        try:
            response = requests.post(
                url,
                json={"transition": {"id": transition_id}},
                headers=self.headers,
                auth=self.auth,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error transitioning Jira issue {issue_key}: {e}")
            return False

    def create_issue_link(self, inward_key: str, outward_key: str, link_type: str = "Relates") -> bool:
        """
        Create a link between two issues.
        Default link type is 'Relates' (Atlassian default name).
        """
        url = f"{self.base_url}/rest/api/3/issueLink"
        payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": inward_key},
            "outwardIssue": {"key": outward_key}
        }
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                auth=self.auth,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error linking issues {inward_key} and {outward_key}: {e}")
            return False

    def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """
        Get Jira issue details

        Args:
            issue_key: Jira issue key (GLENS-XXX)

        Returns:
            Issue data dict or None on failure
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"

        try:
            response = requests.get(url, headers=self.headers, auth=self.auth, timeout=10)
            response.raise_for_status()
            data = response.json()

            assignee_data = data['fields'].get('assignee')
            assignee_name = assignee_data.get('displayName') if assignee_data else None
            assignee_id = assignee_data.get('accountId') if assignee_data else None

            reporter_data = data['fields'].get('reporter')
            reporter_name = reporter_data.get('displayName') if reporter_data else None
            reporter_id = reporter_data.get('accountId') if reporter_data else None

            return {
                'key': issue_key,
                'summary': data['fields']['summary'],
                'status': data['fields']['status']['name'],
                'priority': data['fields']['priority']['name'],
                'assignee': assignee_name,
                'assignee_id': assignee_id,
                'reporter': reporter_name,
                'reporter_id': reporter_id,
                'duedate': data['fields'].get('duedate'),
                'parent': data['fields'].get('parent', {}).get('key'),
                'issuelinks': data['fields'].get('issuelinks', [])
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Jira issue {issue_key}: {e}")
            return None

    def search_users(self, query: str) -> Optional[list]:
        """
        Search for Jira users by name or email
        """
        url = f"{self.base_url}/rest/api/3/user/search"
        params = {"query": query}

        try:
            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                auth=self.auth,
                timeout=10
            )
            response.raise_for_status()
            users = response.json()
            return [
                {
                    "accountId": u.get("accountId"),
                    "displayName": u.get("displayName"),
                    "emailAddress": u.get("emailAddress")
                }
                for u in users
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error searching users: {e}")
            return None

    def search_issues(self, jql: str) -> Optional[list]:
        """Search issues using JQL"""
        url = f"{self.base_url}/rest/api/3/search"
        payload = {
            "jql": jql,
            "maxResults": 50,
            "fields": ["summary", "status", "priority", "assignee", "issuetype", "parent"]
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                auth=self.auth,
                timeout=10
            )
            response.raise_for_status()
            issues = response.json().get('issues', [])
            return [
                {
                    "key": i.get("key"),
                    "summary": i["fields"].get("summary"),
                    "status": i["fields"]["status"].get("name"),
                    "issuetype": i["fields"]["issuetype"].get("name"),
                    "parent": i["fields"].get("parent", {}).get("key")
                }
                for i in issues
            ]
        except requests.exceptions.RequestException as e:
            print(f"Error searching issues: {e}")
            return None


def main():
    """CLI for testing Jira client"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python jira_client.py <command> [args...]")
        print("Commands: create, update, get, search, search_issues, transitions")
        sys.exit(1)

    client = JiraClient()
    command = sys.argv[1]

    if command == "create":
        # Example: python jira_client.py create "Test Task" "Description" "A" "높음" "OPEN" "PARENT-123" "2024-12-31"
        if len(sys.argv) < 7:
            print("Usage: python jira_client.py create <summary> <desc> <assignee> <priority> <status> [parent] [duedate]")
            sys.exit(1)

        parent = sys.argv[7] if len(sys.argv) > 7 else None
        duedate = sys.argv[8] if len(sys.argv) > 8 else None

        issue_key = client.create_issue(
            summary=sys.argv[2],
            description=sys.argv[3],
            assignee=sys.argv[4],
            priority=sys.argv[5],
            status=sys.argv[6],
            parent=parent,
            duedate=duedate,
            reporter=sys.argv[9] if len(sys.argv) > 9 else None
        )

        if issue_key:
            print(f"Created: {issue_key}")
        else:
            print("Failed to create issue")

    elif command == "update":
        # Example: python jira_client.py update AR-123 "개발 진행" "높음" "me" "2026-02-12"
        if len(sys.argv) < 3:
            print("Usage: python jira_client.py update <issue_key> [status] [priority] [assignee] [duedate]")
            sys.exit(1)

        status = sys.argv[3] if len(sys.argv) > 3 else None
        priority = sys.argv[4] if len(sys.argv) > 4 else None
        assignee = sys.argv[5] if len(sys.argv) > 5 else None
        duedate = sys.argv[6] if len(sys.argv) > 6 else None
        reporter = sys.argv[7] if len(sys.argv) > 7 else None

        success = client.update_issue(
            issue_key=sys.argv[2],
            status=status,
            priority=priority,
            assignee=assignee,
            duedate=duedate,
            reporter=reporter
        )
        if success:
            print(f"Updated: {sys.argv[2]}")
        else:
            print(f"Failed to update issue {sys.argv[2]}")

    elif command == "get":
        # Example: python jira_client.py get GLENS-123
        if len(sys.argv) < 3:
            print("Usage: python jira_client.py get <issue_key>")
            sys.exit(1)

        issue = client.get_issue(sys.argv[2])
        if issue:
            print(json.dumps(issue, indent=2, ensure_ascii=False))
        else:
            print("Failed to fetch issue")

    elif command == "search":
        # Example: python jira_client.py search "Youngjun"
        if len(sys.argv) < 3:
            print("Usage: python jira_client.py search <query>")
            sys.exit(1)

        users = client.search_users(sys.argv[2])
        if users:
            print(json.dumps(users, indent=2, ensure_ascii=False))
        else:
            print("No users found or search failed")

    elif command == "search_issues":
        # Example: python jira_client.py search_issues "project = AR AND issuetype = Epic"
        if len(sys.argv) < 3:
            print("Usage: python jira_client.py search_issues <jql>")
            sys.exit(1)

        issues = client.search_issues(sys.argv[2])
        if issues:
            print(json.dumps(issues, indent=2, ensure_ascii=False))
        else:
            print("No issues found or search failed")

    elif command == "transitions":
        # Example: python jira_client.py transitions GLENS-123
        if len(sys.argv) < 3:
            print("Usage: python jira_client.py transitions <issue_key>")
            sys.exit(1)

        transitions = client.get_transitions(sys.argv[2])
        if transitions:
            formatted = [{"id": t["id"], "name": t["to"]["name"]} for t in transitions]
            print(json.dumps(formatted, indent=2, ensure_ascii=False))
        else:
            print("Failed to fetch transitions")


if __name__ == "__main__":
    main()
