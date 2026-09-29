"""Hand-derived behavioral tests for the dossier's separate H1/H2 checker."""
import importlib.util
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import tempfile
import unittest

NAME = "research_extension.mechanism_dossier_20260926.exact_audit"
spec = importlib.util.find_spec(NAME)
audit = importlib.import_module(NAME) if spec else None
PAIRS = tuple(product((False, True), repeat=2))
LOW = (F(1), F(0), F(0))
MID = (F(0), F(1), F(0))
HIGH = (F(0), F(0), F(1))


class ExactAuditTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(audit, "The independent exact checker is not implemented")

    def test_stage_accounting_and_participation_have_hand_values(self):
        # Catches counting each dealer's tied half-fill as a full trade.
        expected = {
            2: (F(-1, 8), F(-1, 8), F(5, 2), F(9, 4), F(7, 8)),
            4: (F(1, 4), F(1, 4), F(3, 2), F(2), F(1, 2)),
            6: (F(3, 4), F(3, 4), F(1, 2), F(2), F(1, 2)),
        }
        for ask, want in expected.items():
            self.assertEqual(audit.stage((F(ask), F(ask))), want)

    def test_realized_no_trade_and_negative_dealer_reward(self):
        self.assertEqual(audit.settlement((F(2), F(4)), F(4), F(2)),
                         (F(-2), F(0), F(0), F(-2), F(1)))
        self.assertEqual(audit.settlement((F(2), F(4)), F(0), F(-2)), (F(0),)*5)

    def test_tied_policy_uses_every_maximizer(self):
        self.assertEqual(audit.policy((F(1), F(1), F(0)), F(1, 10)),
                         (F(29, 60), F(29, 60), F(1, 30)))
        self.assertEqual(audit.policy(LOW, F(1)), (F(1, 3),)*3)

    def test_warm_cache_cannot_bypass_rational_input_validation(self):
        audit.policy((F(9), F(2), F(3)), F(1, 10))
        with self.assertRaises(TypeError):
            audit.policy((9, 2, 3), F(1, 10))

    def test_frozen_scheduled_refresh_has_hand_payoffs(self):
        # Frozen learning still refreshes HIGH at t=1; it is not no deployment.
        r = audit.evaluate((MID, MID), (HIGH, HIGH), (False, False),
                           (False, False), epsilon=F(0))
        self.assertEqual(r["total"], (F(1), F(1), F(2), F(4), F(1)))
        self.assertEqual(r["periods"][1],
                         (F(3, 4), F(3, 4), F(1, 2), F(2), F(1, 2)))

    def test_cost_once_and_not_in_shadow_reward(self):
        args = ((LOW, MID), (HIGH, LOW), (True, False), (True, True))
        zero = audit.evaluate(*args)
        paid = audit.evaluate(*args, costs=(F(1, 5), F(9)))
        self.assertEqual(paid["periods"], zero["periods"])
        want = list(zero["total"])
        want[0] -= F(1, 5)
        want[3] -= F(1, 5)
        self.assertEqual(paid["total"], tuple(want))

    def test_h1_payoffs_cannot_depend_on_learning_mask(self):
        for profile in PAIRS:
            results = [audit.evaluate((LOW, MID), (HIGH, LOW), profile, mask,
                                      horizon=1)["total"] for mask in PAIRS]
            self.assertTrue(all(x == results[0] for x in results))

    def test_alpha_zero_and_frozen_have_same_total(self):
        for profile in PAIRS:
            args = ((LOW, MID), (HIGH, LOW), profile)
            self.assertEqual(audit.evaluate(*args, (True, True), alpha=F(0))["total"],
                             audit.evaluate(*args, (False, False))["total"])

    def test_identical_candidate_is_behavioral_placebo(self):
        for mask in PAIRS:
            outputs = [audit.evaluate((LOW, MID), (LOW, MID), p, mask)["total"]
                       for p in PAIRS]
            self.assertTrue(all(x == outputs[0] for x in outputs))

    def test_uniform_exploration_removes_deployment_effect(self):
        for mask in PAIRS:
            outputs = [audit.evaluate((LOW, MID), (HIGH, LOW), p, mask,
                                      epsilon=F(1))["total"] for p in PAIRS]
            self.assertTrue(all(x == outputs[0] for x in outputs))

    def test_independent_value_customer_welfare_null(self):
        for profile, mask in product(PAIRS, repeat=2):
            r = audit.evaluate((LOW, MID), (HIGH, LOW), profile, mask,
                               costs=(F(1, 5), F(1, 20)), law="independent")
            self.assertEqual(r["total"][3],
                             F(5)-F(1, 5)*profile[0]-F(1, 20)*profile[1])

    def test_period_welfare_reconstructed_from_quote_exposure(self):
        for profile, mask in product(PAIRS, repeat=2):
            r = audit.evaluate((LOW, MID), (HIGH, LOW), profile, mask)
            for pay, probability in zip(r["periods"], r["minimum_ask2"]):
                self.assertEqual(pay[3], F(2)+probability/4)
            self.assertEqual(sum(r["total"][:3]), r["total"][3])

    def test_validation_rejects_out_of_scope_horizon_and_float(self):
        args = ((LOW, MID), (HIGH, LOW), (False, False), (True, True))
        for kwargs in ({"horizon": 3}, {"horizon": True}, {"epsilon": 0.1},
                       {"alpha": F(-1)}, {"costs": (F(-1), F(0))}):
            with self.assertRaises((TypeError, ValueError)):
                audit.evaluate(*args, **kwargs)

    def test_locked_output_is_create_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"result.json"
            audit.write_new_json(path, {"exact": F(1, 3)})
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                audit.write_new_json(path, {"changed": True})
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
