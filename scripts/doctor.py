"""Check project lifecycle, configured gates, tasks, links, and optional template hashes."""
import argparse
import hashlib
from pathlib import Path
import re
import sys

from check_template import ROOT, check, project_files
from project_config import lifecycle, load_config, required_gates, task_settings, validate, valid_task_id


def distribution_files(root):
    for path in project_files(root):
        if path.name not in {'MANIFEST.sha256', '.DS_Store'}:
            yield path


def check_manifest(root):
    errors = []
    manifest = root / 'MANIFEST.sha256'
    if not manifest.is_file():
        return ['Missing MANIFEST.sha256']
    entries = {}
    for number, line in enumerate(manifest.read_text(encoding='utf-8').splitlines(), 1):
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        if not match:
            errors.append(f'MANIFEST.sha256:{number}: invalid entry')
            continue
        digest, name = match.groups()
        if name in entries:
            errors.append(f'MANIFEST.sha256:{number}: duplicate path {name}')
        entries[name] = digest
    actual_names = {path.relative_to(root).as_posix() for path in distribution_files(root)}
    for name in sorted(actual_names - set(entries)):
        errors.append(f'MANIFEST.sha256: unlisted file {name}')
    for name in sorted(set(entries) - actual_names):
        errors.append(f'MANIFEST.sha256: missing file {name}')
    for name in sorted(actual_names & set(entries)):
        digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if digest != entries[name]:
            errors.append(f'MANIFEST.sha256: checksum mismatch {name}')
    return errors


def inspect_tasks(root, config):
    errors = []
    warnings = []
    seen = set()
    active = []
    settings = task_settings(config)
    statuses = settings['statuses']
    for path in sorted((root / 'docs' / 'tasks').glob('*.md')):
        if path.name == 'TEMPLATE.md':
            continue
        content = path.read_text(encoding='utf-8')
        lines = content.splitlines()
        heading = re.fullmatch(r'# ([^ ]+) · .+', lines[0] if lines else '')
        if not heading:
            errors.append(f'{path.relative_to(root)}: expected heading "# TASK-ID · title"')
            continue
        task_id = heading.group(1)
        if not valid_task_id(config, task_id):
            errors.append(f'{path.relative_to(root)}: task ID does not match configured pattern: {task_id}')
        if path.stem != task_id:
            errors.append(f'{path.relative_to(root)}: filename must match task ID {task_id}')
        if task_id in seen:
            errors.append(f'{path.relative_to(root)}: duplicate task ID {task_id}')
        seen.add(task_id)
        status_line = next((line for line in lines[1:8] if line.startswith('状态：')), None)
        status = status_line[3:].strip() if status_line else None
        if status not in statuses:
            errors.append(f'{path.relative_to(root)}: missing or invalid task status')
        elif status not in settings['inactive_statuses']:
            active.append(task_id)
        if re.search(r'\{\{[A-Z_]+\}\}', content):
            errors.append(f'{path.relative_to(root)}: unresolved template placeholder')
    if len(active) > 1:
        warnings.append('Multiple active tasks: ' + ', '.join(active))
    if len(active) == 1:
        status_text = (root / 'docs' / 'status.md').read_text(encoding='utf-8')
        if active[0] not in status_text:
            warnings.append(f'docs/status.md does not mention active task {active[0]}')
    return errors, warnings


def inspect_project(config, root=ROOT, *, strict_manifest=False):
    """Doctor-specific checks; caller supplies the validated config and checks structure."""
    errors, warnings = [], []
    stage = lifecycle(config)['stage']
    try:
        if stage != 'template' and config['project_name'] == 'REPLACE_WITH_PROJECT_NAME':
            errors.append('project_name must be replaced before leaving template stage')
        for name in required_gates(config):
            if config['gates'][name]['status'] != 'configured':
                errors.append(f'Current stage {stage} requires configured gate: {name}')
        if stage in {'application', 'release'}:
            empty = [name for name, command in config['runtime_commands'].items() if not command]
            if empty:
                warnings.append('Runtime commands still empty: ' + ', '.join(empty))
        task_errors, task_warnings = inspect_tasks(root, config)
        errors.extend(task_errors)
        warnings.extend(task_warnings)
        if strict_manifest and stage == 'template':
            errors.extend(check_manifest(root))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(str(exc))
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict-manifest', action='store_true',
                        help='Verify distribution hashes while lifecycle stage is template')
    args = parser.parse_args()
    errors, warnings, stage = [], [], 'unknown'
    try:
        config = load_config(ROOT)
        validate(config)
        stage = lifecycle(config)['stage']
        errors.extend(check(config=config))
        extra_errors, warnings = inspect_project(config, strict_manifest=args.strict_manifest)
        errors.extend(extra_errors)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        errors.append(str(exc))
    for message in errors:
        print('FAIL:', message)
    for message in warnings:
        print('WARN:', message)
    result = 'FAIL' if errors else ('WARN' if warnings else 'PASS')
    print(f'Project doctor: {result} (stage={stage})')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
