"""Check required files and relative Markdown links; not a business test."""
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CORE_REQUIRED = [
    'README.md', 'AGENTS.md', 'project.config.json', 'docs/index.md',
    'docs/product.md', 'docs/architecture.md', 'docs/status.md',
    'docs/testing.md', 'docs/workflow.md', 'docs/tasks/TEMPLATE.md',
    'docs/verification-setup.md', 'contracts/README.md',
    'scripts/verify.py', 'scripts/new_task.py', 'scripts/project_config.py',
    'scripts/doctor.py', 'scripts/promote_project.py', 'scripts/test_framework.py',
]
TEMPLATE_REQUIRED = ['scripts/update_manifest.py', 'TEMPLATE-VALIDATION.md']


def check(root=ROOT):
    errors = []
    stage = 'template'
    try:
        config = json.loads((root / 'project.config.json').read_text(encoding='utf-8'))
        if not isinstance(config, dict) or config.get('schema_version') not in {1, 2}:
            errors.append('project.config.json: expected schema_version 1 or 2 object')
        elif config.get('schema_version') == 2:
            stage = config.get('lifecycle', {}).get('stage', 'template')
    except (OSError, ValueError) as exc:
        errors.append(f'Invalid project.config.json: {exc}')
    required = CORE_REQUIRED + (TEMPLATE_REQUIRED if stage == 'template' else [])
    for name in required:
        if not (root / name).is_file():
            errors.append(f'Missing required file: {name}')
    excluded = {'node_modules', '.git', '.venv', 'artifacts', 'dist', 'build', '__pycache__'}
    def markdown_files(folder):
        for path in folder.iterdir():
            if path.is_symlink():
                continue
            if path.is_dir() and path.name not in excluded:
                yield from markdown_files(path)
            elif path.is_file() and path.suffix == '.md':
                yield path
    for path in markdown_files(root):
        content = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', content):
            if target.startswith(('#', '//')) or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            relative = unquote(target.split('#', 1)[0].split('?', 1)[0])
            if relative and not (path.parent / relative).exists():
                errors.append(f'{path.relative_to(root)}: broken local link {target}')
    return errors


if __name__ == '__main__':
    failures = check()
    for error in failures:
        print('FAIL:', error)
    print(f'Template integrity: {"FAIL" if failures else "PASS"} (not business acceptance)')
    sys.exit(1 if failures else 0)
