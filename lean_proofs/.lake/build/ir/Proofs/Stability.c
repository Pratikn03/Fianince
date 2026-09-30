// Lean compiler output
// Module: Proofs.Stability
// Imports: public import Init public meta import Init public import Init.GrindInstances.Ring.Rat
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* l_Rat_mul(lean_object*, lean_object*);
lean_object* l_Nat_cast___at___00Dyadic_toRat_spec__0(lean_object*);
lean_object* l_Rat_add(lean_object*, lean_object*);
lean_object* l_Rat_sub(lean_object*, lean_object*);
static lean_once_cell_t lp_lean__proofs_MachineMarkets_charPoly___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_charPoly___closed__0;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_charPoly(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_charPoly___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_resolventDenom(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_resolventDenom___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_aggregateStability(lean_object*, lean_object*);
static lean_object* _init_lp_lean__proofs_MachineMarkets_charPoly___closed__0(void){
_start:
{
lean_object* v___x_1_; lean_object* v___x_2_; 
v___x_1_ = lean_unsigned_to_nat(1u);
v___x_2_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_1_);
return v___x_2_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_charPoly(lean_object* v_a_3_, lean_object* v_g_4_, lean_object* v_eta_5_, lean_object* v_kappa_6_, lean_object* v_lam_7_){
_start:
{
lean_object* v___x_8_; lean_object* v___x_9_; lean_object* v___x_10_; lean_object* v___x_11_; lean_object* v___x_12_; lean_object* v___x_13_; lean_object* v___x_14_; lean_object* v___x_15_; lean_object* v___x_16_; lean_object* v___x_17_; lean_object* v___x_18_; lean_object* v___x_19_; 
lean_inc_ref(v_lam_7_);
v___x_8_ = l_Rat_mul(v_lam_7_, v_lam_7_);
v___x_9_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_charPoly___closed__0, &lp_lean__proofs_MachineMarkets_charPoly___closed__0_once, _init_lp_lean__proofs_MachineMarkets_charPoly___closed__0);
lean_inc_ref(v_a_3_);
v___x_10_ = l_Rat_add(v_a_3_, v___x_9_);
lean_inc_ref_n(v_eta_5_, 2);
v___x_11_ = l_Rat_sub(v___x_10_, v_eta_5_);
v___x_12_ = l_Rat_mul(v___x_11_, v_lam_7_);
lean_dec_ref(v___x_11_);
v___x_13_ = l_Rat_sub(v___x_8_, v___x_12_);
v___x_14_ = l_Rat_sub(v___x_9_, v_eta_5_);
v___x_15_ = l_Rat_mul(v_a_3_, v___x_14_);
lean_dec_ref(v_a_3_);
v___x_16_ = l_Rat_add(v___x_13_, v___x_15_);
v___x_17_ = l_Rat_mul(v_g_4_, v_eta_5_);
v___x_18_ = l_Rat_mul(v___x_17_, v_kappa_6_);
lean_dec_ref(v___x_17_);
v___x_19_ = l_Rat_sub(v___x_16_, v___x_18_);
return v___x_19_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_charPoly___boxed(lean_object* v_a_20_, lean_object* v_g_21_, lean_object* v_eta_22_, lean_object* v_kappa_23_, lean_object* v_lam_24_){
_start:
{
lean_object* v_res_25_; 
v_res_25_ = lp_lean__proofs_MachineMarkets_charPoly(v_a_20_, v_g_21_, v_eta_22_, v_kappa_23_, v_lam_24_);
lean_dec_ref(v_g_21_);
return v_res_25_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_resolventDenom(lean_object* v_a_26_, lean_object* v_g_27_, lean_object* v_eta_28_, lean_object* v_kappa_29_, lean_object* v_lam_30_){
_start:
{
lean_object* v___x_31_; lean_object* v___x_32_; lean_object* v___x_33_; lean_object* v___x_34_; lean_object* v___x_35_; lean_object* v___x_36_; lean_object* v___x_37_; lean_object* v___x_38_; 
lean_inc_ref(v_lam_30_);
v___x_31_ = l_Rat_sub(v_lam_30_, v_a_26_);
v___x_32_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_charPoly___closed__0, &lp_lean__proofs_MachineMarkets_charPoly___closed__0_once, _init_lp_lean__proofs_MachineMarkets_charPoly___closed__0);
v___x_33_ = l_Rat_sub(v_lam_30_, v___x_32_);
lean_inc_ref(v_eta_28_);
v___x_34_ = l_Rat_add(v___x_33_, v_eta_28_);
v___x_35_ = l_Rat_mul(v___x_31_, v___x_34_);
lean_dec_ref(v___x_31_);
v___x_36_ = l_Rat_mul(v_g_27_, v_eta_28_);
v___x_37_ = l_Rat_mul(v___x_36_, v_kappa_29_);
lean_dec_ref(v___x_36_);
v___x_38_ = l_Rat_sub(v___x_35_, v___x_37_);
return v___x_38_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_resolventDenom___boxed(lean_object* v_a_39_, lean_object* v_g_40_, lean_object* v_eta_41_, lean_object* v_kappa_42_, lean_object* v_lam_43_){
_start:
{
lean_object* v_res_44_; 
v_res_44_ = lp_lean__proofs_MachineMarkets_resolventDenom(v_a_39_, v_g_40_, v_eta_41_, v_kappa_42_, v_lam_43_);
lean_dec_ref(v_g_40_);
return v_res_44_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_aggregateStability(lean_object* v_a_45_, lean_object* v_Q_46_){
_start:
{
lean_object* v___x_47_; 
v___x_47_ = l_Rat_add(v_a_45_, v_Q_46_);
return v___x_47_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init_GrindInstances_Ring_Rat(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_lean__proofs_Proofs_Stability(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
lean_initialize_runtime_module();
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init_GrindInstances_Ring_Rat(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
