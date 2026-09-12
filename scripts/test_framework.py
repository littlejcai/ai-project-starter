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

    def run_script(self, name, *args, env=None):
        variables = os.environ.copy()
        variables.pop('DEMO_MUTATION', None)
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

    def test_template_and_demo(self):
        self.assertEqual(self.run_script('check_template.py').returncode, 0)
        result = self.run_script('verify.py', '--profile', 'demo')
        self.assertEqual(result.returncode, 0, result.stdout)
        report = self.report()
        log = self.root / report['checks'][-1]['log']
        self.assertIn('Ran 8 tests', log.read_text(encoding='utf-8'))
        self.assertEqual(report['scope'], 'isolated example only')

    def test_demo_fault_is_caught(self):
        result = self.run_script('verify.py', '--profile', 'demo', env={'DEMO_MUTATION': 'allow_full'})
        self.assertEqual(result.returncode, 1)
        log = self.root / self.report()['checks'][-1]['log']
        self.assertIn('FAILED (failures=2)', log.read_text(encoding='utf-8'))

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
        result = self.run_script('new_task.py', 'FEAT-001', '报名功能')
        self.assertEqual(result.returncode, 0, result.stderr)
        path = self.root / 'docs/tasks/FEAT-001.md'
        content = path.read_text(encoding='utf-8')
        self.assertIn('报名功能', content)
        self.assertNotIn('{{TASK_ID}}', content)
        self.assertEqual(self.run_script('new_task.py', 'FEAT-001', 'overwrite').returncode, 1)
        self.assertEqual(path.read_text(encoding='utf-8'), content)
        self.assertEqual(self.run_script('new_task.py', '../escape', 'invalid').returncode, 2)
        self.assertEqual(self.run_script('check_template.py').returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
