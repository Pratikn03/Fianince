"""Economic hand fixtures for the selected post-hoc witness, not training tests."""
import importlib
import importlib.util
from fractions import Fraction as F
import unittest

NAME = "research_extension.mechanism_dossier_20260926.witness_audit"
module = importlib.import_module(NAME) if importlib.util.find_spec(NAME) else None


class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(module, "Witness calculation is not implemented")

    def test_closed_form_has_hand_checked_default_and_null_values(self):
        self.assertEqual(module.prediction(F(1, 10), F(1, 2)),
                         (F(1023, 16000), -F(87, 8000)))
        self.assertEqual(module.prediction(F(0), F(1)), (F(1, 12), -F(1, 72)))
        self.assertEqual(module.prediction(F(1), F(1, 2)), (F(0), F(0)))
        self.assertEqual(module.prediction(F(1, 10), F(0)), (F(0), F(0)))

    def test_costly_game_has_unique_pure_equilibrium_and_different_planner(self):
        r = module.witness_report()
        self.assertEqual(r["costly_game"]["pure_equilibria"], [(True, False)])
        self.assertEqual(r["costly_game"]["planner_profiles"], [(False, False)])
        self.assertEqual(r["costly_game"]["welfare_gap"], F(487, 8000))
        self.assertEqual(r["costly_game"]["focal_net_gain"], F(223, 16000))

    def test_formulas_agree_and_sensitivity_retains_vanishing_case(self):
        r = module.witness_report()
        self.assertEqual(r["formula_checks"], 16)
        self.assertEqual(r["formula_failures"], [])
        negative = next(x for x in r["initial_shadow_sensitivity"]
                        if x["rival_shadow"] == (F(-1, 100),)*3)
        self.assertEqual(negative["gross_delta_own_welfare"], (F(0), F(0)))


if __name__ == "__main__":
    unittest.main()
