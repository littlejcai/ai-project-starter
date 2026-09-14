"""Check required files and relative Markdown links; not a business test."""
from pathlib import Path
import os
import re
import sys
from urllib.parse import unquote

from project_config import load_config, validate, lifecycle

ROOT = Path(__file__).resolve().parents[1]
CORE_REQUIRED = [
    'README.md', 'AGENTS.md', 'project.config.json', 'docs/index.md',
    'docs/product.md', 'docs/architecture.md', 'docs/status.md',
    'docs/testing.md', 'docs/workflow.md', 'docs/tasks/TEMPLATE.md',
    'docs/verification-setup.md',
    'scripts/verify.py', 'scripts/new_task.py', 'scripts/project_config.py',
    'scripts/doctor.py', 'scripts/promote_project.py', 'scripts/test_framework.py',
    'scripts/read_doc.py',
]
TEMPLATE_REQUIRED = ['scripts/update_manifest.py', 'TEMPLATE-VALIDATION.md']


EXCLUDED_PARTS = {'.git', 'artifacts', '__pycache__', 'node_modules', '.venv', 'dist', 'build'}


def project_files(root):
    """Prune excluded directories before walking into them; never follow symlinks."""
    for folder, directories, files in os.walk(root, topdown=True, followlinks=False):
        base = Path(folder)
        directories[:] = sorted(name for name in directories
                                if name not in EXCLUDED_PARTS and not (base / name).is_symlink())
        for name in sorted(files):
            path = base / name
            if not path.is_symlink():
                yield path


def check(root=ROOT, *, config=None):
    # Internal callers pass their already validated configuration for this run only.
    errors = []
    stage = 'template'
    try:
        if config is None:
            config = load_config(root)
            validate(config)
        stage = lifecycle(config)['stage']
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(f'Invalid project.config.json: {exc}')
    required = CORE_REQUIRED + (TEMPLATE_REQUIRED if stage == 'template' else [])
    for name in required:
        if not (root / name).is_file():
            errors.append(f'Missing required file: {name}')
    for path in project_files(root):
        if path.suffix != '.md':
            continue
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
