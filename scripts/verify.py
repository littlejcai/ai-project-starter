"""Run explicit checks and preserve evidence. No business checks are preconfigured."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

from check_template import ROOT, check
from project_config import GATES, lifecycle, load_config, required_gates, validate


def git_value(*args):
    try:
        result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True,
                                text=True, encoding='utf-8', errors='replace', timeout=5)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def execute(name, gate, folder):
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    command = [sys.executable if item == '{python}' else item for item in gate['command']]
    command[0] = shutil.which(command[0]) or command[0]
    log = folder / f'{name}.log'
    record = {'name': name, 'status': 'failed', 'command': command,
              'started_at': started, 'exit_code': None, 'log': str(log.relative_to(ROOT))}
    with log.open('w', encoding='utf-8') as output:
        try:
            result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                    timeout=gate.get('timeout_seconds', 300), shell=False)
            record['exit_code'] = result.returncode
            record['status'] = 'passed' if result.returncode == 0 else 'failed'
        except subprocess.TimeoutExpired:
            record['status'] = 'timeout'
            output.write('\nRunner: timed out; command must clean up any child services.\n')
        except OSError as exc:
            record['status'] = 'execution_error'
            output.write(f'Runner: {exc}\n')
    record['elapsed_seconds'] = round(time.monotonic() - start, 3)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=['demo', 'current', 'quick', 'full'], required=True)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    folder = ROOT / 'artifacts' / (now.strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    report = {'profile': args.profile, 'started_at': now.isoformat(),
              'scope': 'isolated example only' if args.profile == 'demo' else 'configured automatic checks only',
              'git_head': git_value('rev-parse', 'HEAD'),
              'git_status_before': git_value('status', '--porcelain'), 'checks': []}
    exit_code = 0
    try:
        config = load_config(ROOT)
        validate(config)
        stage = lifecycle(config)['stage']
        report['project_stage'] = stage
        report['config_snapshot'] = config
        errors = check()
        report['checks'].append({'name': 'template_integrity',
                                 'status': 'failed' if errors else 'passed', 'errors': errors})
        if errors:
            exit_code = 1
        if args.profile == 'demo' or (args.profile == 'current' and stage == 'template'):
            selected = {'demo': {'status': 'configured', 'command': [
                '{python}', '-m', 'unittest', 'discover', '-s', 'examples/registration',
                '-p', 'test_*.py', '-v'], 'timeout_seconds': 60}}
            if args.profile == 'current':
                report['scope'] = 'current template stage; isolated example only'
        else:
            if args.profile == 'current':
                names = required_gates(config)
                report['scope'] = f'current {stage} stage required automatic checks only'
            else:
                names = GATES[:2] if args.profile == 'quick' else GATES
            selected = {name: config['gates'][name] for name in names}
            if config['project_name'] == 'REPLACE_WITH_PROJECT_NAME':
                report['checks'].append({'name': 'project_identity', 'status': 'unconfigured'})
                exit_code = 1
        executed = 0
        for name, gate in selected.items():
            if gate['status'] == 'configured':
                executed += 1
                record = execute(name, gate, folder)
                if record['status'] != 'passed':
                    exit_code = 1
            else:
                record = {'name': name, 'status': gate['status'], 'reason': gate.get('reason', '')}
                if gate['status'] == 'unconfigured' or args.profile == 'current':
                    exit_code = 1
            report['checks'].append(record)
            print(f'{name}: {record["status"]}')
        if not executed:
            report['error'] = 'No configured checks executed'
            exit_code = 1
    except (ValueError, OSError, TypeError) as exc:
        report['error'] = str(exc)
        exit_code = 2
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    report['git_status_after'] = git_value('status', '--porcelain')
    report['result'] = 'passed' if exit_code == 0 else 'failed'
    report['exit_code'] = exit_code
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{args.profile}: {report["result"]}; scope: {report["scope"]}')
    print(f'Report: {folder / "report.json"}')
    if 'error' in report:
        print(report['error'])
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
