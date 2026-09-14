"""Run explicit checks and preserve evidence. No business checks are preconfigured."""
import argparse
from datetime import datetime, timezone
import json
import html
import os
import re
import shutil
import subprocess
import sys
import time
import uuid

from check_template import ROOT, check
from doctor import inspect_project
from project_config import GATES, lifecycle, load_config, required_gates, validate, valid_task_id


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


def write_summary(report, folder):
    """Publish a small index without copying commands, config, errors or raw logs."""
    def cell(value):
        return html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ')

    lines = [
        '# 自动检查摘要', '',
        f'- Run ID：{folder.name}',
        f'- 任务：{cell(report.get("task_id") or "未关联")}',
        f'- Profile / 阶段：{cell(report["profile"])} / {cell(report.get("project_stage", "unknown"))}',
        f'- 范围：{cell(report["scope"])}',
        f'- 结果 / 退出码：{report["result"]} / {report["exit_code"]}',
        f'- 尝试执行命令数：{report["automatic_commands_executed"]}（不是测试用例数）',
        f'- UTC：{report["started_at"]} → {report["completed_at"]}',
        f'- Git 提交：{cell(report.get("git_head") or "无 Git 提交")}',
        f'- 工作区有改动（运行前 / 后）：{report["worktree_dirty_before"]} / {report["worktree_dirty_after"]}',
        f'- 执行环境：{cell(report["runner_environment"])}（检查工具环境，不代表业务技术栈）',
    ]
    if report.get('ci_run_url'):
        lines.append(f'- CI 运行：{cell(report["ci_run_url"])}')
    lines += ['', '| 检查 | 状态 | 退出码 | 耗时（秒） |', '|---|---|---|---|']
    for item in report['checks']:
        lines.append('| ' + ' | '.join(cell(item.get(key, '—')) for key in
                                      ['name', 'status', 'exit_code', 'elapsed_seconds']) + ' |')
    if report.get('error'):
        lines += ['', '存在执行或配置错误，详细原因见本地 report.json。']
    lines += ['', '业务验收未由本摘要判定；人工、浏览器和真机结果需另有证据。',
              '详细命令、配置、错误和日志保存在同一运行目录的 report.json 与日志文件中，CI 默认仅归档本摘要。',
              '脏工作区仅标记有改动，不保存代码快照；重要验收需固定版本或另存变更证据。', '']
    (folder / 'summary.md').write_text('\n'.join(lines), encoding='utf-8')


def read_report(run_id, check_name=None, tail=None):
    """Read only selected evidence; no commands or configuration in the default view."""
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', run_id):
        raise ValueError('Expected a run ID, not a path')
    artifacts = (ROOT / 'artifacts').resolve()
    artifacts.relative_to(ROOT.resolve())
    folder = (artifacts / run_id).resolve()
    if folder.parent != artifacts:
        raise ValueError('Run must be inside artifacts/')
    source = (folder / 'report.json').resolve()
    if source.parent != folder:
        raise ValueError('Report must be inside its run directory')
    report = json.loads(source.read_text(encoding='utf-8'))
    if not isinstance(report, dict) or not isinstance(report.get('checks'), list):
        raise ValueError('Invalid report structure')
    checks = report['checks']
    if any(not isinstance(item, dict) for item in checks):
        raise ValueError('Invalid check record')
    if report.get('error'):
        checks = checks + [{'name': 'configuration', 'status': 'failed', 'errors': [report['error']]}]
    selected = ([item for item in checks if item.get('name') == check_name] if check_name is not None
                else [item for item in checks if item.get('status') not in {'passed', 'not_applicable'}
                      or item.get('warnings')])
    if check_name is not None and len(selected) != 1:
        raise ValueError('Expected exactly one check with that name')
    output = {key: report.get(key) for key in [
        'profile', 'project_stage', 'task_id', 'result', 'exit_code', 'scope', 'git_head',
        'completed_at', 'worktree_dirty_before', 'worktree_dirty_after', 'automatic_commands_executed']}
    output.update(run_id=run_id, business_acceptance='not_assessed',
                  view='selected check' if check_name is not None else 'failures and warnings', checks=[])
    for item in selected:
        row = {key: item[key] for key in ['name', 'status', 'exit_code', 'elapsed_seconds', 'log', 'manifest_checked'] if key in item}
        for key in ['errors', 'warnings']:
            values = item.get(key, [])
            row[key + '_count'] = len(values) if isinstance(values, list) else 1
            if check_name is not None and values:
                values = values if isinstance(values, list) else [values]
                row[key] = [str(value)[:1000] for value in values[:10]]
                row[key + '_truncated'] = len(values) > 10 or any(len(str(value)) > 1000 for value in values[:10])
        if check_name is not None and item.get('reason'):
            row['reason'] = str(item['reason'])[:1000]
        output['checks'].append(row)
    if tail is not None:
        log_name = selected[0].get('log')
        if not isinstance(log_name, str):
            raise ValueError('Selected check has no log')
        log = (ROOT / log_name).resolve()
        if log.parent != folder or log.suffix != '.log':
            raise ValueError('Log must belong to the selected run')
        with log.open('rb') as stream:
            stream.seek(0, 2)
            size = stream.tell()
            stream.seek(max(0, size - 16384))
            lines = stream.read().decode('utf-8', errors='replace').splitlines()
        excerpt = '\n'.join(lines[-tail:])
        output['log_excerpt'] = excerpt[-12000:]
        output['log_excerpt_truncated'] = size > 16384 or len(lines) > tail or len(excerpt) > 12000
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--profile', choices=['current', 'quick', 'full'])
    mode.add_argument('--report', metavar='RUN_ID', help='Read an existing report; do not run checks')
    parser.add_argument('--readiness', action='store_true', help='Include doctor checks in this run')
    parser.add_argument('--strict-manifest', action='store_true', help='Include readiness and template hashes')
    parser.add_argument('--check', dest='check_name', help='Read one check from --report')
    parser.add_argument('--tail', type=int, help='Explicitly read 1-200 trailing log lines for --check')
    parser.add_argument('--task', help='Associate an existing task ID without editing the task file')
    args = parser.parse_args()
    if args.report is not None:
        if args.task is not None or args.readiness or args.strict_manifest:
            parser.error('--task/--readiness/--strict-manifest require --profile')
        if args.tail is not None and (not args.check_name or not 1 <= args.tail <= 200):
            parser.error('--tail requires --check and a value between 1 and 200')
        try:
            read_report(args.report, args.check_name, args.tail)
            return 0  # Reading a failed report succeeds; the report keeps its original result.
        except (OSError, ValueError, TypeError, KeyError) as exc:
            parser.exit(2, f'Cannot read report: {exc}\n')
    if args.check_name is not None or args.tail is not None:
        parser.error('--check/--tail require --report')
    now = datetime.now(timezone.utc)
    folder = ROOT / 'artifacts' / (now.strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
    folder.mkdir(parents=True)
    report = {'report_schema_version': 1, 'profile': args.profile, 'started_at': now.isoformat(),
              'readiness_requested': args.readiness or args.strict_manifest,
              'strict_manifest_requested': args.strict_manifest,
              'task_id': None, 'automatic_commands_executed': 0,
              'business_acceptance': 'not_assessed',
              'runner_environment': f'{sys.platform}; Python {sys.version.split()[0]}',
              'scope': 'configured automatic checks only',
              'git_head': git_value('rev-parse', 'HEAD'),
              'git_status_before': git_value('status', '--porcelain'), 'checks': []}
    exit_code = 0
    try:
        config = load_config(ROOT)
        validate(config)
        if args.task is not None:
            if not valid_task_id(config, args.task) or not (ROOT / 'docs/tasks' / f'{args.task}.md').is_file():
                raise ValueError('The task ID must match project configuration and an existing task file')
            report['task_id'] = args.task
        stage = lifecycle(config)['stage']
        report['project_stage'] = stage
        report['config_snapshot'] = config
        errors = check(config=config)
        report['checks'].append({'name': 'template_integrity',
                                 'status': 'failed' if errors else 'passed', 'errors': errors})
        if errors:
            exit_code = 1
        if args.readiness or args.strict_manifest:
            readiness_errors, warnings = inspect_project(config, strict_manifest=args.strict_manifest)
            report['checks'].append({'name': 'project_readiness',
                                     'status': 'failed' if readiness_errors else 'passed',
                                     'manifest_checked': args.strict_manifest and stage == 'template',
                                     'errors': readiness_errors, 'warnings': warnings})
            print(f'project_readiness: {"failed" if readiness_errors else "passed"}')
            for warning in warnings:
                print(f'WARN: {warning}')
            if readiness_errors:
                exit_code = 1
        template_current = args.profile == 'current' and stage == 'template'
        if args.profile == 'current':
            names = required_gates(config)
            report['scope'] = ('template structure and declared tooling checks only; no business tests'
                               if template_current else f'current {stage} stage required automatic checks only')
        else:
            names = GATES[:2] if args.profile == 'quick' else GATES
        selected = {name: config['gates'][name] for name in names}
        if not template_current and config['project_name'] == 'REPLACE_WITH_PROJECT_NAME':
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
        report['automatic_commands_executed'] = executed
        if not executed and not (template_current and not names):
            report['error'] = 'No configured checks executed'
            exit_code = 1
    except (ValueError, OSError, TypeError, KeyError) as exc:
        report['error'] = str(exc)
        exit_code = 2
    report['completed_at'] = datetime.now(timezone.utc).isoformat()
    report['git_status_after'] = git_value('status', '--porcelain')
    for when in ['before', 'after']:
        state = report[f'git_status_{when}']
        report[f'worktree_dirty_{when}'] = None if state is None else bool(state)
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        report['ci_run_url'] = '{}/{}/actions/runs/{}'.format(
            os.environ.get('GITHUB_SERVER_URL', 'https://github.com'),
            os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GITHUB_RUN_ID', ''))
    report['result'] = 'passed' if exit_code == 0 else 'failed'
    report['exit_code'] = exit_code
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_summary(report, folder)
    print(f'{args.profile}: {report["result"]}; scope: {report["scope"]}')
    print(f'Report: {folder / "report.json"}')
    print(f'Summary: {folder / "summary.md"}')
    if 'error' in report:
        print(report['error'])
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
