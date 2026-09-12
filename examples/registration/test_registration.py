"""Acceptance examples mapped to pure-rule tests; no infrastructure claims."""
import os
import unittest
from registration import registration_decision as correct_decision

# Controlled fault demonstration; enabled only for this isolated example.
if os.environ.get('DEMO_MUTATION') == 'allow_full':
    def registration_decision(**kwargs):
        result = correct_decision(**kwargs)
        return 'ACCEPT' if result == 'FULL' else result
else:
    registration_decision = correct_decision


class RegistrationTests(unittest.TestCase):
    def decide(self, **changes):
        values = dict(capacity=10, registered=5, already_registered=False, authenticated=True)
        values.update(changes)
        return registration_decision(**values)

    def test_AC001_available_seat(self):
        self.assertEqual(self.decide(), 'ACCEPT')

    def test_AC002_last_seat(self):
        self.assertEqual(self.decide(registered=9), 'ACCEPT')

    def test_AC003_full(self):
        self.assertEqual(self.decide(registered=10), 'FULL')

    def test_AC004_duplicate_takes_precedence_over_full(self):
        self.assertEqual(self.decide(registered=10, already_registered=True), 'ALREADY_REGISTERED')

    def test_AC005_unauthenticated(self):
        self.assertEqual(self.decide(authenticated=False, already_registered=True), 'UNAUTHENTICATED')

    def test_AC006_zero_capacity(self):
        self.assertEqual(self.decide(capacity=0, registered=0), 'FULL')

    def test_AC007_invalid_counts(self):
        for values in ({'registered': -1}, {'capacity': -1}, {'registered': 11},
                       {'capacity': True}, {'registered': 1.5}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.decide(**values)

    def test_AC008_invalid_flags(self):
        with self.assertRaises(ValueError):
            self.decide(authenticated='yes')


if __name__ == '__main__':
    unittest.main()
