"""Shared project configuration validation for starter tooling."""
import json
from pathlib import Path
import re


GATES = ['quality', 'unit', 'integration', 'build', 'e2e']
STAGES = ['template', 'discovery', 'application', 'release']
DEFAULT_TASK_ID_PATTERN = r'(?:FEAT|BUG|CHORE|M[0-9]+)(?:-[A-Z0-9]+)*-[0-9]{3,6}'
DEFAULT_TASK_STATUSES = ['待开始', '澄清中', '开发中', '验证中', '阻塞', '已完成']


def load_config(root):
    return json.loads((Path(root) / 'project.config.json').read_text(encoding='utf-8'))


def lifecycle(config):
    if config.get('schema_version') == 1:
        return {
            'stage': 'template',
            'required_gates': {
                'template': [],
                'discovery': ['quality', 'unit'],
                'application': ['quality', 'unit', 'integration', 'build'],
                'release': GATES.copy(),
            },
        }
    return config['lifecycle']


def task_settings(config):
    if config.get('schema_version') == 1:
        return {
            'id_pattern': DEFAULT_TASK_ID_PATTERN,
            'statuses': DEFAULT_TASK_STATUSES.copy(),
            'default_status': DEFAULT_TASK_STATUSES[0],
            'inactive_statuses': [DEFAULT_TASK_STATUSES[0], DEFAULT_TASK_STATUSES[-1]],
        }
    return config['tasks']


def validate_command(command, label):
    if not isinstance(command, list) or any(not isinstance(item, str) or not item for item in command):
        raise ValueError(f'{label} must be an array of nonempty strings')


def validate(config):
    if not isinstance(config, dict) or config.get('schema_version') not in {1, 2}:
        raise ValueError('Expected schema_version 1 or 2 object')
    if not isinstance(config.get('project_name'), str) or not config['project_name'].strip():
        raise ValueError('project_name must be a nonempty string')

    runtime = config.get('runtime_commands')
    if not isinstance(runtime, dict) or not runtime:
        raise ValueError('runtime_commands must be a nonempty object')
    for name, command in runtime.items():
        if not isinstance(name, str) or not name:
            raise ValueError('runtime command names must be nonempty strings')
        validate_command(command, f'runtime_commands.{name}')

    gates = config.get('gates')
    if not isinstance(gates, dict) or set(gates) != set(GATES):
        raise ValueError('gates must contain exactly: ' + ', '.join(GATES))
    for name, gate in gates.items():
        if not isinstance(gate, dict):
            raise ValueError(f'{name}: gate must be an object')
        status = gate.get('status')
        command = gate.get('command')
        if status not in {'configured', 'unconfigured', 'not_applicable'}:
            raise ValueError(f'{name}: invalid status')
        validate_command(command, f'{name}.command')
        if status == 'configured' and not command:
            raise ValueError(f'{name}: configured command is empty')
        if status != 'configured' and command:
            raise ValueError(f'{name}: inactive gate must not contain a command')
        if status == 'not_applicable' and not str(gate.get('reason', '')).strip():
            raise ValueError(f'{name}: not_applicable requires a reason')
        timeout = gate.get('timeout_seconds', 300)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 3600:
            raise ValueError(f'{name}: timeout_seconds must be >0 and <=3600')

    stage_config = lifecycle(config)
    if not isinstance(stage_config, dict) or stage_config.get('stage') not in STAGES:
        raise ValueError('lifecycle.stage must be one of: ' + ', '.join(STAGES))
    requirements = stage_config.get('required_gates')
    if not isinstance(requirements, dict) or set(requirements) != set(STAGES):
        raise ValueError('lifecycle.required_gates must contain exactly: ' + ', '.join(STAGES))
    for stage, names in requirements.items():
        if not isinstance(names, list) or any(name not in GATES for name in names):
            raise ValueError(f'lifecycle.required_gates.{stage} contains an invalid gate')
        if len(names) != len(set(names)):
            raise ValueError(f'lifecycle.required_gates.{stage} contains duplicate gates')

    settings = task_settings(config)
    pattern = settings.get('id_pattern') if isinstance(settings, dict) else None
    statuses = settings.get('statuses') if isinstance(settings, dict) else None
    if not isinstance(pattern, str) or not pattern or len(pattern) > 512:
        raise ValueError('tasks.id_pattern must be a nonempty regex no longer than 512 characters')
    try:
        re.compile(pattern, re.ASCII)
    except re.error as exc:
        raise ValueError(f'tasks.id_pattern is invalid: {exc}') from exc
    if not isinstance(statuses, list) or not statuses or any(
            not isinstance(status, str) or not status.strip() for status in statuses):
        raise ValueError('tasks.statuses must be a nonempty array of nonempty strings')
    if len(statuses) != len(set(statuses)):
        raise ValueError('tasks.statuses contains duplicate values')
    default_status = settings.get('default_status')
    inactive = settings.get('inactive_statuses')
    if default_status not in statuses:
        raise ValueError('tasks.default_status must be listed in tasks.statuses')
    if not isinstance(inactive, list) or any(status not in statuses for status in inactive):
        raise ValueError('tasks.inactive_statuses must contain only configured statuses')
    if len(inactive) != len(set(inactive)):
        raise ValueError('tasks.inactive_statuses contains duplicate values')


def required_gates(config, stage=None):
    stage_config = lifecycle(config)
    return stage_config['required_gates'][stage or stage_config['stage']]


def valid_task_id(config, task_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', task_id, re.ASCII):
        return False
    return re.fullmatch(task_settings(config)['id_pattern'], task_id, re.ASCII) is not None
