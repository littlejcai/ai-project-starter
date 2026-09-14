"""Regression checks for the template tooling, in disposable copies."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FrameworkChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            '.git', 'artifacts', '__pycache__', 'node_modules', '.venv'))
        config_path = self.root / 'project.config.json'
        config = json.loads(config_path.read_text(encoding='utf-8'))
        config['project_name'] = 'REPLACE_WITH_PROJECT_NAME'
        config['lifecycle'] = {
            'stage': 'template',
            'required_gates': {
                'template': [],
                'discovery': ['quality', 'unit'],
                'application': ['quality', 'unit', 'integration', 'build'],
                'release': ['quality', 'unit', 'integration', 'build', 'e2e'],
            },
        }
        config['tasks'] = {
            'id_pattern': r'(?:FEAT|BUG|CHORE|M[0-9]+)(?:-[A-Z0-9]+)*-[0-9]{3,6}',
            'statuses': ['待开始', '澄清中', '开发中', '验证中', '阻塞', '已完成'],
            'default_status': '待开始',
            'inactive_statuses': ['待开始', '已完成'],
        }
        for gate in config['gates'].values():
            gate.update(status='unconfigured', command=[], reason='')
        config_path.write_text(json.dumps(config), encoding='utf-8')

    def run_script(self, name, *args, env=None):
        variables = os.environ.copy()
        variables.update(env or {})
        return subprocess.run([sys.executable, str(self.root / 'scripts' / name), *args],
                              cwd=self.root, env=variables, capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=30)

    def configure(self, mutate=None):
        path = self.root / 'project.config.json'
        config = json.loads(path.read_text(encoding='utf-8'))
        config['project_name'] = 'tooling-self-test'
        for gate in config['gates'].values():
            gate.update(status='configured', command=['{python}', '-c', 'pass'])
        if mutate:
            mutate(config)
        path.write_text(json.dumps(config), encoding='utf-8')

    def report(self):
        paths = list((self.root / 'artifacts').glob('*/report.json'))
        self.assertTrue(paths)
        return json.loads(max(paths, key=lambda p: p.stat().st_mtime_ns).read_text(encoding='utf-8'))

    def test_current_template_has_no_business_tests(self):
        self.assertEqual(self.run_script('check_template.py').returncode, 0)
        result = self.run_script('verify.py', '--profile', 'current')
        self.assertEqual(result.returncode, 0, result.stdout)
        report = self.report()
        self.assertEqual(report['project_stage'], 'template')
        self.assertIn('no business tests', report['scope'])
        self.assertEqual([c['name'] for c in report['checks']], ['template_integrity'])
        self.assertEqual(report['automatic_commands_executed'], 0)
        self.assertEqual(report['business_acceptance'], 'not_assessed')

    def test_template_current_honors_explicit_gates(self):
        self.configure(lambda c: c['lifecycle']['required_gates'].update(template=['unit']))
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 0)
        self.assertEqual(self.report()['automatic_commands_executed'], 1)
        self.configure(lambda c: (
            c['lifecycle']['required_gates'].update(template=['unit']),
            c['gates']['unit'].update(command=['{python}', '-c', 'raise SystemExit(8)'])))
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 1)
        self.assertEqual(self.report()['checks'][-1]['exit_code'], 8)

    def test_template_integrity_failure_is_not_green(self):
        with (self.root / 'README.md').open('a', encoding='utf-8') as stream:
            stream.write('\n[missing](missing-file.md)\n')
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 1)
        self.assertEqual(self.report()['result'], 'failed')
        self.assertEqual(self.report()['checks'][0]['status'], 'failed')

    def test_removed_profile_is_rejected(self):
        result = self.run_script('verify.py', '--profile', 'demo')
        self.assertEqual(result.returncode, 2)
        self.assertIn('invalid choice', result.stderr)

    def test_summary_links_task_without_copying_raw_details(self):
        task_id = 'CHORE-REPORT-001'
        self.assertEqual(self.run_script('new_task.py', task_id, '工具检查').returncode, 0)
        task = self.root / 'docs/tasks' / f'{task_id}.md'
        before = task.read_bytes()
        canary = 'private-test-fixture-marker'
        self.configure(lambda c: c['gates']['unit'].update(
            command=['{python}', '-c', f'print({canary!r}); raise SystemExit(7)']))
        result = self.run_script('verify.py', '--profile', 'quick', '--task', task_id)
        self.assertEqual(result.returncode, 1)
        report = self.report()
        self.assertEqual(report['task_id'], task_id)
        folder = max((self.root / 'artifacts').iterdir(), key=lambda p: p.stat().st_mtime_ns)
        summary = (folder / 'summary.md').read_text(encoding='utf-8')
        self.assertIn(task_id, summary)
        self.assertIn('| unit | failed | 7 |', summary)
        self.assertNotIn(canary, summary)
        self.assertIn(canary, (folder / 'unit.log').read_text(encoding='utf-8'))
        self.assertEqual(task.read_bytes(), before)
        self.assertEqual(report['business_acceptance'], 'not_assessed')

    def test_task_reference_rejects_missing_and_traversal(self):
        for task_id in ['FEAT-999999', '../escape', '']:
            self.assertEqual(self.run_script('verify.py', '--profile', 'current',
                                            '--task', task_id).returncode, 2)
            self.assertIsNone(self.report()['task_id'])

    def test_each_run_preserves_summary_even_on_config_failure(self):
        config_path = self.root / 'project.config.json'
        config = json.loads(config_path.read_text(encoding='utf-8'))
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 0)
        config_path.write_text('{broken', encoding='utf-8')
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 2)
        config.pop('lifecycle')
        config_path.write_text(json.dumps(config), encoding='utf-8')
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 2)
        summaries = list((self.root / 'artifacts').glob('*/summary.md'))
        self.assertEqual(len(summaries), 3)
        self.assertTrue(any('failed / 2' in p.read_text(encoding='utf-8') for p in summaries))
        self.assertTrue(any('passed / 0' in p.read_text(encoding='utf-8') for p in summaries))

    def test_unconfigured_quick_and_full_fail(self):
        for profile in ['quick', 'full']:
            self.assertEqual(self.run_script('verify.py', '--profile', profile).returncode, 1)
            self.assertEqual(self.report()['error'], 'No configured checks executed')

    def test_configured_gates_and_report(self):
        self.configure()
        self.assertEqual(self.run_script('verify.py', '--profile', 'full').returncode, 0)
        report = self.report()
        self.assertEqual(len(report['checks']), 6)
        self.assertEqual(report['config_snapshot']['project_name'], 'tooling-self-test')
        self.assertTrue(all(c['exit_code'] == 0 for c in report['checks'][1:]))

    def test_current_stage_requires_only_declared_gates(self):
        def discovery(config):
            config['lifecycle']['stage'] = 'discovery'
            config['gates']['integration'].update(status='unconfigured', command=[])
            config['gates']['build'].update(status='unconfigured', command=[])
            config['gates']['e2e'].update(status='unconfigured', command=[])

        self.configure(discovery)
        result = self.run_script('verify.py', '--profile', 'current')
        self.assertEqual(result.returncode, 0, result.stdout)
        report = self.report()
        self.assertEqual([item['name'] for item in report['checks'][1:]], ['quality', 'unit'])

    def test_current_stage_rejects_missing_required_gate(self):
        def discovery(config):
            config['lifecycle']['stage'] = 'discovery'
            config['gates']['unit'].update(status='unconfigured', command=[])

        self.configure(discovery)
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 1)

    def test_current_stage_rejects_required_not_applicable_gate(self):
        def discovery(config):
            config['lifecycle']['stage'] = 'discovery'
            config['gates']['unit'].update(
                status='not_applicable', command=[], reason='not used by this project')

        self.configure(discovery)
        self.assertEqual(self.run_script('verify.py', '--profile', 'current').returncode, 1)

    def test_failed_command_propagates(self):
        self.configure(lambda c: c['gates']['unit'].update(command=['{python}', '-c', 'raise SystemExit(7)']))
        self.assertEqual(self.run_script('verify.py', '--profile', 'quick').returncode, 1)
        self.assertEqual(self.report()['checks'][-1]['exit_code'], 7)

    def test_timeout_propagates(self):
        self.configure(lambda c: c['gates']['unit'].update(
            command=['{python}', '-c', 'import time; time.sleep(5)'], timeout_seconds=0.05))
        self.assertEqual(self.run_script('verify.py', '--profile', 'quick').returncode, 1)
        self.assertEqual(self.report()['checks'][-1]['status'], 'timeout')

    def test_missing_command_propagates(self):
        self.configure(lambda c: c['gates']['unit'].update(command=['not-an-installed-program-734923']))
        self.assertEqual(self.run_script('verify.py', '--profile', 'quick').returncode, 1)
        self.assertEqual(self.report()['checks'][-1]['status'], 'execution_error')

    def test_empty_configured_command_rejected(self):
        self.configure(lambda c: c['gates']['unit'].update(command=[]))
        self.assertEqual(self.run_script('verify.py', '--profile', 'quick').returncode, 2)

    def test_all_not_applicable_cannot_pass(self):
        def mutate(c):
            for gate in c['gates'].values():
                gate.update(status='not_applicable', command=[], reason='self-test fixture')
        self.configure(mutate)
        self.assertEqual(self.run_script('verify.py', '--profile', 'full').returncode, 1)

    def test_not_applicable_requires_reason(self):
        self.configure(lambda c: c['gates']['unit'].update(status='not_applicable', command=[], reason=''))
        self.assertEqual(self.run_script('verify.py', '--profile', 'quick').returncode, 2)

    def test_bad_json_rejected(self):
        (self.root / 'project.config.json').write_text('{broken', encoding='utf-8')
        self.assertEqual(self.run_script('verify.py', '--profile', 'full').returncode, 2)

    def test_broken_link_detected(self):
        with (self.root / 'docs/product.md').open('a', encoding='utf-8') as stream:
            stream.write('\n[missing](missing-file.md)\n')
        self.assertEqual(self.run_script('check_template.py').returncode, 1)

    def test_task_create_preserve_and_reject_traversal(self):
        result = self.run_script('new_task.py', 'FEAT-TOOLING-999999', '工具任务', '--status', '澄清中')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / 'docs/tasks/FEAT-TOOLING-999999.md'
        content = path.read_text(encoding='utf-8')
        self.assertIn('工具任务', content)
        self.assertIn('状态：澄清中', content)
        self.assertNotIn('{{TASK_ID}}', content)
        self.assertEqual(self.run_script('new_task.py', 'FEAT-TOOLING-999999', 'overwrite').returncode, 1)
        self.assertEqual(path.read_text(encoding='utf-8'), content)
        self.assertEqual(self.run_script('new_task.py', '../escape', 'invalid').returncode, 2)
        self.assertEqual(self.run_script('check_template.py').returncode, 0)

    def test_doctor_checks_tasks_and_current_gates(self):
        self.configure(lambda c: c['lifecycle'].update(stage='discovery'))
        self.assertEqual(self.run_script('new_task.py', 'FEAT-DOCTOR-999998', '风险实验').returncode, 0)
        result = self.run_script('doctor.py')
        self.assertEqual(result.returncode, 0, result.stdout)
        task = self.root / 'docs/tasks/FEAT-DOCTOR-999998.md'
        task.write_text(task.read_text(encoding='utf-8').replace('状态：待开始', '状态：未知'),
                        encoding='utf-8')
        self.assertEqual(self.run_script('doctor.py').returncode, 1)

    def test_promote_dry_run_and_forward_only(self):
        self.configure()
        result = self.run_script('promote_project.py', '--to', 'discovery', '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        config_path = self.root / 'project.config.json'
        self.assertEqual(json.loads(config_path.read_text(encoding='utf-8'))['lifecycle']['stage'], 'template')
        self.assertEqual(self.run_script('promote_project.py', '--to', 'discovery').returncode, 0)
        self.assertEqual(json.loads(config_path.read_text(encoding='utf-8'))['lifecycle']['stage'], 'discovery')
        self.assertEqual(self.run_script('promote_project.py', '--to', 'discovery').returncode, 1)

    def test_promote_rejects_missing_target_gate(self):
        self.configure(lambda c: c['gates']['build'].update(status='unconfigured', command=[]))
        self.assertEqual(self.run_script('promote_project.py', '--to', 'application').returncode, 1)

    def test_promote_upgrades_schema_version_one(self):
        self.configure()
        path = self.root / 'project.config.json'
        config = json.loads(path.read_text(encoding='utf-8'))
        config['schema_version'] = 1
        config.pop('lifecycle')
        config.pop('tasks')
        path.write_text(json.dumps(config), encoding='utf-8')
        self.assertEqual(self.run_script('promote_project.py', '--to', 'discovery').returncode, 0)
        upgraded = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(upgraded['schema_version'], 2)
        self.assertEqual(upgraded['lifecycle']['stage'], 'discovery')
        self.assertIn('id_pattern', upgraded['tasks'])


if __name__ == '__main__':
    if '--if-template' in sys.argv:
        sys.argv.remove('--if-template')
        config = json.loads((ROOT / 'project.config.json').read_text(encoding='utf-8'))
        if config.get('lifecycle', {}).get('stage', 'template') != 'template':
            print('Framework regression skipped outside template stage.')
            raise SystemExit(0)
    unittest.main(verbosity=2)
