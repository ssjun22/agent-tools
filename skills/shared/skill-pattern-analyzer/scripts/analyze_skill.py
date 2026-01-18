#!/usr/bin/env python3
"""
Skill Pattern Analyzer

Analyzes a Claude Code skill directory to extract:
- Folder structure
- SKILL.md writing patterns
- YAML frontmatter patterns
- Best practices
"""

import argparse
import os
import re
from pathlib import Path
from typing import Dict, List, Optional


class SkillAnalyzer:
    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name

    def analyze(self) -> Dict:
        """Run full analysis and return structured results"""
        return {
            'name': self.skill_name,
            'folder_structure': self._analyze_folder_structure(),
            'skill_md': self._analyze_skill_md(),
        }

    def _analyze_folder_structure(self) -> Dict:
        """Analyze directory structure"""
        structure = {
            'has_scripts': False,
            'has_references': False,
            'has_assets': False,
            'scripts': [],
            'references': [],
            'assets': [],
        }

        scripts_dir = self.skill_path / 'scripts'
        if scripts_dir.exists():
            structure['has_scripts'] = True
            structure['scripts'] = [f.name for f in scripts_dir.rglob('*') if f.is_file()]

        references_dir = self.skill_path / 'references'
        if references_dir.exists():
            structure['has_references'] = True
            structure['references'] = self._get_file_tree(references_dir)

        assets_dir = self.skill_path / 'assets'
        if assets_dir.exists():
            structure['has_assets'] = True
            structure['assets'] = self._get_file_tree(assets_dir)

        return structure

    def _get_file_tree(self, directory: Path) -> List[str]:
        """Get file tree relative to directory"""
        files = []
        for item in directory.rglob('*'):
            if item.is_file():
                relative = item.relative_to(directory)
                files.append(str(relative))
        return sorted(files)

    def _analyze_skill_md(self) -> Dict:
        """Analyze SKILL.md content"""
        skill_md_path = self.skill_path / 'SKILL.md'

        if not skill_md_path.exists():
            return {'error': 'SKILL.md not found'}

        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            'frontmatter': self._extract_frontmatter(content),
            'sections': self._extract_sections(content),
            'structure_pattern': self._detect_structure_pattern(content),
            'word_count': len(content.split()),
            'line_count': len(content.splitlines()),
        }

    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter"""
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return {}

        frontmatter_text = frontmatter_match.group(1)
        frontmatter = {}

        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract markdown sections"""
        # Remove frontmatter
        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

        sections = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Match markdown headers (## Header or ### Header)
            header_match = re.match(r'^(#{2,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2)
                sections.append({
                    'level': level,
                    'title': title,
                    'line': i + 1,
                })

        return sections

    def _detect_structure_pattern(self, content: str) -> str:
        """Detect which structure pattern the skill follows"""
        content_lower = content.lower()

        # Check for common patterns
        if 'workflow' in content_lower or 'step-by-step' in content_lower:
            return 'Workflow-Based'
        elif 'task' in content_lower or 'operation' in content_lower:
            return 'Task-Based'
        elif 'guidelines' in content_lower or 'standards' in content_lower:
            return 'Reference/Guidelines'
        elif 'capabilities' in content_lower or 'features' in content_lower:
            return 'Capabilities-Based'
        else:
            return 'Custom/Mixed'

    def generate_markdown_report(self, analysis: Dict) -> str:
        """Generate markdown report from analysis"""
        md = f"# {analysis['name']} - Skill Analysis\n\n"
        md += f"> Analyzed on: {self._get_current_date()}\n\n"

        # Folder Structure
        md += "## Folder Structure\n\n"
        fs = analysis['folder_structure']

        md += "```\n"
        md += f"{analysis['name']}/\n"
        md += f"├── SKILL.md\n"

        if fs['has_scripts']:
            md += f"├── scripts/\n"
            for script in fs['scripts'][:5]:  # Show first 5
                md += f"│   ├── {script}\n"
            if len(fs['scripts']) > 5:
                md += f"│   └── ... ({len(fs['scripts']) - 5} more files)\n"

        if fs['has_references']:
            md += f"├── references/\n"
            for ref in fs['references'][:5]:
                md += f"│   ├── {ref}\n"
            if len(fs['references']) > 5:
                md += f"│   └── ... ({len(fs['references']) - 5} more files)\n"

        if fs['has_assets']:
            md += f"└── assets/\n"
            for asset in fs['assets'][:5]:
                md += f"    ├── {asset}\n"
            if len(fs['assets']) > 5:
                md += f"    └── ... ({len(fs['assets']) - 5} more files)\n"

        md += "```\n\n"

        # YAML Frontmatter
        skill_md = analysis['skill_md']
        if 'frontmatter' in skill_md and skill_md['frontmatter']:
            md += "## YAML Frontmatter\n\n"
            md += "```yaml\n"
            for key, value in skill_md['frontmatter'].items():
                md += f"{key}: {value}\n"
            md += "```\n\n"

        # Structure Pattern
        if 'structure_pattern' in skill_md:
            md += f"## Structure Pattern\n\n"
            md += f"**Detected Pattern**: {skill_md['structure_pattern']}\n\n"

        # Section Structure
        if 'sections' in skill_md and skill_md['sections']:
            md += "## Section Structure\n\n"
            for section in skill_md['sections']:
                indent = "  " * (section['level'] - 2)
                md += f"{indent}- {section['title']} (Level {section['level']})\n"
            md += "\n"

        # Statistics
        md += "## Statistics\n\n"
        md += f"- **Word Count**: {skill_md.get('word_count', 'N/A')}\n"
        md += f"- **Line Count**: {skill_md.get('line_count', 'N/A')}\n"
        md += f"- **Scripts**: {len(fs['scripts'])}\n"
        md += f"- **References**: {len(fs['references'])}\n"
        md += f"- **Assets**: {len(fs['assets'])}\n\n"

        # Best Practices Observations
        md += "## Best Practices Observations\n\n"

        practices = []

        if fs['has_scripts']:
            practices.append("✓ Uses scripts for reusable automation")
        if fs['has_references']:
            practices.append("✓ Separates detailed documentation into references")
        if fs['has_assets']:
            practices.append("✓ Includes assets for template/output files")

        if skill_md.get('word_count', 0) < 5000:
            practices.append("✓ Keeps SKILL.md concise (< 5k words)")
        elif skill_md.get('word_count', 0) > 10000:
            practices.append("⚠ SKILL.md is quite long (> 10k words) - consider moving content to references")

        frontmatter = skill_md.get('frontmatter', {})
        if 'name' in frontmatter and 'description' in frontmatter:
            practices.append("✓ Includes required frontmatter (name, description)")

        for practice in practices:
            md += f"- {practice}\n"

        md += "\n"

        return md

    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description='Analyze Claude Code skill patterns')
    parser.add_argument('skill_path', help='Path to the skill directory')
    parser.add_argument('-o', '--output', help='Output file path (optional)')

    args = parser.parse_args()

    analyzer = SkillAnalyzer(args.skill_path)
    analysis = analyzer.analyze()
    report = analyzer.generate_markdown_report(analysis)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ Analysis saved to: {args.output}")
    else:
        print(report)


if __name__ == '__main__':
    main()
