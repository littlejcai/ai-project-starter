"""Advance the project lifecycle after the target stage gates are ready."""
import argparse
import json
import sys

from check_template import ROOT
from project_config import STAGES, lifecycle, load_config, required_gates, task_settings, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--to', choices=STAGES[1:], required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        config = load_config(ROOT)
        validate(config)
        stage_config = lifecycle(config)
        settings = task_settings(config)
        current = stage_config['stage']
        if STAGES.index(args.to) <= STAGES.index(current):
            raise ValueError(f'Lifecycle can only move forward: {current} -> {args.to} is not allowed')
        if config['project_name'] == 'REPLACE_WITH_PROJECT_NAME':
            raise ValueError('Replace project_name before promotion')
        missing = [name for name in required_gates(config, args.to)
                   if config['gates'][name]['status'] != 'configured']
        if missing:
            raise ValueError(f'Target stage {args.to} requires configured gates: {", ".join(missing)}')
        print(f'Ready to promote: {current} -> {args.to}')
        if args.dry_run:
            print('Dry run only; project.config.json was not changed.')
            return 0
        config['schema_version'] = 2
        config['lifecycle'] = stage_config
        config['tasks'] = settings
        config['lifecycle']['stage'] = args.to
        (ROOT / 'project.config.json').write_text(
            json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('Updated project.config.json.')
        print('Update AGENTS.md, README.md, and docs/status.md if their project identity is stale.')
        print('Then run: python3 scripts/verify.py --profile current --readiness')
        return 0
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f'Cannot promote: {exc}\n')


if __name__ == '__main__':
    sys.exit(main())
