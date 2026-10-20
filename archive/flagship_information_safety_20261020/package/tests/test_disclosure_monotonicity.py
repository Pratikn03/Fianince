"""Blueprint Section G test: test_disclosure_monotonicity.py (D9, E06)."""
from research_extension.information_safety.disclosure_experiment import evaluate_disclosure_tiers_T07


def test_disclosure_monotonicity():
    res = evaluate_disclosure_tiers_T07()
    tiers = res["tiers"]
    v_pub = tiers["public_aggregate"]["v_safe"]
    v_tag = tiers["class_tagged"]["v_safe"]
    v_aud = tiers["audited_channel"]["v_safe"]
    assert v_pub < v_tag < v_aud <= res["true_v_max"]
    assert tiers["class_tagged"]["net_disclosure_value_vs_public"] > 0.0
    assert res["negative_net_benefit_regime_example"]["net_value"] < 0.0


if __name__ == "__main__":
    test_disclosure_monotonicity()
    print("[PASS] test_disclosure_monotonicity.py")
