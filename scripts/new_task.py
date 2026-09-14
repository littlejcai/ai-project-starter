"""Create one task without overwriting an existing task."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import re

from project_config import load_config, task_settings, validate, valid_task_id

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task_id', help='For example FEAT-001, FEAT-ID-001, or M0-001')
    parser.add_argument('title')
    config = load_config(ROOT)
    validate(config)
    settings = task_settings(config)
    parser.add_argument('--status', choices=settings['statuses'], default=settings['default_status'])
    args = parser.parse_args()
    if not valid_task_id(config, args.task_id):
        parser.error('Task ID does not match project.config.json tasks.id_pattern')
    if not args.title.strip() or any(c in args.title for c in '\r\n'):
        parser.error('Title must be one nonempty line')
    template = (ROOT / 'docs/tasks/TEMPLATE.md').read_text(encoding='utf-8')
    replacements = {'TASK_ID': args.task_id, 'TITLE': args.title.strip(), 'STATUS': args.status,
                    'DATE': datetime.now(timezone.utc).isoformat()}
    content = re.sub(r'\{\{(TASK_ID|TITLE|STATUS|DATE)\}\}',
                     lambda match: replacements[match.group(1)], template)
    destination = ROOT / 'docs/tasks' / f'{args.task_id}.md'
    try:
        with destination.open('x', encoding='utf-8') as stream:
            stream.write(content)
    except FileExistsError:
        parser.exit(1, f'Refusing to overwrite: {destination}\n')
    print(f'Created: {destination}')
    print('Update docs/status.md to reference this task when it becomes active.')


if __name__ == '__main__':
    main()
