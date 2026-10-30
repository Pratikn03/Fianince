import Init
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000
-- Seven concrete rational inequality certificates, not a formal market theorem.
namespace CostWitness
theorem se_upper : (3 : Nat) * 160000 < 121 * 4000 := by decide
#print axioms se_upper
theorem normal_tail_budget : (20480000000000000000000 : Nat) * 40 < 1 * 935777428277954763057921 := by decide
#print axioms normal_tail_budget
theorem stress_reserve_safe : (10931588729 : Nat) * 1 < 1 * 10950000000 := by decide
#print axioms stress_reserve_safe
theorem prefunding_safe : (4917421344119 : Nat) * 1 < 1000 * 10950000000 := by decide
#print axioms prefunding_safe
theorem no_data_cap_upper : (1 : Nat) * 31561226188612435968000000000000000000000000000000000000000000000000000000000000000 < 31669474489466798987803386707824376304541464676896101750604603619802949756638426111 * 1 := by decide
#print axioms no_data_cap_upper
theorem positive_net_value : (7 : Nat) * 73000000000 < 10525881163 * 50 := by decide
#print axioms positive_net_value
theorem positive_asset_price : (1099806642641875194194788586141879337186429107912304428547687393070617649853199 : Nat) * 1 < 100 * 1441151880758558720000000000000000000000000000000000000000000000000000000000000 := by decide
#print axioms positive_asset_price
end CostWitness
