// Lean compiler output
// Module: Proofs.Bounds
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
lean_object* l_Nat_cast___at___00Dyadic_toRat_spec__0(lean_object*);
lean_object* l_Rat_sub(lean_object*, lean_object*);
lean_object* l_Rat_pow(lean_object*, lean_object*);
lean_object* l_Rat_mul(lean_object*, lean_object*);
lean_object* lean_nat_to_int(lean_object*);
uint8_t l_instDecidableEqRat_decEq(lean_object*, lean_object*);
lean_object* lean_string_length(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* l_Int_repr(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
uint8_t lean_int_dec_lt(lean_object*, lean_object*);
lean_object* l_Repr_addAppParen(lean_object*, lean_object*);
static lean_once_cell_t lp_lean__proofs_MachineMarkets_tailBound___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_tailBound___closed__0;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_tailBound(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_tailBound___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqInterval_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqInterval_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqInterval(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqInterval___boxed(lean_object*, lean_object*);
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__0 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__0_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "lower"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__1 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__1_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__1_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__2 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__2_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__2_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__3 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__3_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__4 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__4_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__4_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__5 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__5_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__3_value),((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__5_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__6 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__6_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__7;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__8 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__8_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__9;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__10;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__0_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__11 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__11_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__8_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__12 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__12_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__13 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__13_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__13_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__14 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__14_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "upper"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__15 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__15_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__15_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__16 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__16_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "("};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__17 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__17_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " : Rat)/"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__18 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__18_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_lean__proofs_MachineMarkets_instReprInterval___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_lean__proofs_MachineMarkets_instReprInterval_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval___closed__0 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval___closed__0_value;
LEAN_EXPORT const lean_object* lp_lean__proofs_MachineMarkets_instReprInterval = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprInterval___closed__0_value;
static lean_object* _init_lp_lean__proofs_MachineMarkets_tailBound___closed__0(void){
_start:
{
lean_object* v___x_1_; lean_object* v___x_2_; 
v___x_1_ = lean_unsigned_to_nat(1u);
v___x_2_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_1_);
return v___x_2_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_tailBound(lean_object* v_Qmax_3_, lean_object* v_eta_4_, lean_object* v_H_5_){
_start:
{
lean_object* v___x_6_; lean_object* v___x_7_; lean_object* v___x_8_; lean_object* v___x_9_; 
v___x_6_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_tailBound___closed__0, &lp_lean__proofs_MachineMarkets_tailBound___closed__0_once, _init_lp_lean__proofs_MachineMarkets_tailBound___closed__0);
v___x_7_ = l_Rat_sub(v___x_6_, v_eta_4_);
v___x_8_ = l_Rat_pow(v___x_7_, v_H_5_);
v___x_9_ = l_Rat_mul(v_Qmax_3_, v___x_8_);
return v___x_9_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_tailBound___boxed(lean_object* v_Qmax_10_, lean_object* v_eta_11_, lean_object* v_H_12_){
_start:
{
lean_object* v_res_13_; 
v_res_13_ = lp_lean__proofs_MachineMarkets_tailBound(v_Qmax_10_, v_eta_11_, v_H_12_);
lean_dec(v_H_12_);
lean_dec_ref(v_Qmax_10_);
return v_res_13_;
}
}
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqInterval_decEq(lean_object* v_x_14_, lean_object* v_x_15_){
_start:
{
lean_object* v_lower_16_; lean_object* v_upper_17_; lean_object* v_lower_18_; lean_object* v_upper_19_; uint8_t v___x_20_; 
v_lower_16_ = lean_ctor_get(v_x_14_, 0);
v_upper_17_ = lean_ctor_get(v_x_14_, 1);
v_lower_18_ = lean_ctor_get(v_x_15_, 0);
v_upper_19_ = lean_ctor_get(v_x_15_, 1);
v___x_20_ = l_instDecidableEqRat_decEq(v_lower_16_, v_lower_18_);
if (v___x_20_ == 0)
{
return v___x_20_;
}
else
{
uint8_t v___x_21_; 
v___x_21_ = l_instDecidableEqRat_decEq(v_upper_17_, v_upper_19_);
return v___x_21_;
}
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqInterval_decEq___boxed(lean_object* v_x_22_, lean_object* v_x_23_){
_start:
{
uint8_t v_res_24_; lean_object* v_r_25_; 
v_res_24_ = lp_lean__proofs_MachineMarkets_instDecidableEqInterval_decEq(v_x_22_, v_x_23_);
lean_dec_ref(v_x_23_);
lean_dec_ref(v_x_22_);
v_r_25_ = lean_box(v_res_24_);
return v_r_25_;
}
}
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqInterval(lean_object* v_x_26_, lean_object* v_x_27_){
_start:
{
uint8_t v___x_28_; 
v___x_28_ = lp_lean__proofs_MachineMarkets_instDecidableEqInterval_decEq(v_x_26_, v_x_27_);
return v___x_28_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqInterval___boxed(lean_object* v_x_29_, lean_object* v_x_30_){
_start:
{
uint8_t v_res_31_; lean_object* v_r_32_; 
v_res_31_ = lp_lean__proofs_MachineMarkets_instDecidableEqInterval(v_x_29_, v_x_30_);
lean_dec_ref(v_x_30_);
lean_dec_ref(v_x_29_);
v_r_32_ = lean_box(v_res_31_);
return v_r_32_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_46_; lean_object* v___x_47_; 
v___x_46_ = lean_unsigned_to_nat(9u);
v___x_47_ = lean_nat_to_int(v___x_46_);
return v___x_47_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__9(void){
_start:
{
lean_object* v___x_49_; lean_object* v___x_50_; 
v___x_49_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__0));
v___x_50_ = lean_string_length(v___x_49_);
return v___x_50_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__10(void){
_start:
{
lean_object* v___x_51_; lean_object* v___x_52_; 
v___x_51_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__9, &lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__9_once, _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__9);
v___x_52_ = lean_nat_to_int(v___x_51_);
return v___x_52_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19(void){
_start:
{
lean_object* v___x_65_; lean_object* v___x_66_; 
v___x_65_ = lean_unsigned_to_nat(0u);
v___x_66_ = lean_nat_to_int(v___x_65_);
return v___x_66_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg(lean_object* v_x_67_){
_start:
{
lean_object* v_lower_68_; lean_object* v_upper_69_; lean_object* v___x_71_; uint8_t v_isShared_72_; uint8_t v_isSharedCheck_157_; 
v_lower_68_ = lean_ctor_get(v_x_67_, 0);
v_upper_69_ = lean_ctor_get(v_x_67_, 1);
v_isSharedCheck_157_ = !lean_is_exclusive(v_x_67_);
if (v_isSharedCheck_157_ == 0)
{
v___x_71_ = v_x_67_;
v_isShared_72_ = v_isSharedCheck_157_;
goto v_resetjp_70_;
}
else
{
lean_inc(v_upper_69_);
lean_inc(v_lower_68_);
lean_dec(v_x_67_);
v___x_71_ = lean_box(0);
v_isShared_72_ = v_isSharedCheck_157_;
goto v_resetjp_70_;
}
v_resetjp_70_:
{
lean_object* v_num_73_; lean_object* v_den_74_; lean_object* v___x_76_; uint8_t v_isShared_77_; uint8_t v_isSharedCheck_156_; 
v_num_73_ = lean_ctor_get(v_lower_68_, 0);
v_den_74_ = lean_ctor_get(v_lower_68_, 1);
v_isSharedCheck_156_ = !lean_is_exclusive(v_lower_68_);
if (v_isSharedCheck_156_ == 0)
{
v___x_76_ = v_lower_68_;
v_isShared_77_ = v_isSharedCheck_156_;
goto v_resetjp_75_;
}
else
{
lean_inc(v_den_74_);
lean_inc(v_num_73_);
lean_dec(v_lower_68_);
v___x_76_ = lean_box(0);
v_isShared_77_ = v_isSharedCheck_156_;
goto v_resetjp_75_;
}
v_resetjp_75_:
{
lean_object* v___x_78_; lean_object* v___x_79_; lean_object* v___x_80_; lean_object* v___y_82_; uint8_t v___y_83_; lean_object* v___y_84_; lean_object* v___y_100_; lean_object* v___x_138_; uint8_t v___x_139_; 
v___x_78_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__5));
v___x_79_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__6));
v___x_80_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__7, &lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__7_once, _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__7);
v___x_138_ = lean_unsigned_to_nat(1u);
v___x_139_ = lean_nat_dec_eq(v_den_74_, v___x_138_);
if (v___x_139_ == 0)
{
lean_object* v___x_140_; lean_object* v___x_141_; lean_object* v___x_142_; lean_object* v___x_143_; lean_object* v___x_144_; lean_object* v___x_145_; lean_object* v___x_146_; lean_object* v___x_147_; 
v___x_140_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__17));
v___x_141_ = l_Int_repr(v_num_73_);
lean_dec(v_num_73_);
v___x_142_ = lean_string_append(v___x_140_, v___x_141_);
lean_dec_ref(v___x_141_);
v___x_143_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__18));
v___x_144_ = lean_string_append(v___x_142_, v___x_143_);
v___x_145_ = l_Nat_reprFast(v_den_74_);
v___x_146_ = lean_string_append(v___x_144_, v___x_145_);
lean_dec_ref(v___x_145_);
v___x_147_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_147_, 0, v___x_146_);
v___y_100_ = v___x_147_;
goto v___jp_99_;
}
else
{
lean_object* v___x_148_; lean_object* v___x_149_; uint8_t v___x_150_; 
lean_dec(v_den_74_);
v___x_148_ = lean_unsigned_to_nat(0u);
v___x_149_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19, &lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19_once, _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19);
v___x_150_ = lean_int_dec_lt(v_num_73_, v___x_149_);
if (v___x_150_ == 0)
{
lean_object* v___x_151_; lean_object* v___x_152_; 
v___x_151_ = l_Int_repr(v_num_73_);
lean_dec(v_num_73_);
v___x_152_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_152_, 0, v___x_151_);
v___y_100_ = v___x_152_;
goto v___jp_99_;
}
else
{
lean_object* v___x_153_; lean_object* v___x_154_; lean_object* v___x_155_; 
v___x_153_ = l_Int_repr(v_num_73_);
lean_dec(v_num_73_);
v___x_154_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_154_, 0, v___x_153_);
v___x_155_ = l_Repr_addAppParen(v___x_154_, v___x_148_);
v___y_100_ = v___x_155_;
goto v___jp_99_;
}
}
v___jp_81_:
{
lean_object* v___x_86_; 
if (v_isShared_77_ == 0)
{
lean_ctor_set_tag(v___x_76_, 4);
lean_ctor_set(v___x_76_, 1, v___y_84_);
lean_ctor_set(v___x_76_, 0, v___x_80_);
v___x_86_ = v___x_76_;
goto v_reusejp_85_;
}
else
{
lean_object* v_reuseFailAlloc_98_; 
v_reuseFailAlloc_98_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_98_, 0, v___x_80_);
lean_ctor_set(v_reuseFailAlloc_98_, 1, v___y_84_);
v___x_86_ = v_reuseFailAlloc_98_;
goto v_reusejp_85_;
}
v_reusejp_85_:
{
lean_object* v___x_87_; lean_object* v___x_89_; 
v___x_87_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_87_, 0, v___x_86_);
lean_ctor_set_uint8(v___x_87_, sizeof(void*)*1, v___y_83_);
if (v_isShared_72_ == 0)
{
lean_ctor_set_tag(v___x_71_, 5);
lean_ctor_set(v___x_71_, 1, v___x_87_);
lean_ctor_set(v___x_71_, 0, v___y_82_);
v___x_89_ = v___x_71_;
goto v_reusejp_88_;
}
else
{
lean_object* v_reuseFailAlloc_97_; 
v_reuseFailAlloc_97_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v_reuseFailAlloc_97_, 0, v___y_82_);
lean_ctor_set(v_reuseFailAlloc_97_, 1, v___x_87_);
v___x_89_ = v_reuseFailAlloc_97_;
goto v_reusejp_88_;
}
v_reusejp_88_:
{
lean_object* v___x_90_; lean_object* v___x_91_; lean_object* v___x_92_; lean_object* v___x_93_; lean_object* v___x_94_; lean_object* v___x_95_; lean_object* v___x_96_; 
v___x_90_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__10, &lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__10_once, _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__10);
v___x_91_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__11));
v___x_92_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_92_, 0, v___x_91_);
lean_ctor_set(v___x_92_, 1, v___x_89_);
v___x_93_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__12));
v___x_94_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_94_, 0, v___x_92_);
lean_ctor_set(v___x_94_, 1, v___x_93_);
v___x_95_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_95_, 0, v___x_90_);
lean_ctor_set(v___x_95_, 1, v___x_94_);
v___x_96_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_96_, 0, v___x_95_);
lean_ctor_set_uint8(v___x_96_, sizeof(void*)*1, v___y_83_);
return v___x_96_;
}
}
}
v___jp_99_:
{
lean_object* v_num_101_; lean_object* v_den_102_; lean_object* v___x_104_; uint8_t v_isShared_105_; uint8_t v_isSharedCheck_137_; 
v_num_101_ = lean_ctor_get(v_upper_69_, 0);
v_den_102_ = lean_ctor_get(v_upper_69_, 1);
v_isSharedCheck_137_ = !lean_is_exclusive(v_upper_69_);
if (v_isSharedCheck_137_ == 0)
{
v___x_104_ = v_upper_69_;
v_isShared_105_ = v_isSharedCheck_137_;
goto v_resetjp_103_;
}
else
{
lean_inc(v_den_102_);
lean_inc(v_num_101_);
lean_dec(v_upper_69_);
v___x_104_ = lean_box(0);
v_isShared_105_ = v_isSharedCheck_137_;
goto v_resetjp_103_;
}
v_resetjp_103_:
{
lean_object* v___x_107_; 
if (v_isShared_105_ == 0)
{
lean_ctor_set_tag(v___x_104_, 4);
lean_ctor_set(v___x_104_, 1, v___y_100_);
lean_ctor_set(v___x_104_, 0, v___x_80_);
v___x_107_ = v___x_104_;
goto v_reusejp_106_;
}
else
{
lean_object* v_reuseFailAlloc_136_; 
v_reuseFailAlloc_136_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_136_, 0, v___x_80_);
lean_ctor_set(v_reuseFailAlloc_136_, 1, v___y_100_);
v___x_107_ = v_reuseFailAlloc_136_;
goto v_reusejp_106_;
}
v_reusejp_106_:
{
uint8_t v___x_108_; lean_object* v___x_109_; lean_object* v___x_110_; lean_object* v___x_111_; lean_object* v___x_112_; lean_object* v___x_113_; lean_object* v___x_114_; lean_object* v___x_115_; lean_object* v___x_116_; lean_object* v___x_117_; lean_object* v___x_118_; uint8_t v___x_119_; 
v___x_108_ = 0;
v___x_109_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_109_, 0, v___x_107_);
lean_ctor_set_uint8(v___x_109_, sizeof(void*)*1, v___x_108_);
v___x_110_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_110_, 0, v___x_79_);
lean_ctor_set(v___x_110_, 1, v___x_109_);
v___x_111_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__14));
v___x_112_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_112_, 0, v___x_110_);
lean_ctor_set(v___x_112_, 1, v___x_111_);
v___x_113_ = lean_box(1);
v___x_114_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_114_, 0, v___x_112_);
lean_ctor_set(v___x_114_, 1, v___x_113_);
v___x_115_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__16));
v___x_116_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_116_, 0, v___x_114_);
lean_ctor_set(v___x_116_, 1, v___x_115_);
v___x_117_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_117_, 0, v___x_116_);
lean_ctor_set(v___x_117_, 1, v___x_78_);
v___x_118_ = lean_unsigned_to_nat(1u);
v___x_119_ = lean_nat_dec_eq(v_den_102_, v___x_118_);
if (v___x_119_ == 0)
{
lean_object* v___x_120_; lean_object* v___x_121_; lean_object* v___x_122_; lean_object* v___x_123_; lean_object* v___x_124_; lean_object* v___x_125_; lean_object* v___x_126_; lean_object* v___x_127_; 
v___x_120_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__17));
v___x_121_ = l_Int_repr(v_num_101_);
lean_dec(v_num_101_);
v___x_122_ = lean_string_append(v___x_120_, v___x_121_);
lean_dec_ref(v___x_121_);
v___x_123_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__18));
v___x_124_ = lean_string_append(v___x_122_, v___x_123_);
v___x_125_ = l_Nat_reprFast(v_den_102_);
v___x_126_ = lean_string_append(v___x_124_, v___x_125_);
lean_dec_ref(v___x_125_);
v___x_127_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_127_, 0, v___x_126_);
v___y_82_ = v___x_117_;
v___y_83_ = v___x_108_;
v___y_84_ = v___x_127_;
goto v___jp_81_;
}
else
{
lean_object* v___x_128_; lean_object* v___x_129_; uint8_t v___x_130_; 
lean_dec(v_den_102_);
v___x_128_ = lean_unsigned_to_nat(0u);
v___x_129_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19, &lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19_once, _init_lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg___closed__19);
v___x_130_ = lean_int_dec_lt(v_num_101_, v___x_129_);
if (v___x_130_ == 0)
{
lean_object* v___x_131_; lean_object* v___x_132_; 
v___x_131_ = l_Int_repr(v_num_101_);
lean_dec(v_num_101_);
v___x_132_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_132_, 0, v___x_131_);
v___y_82_ = v___x_117_;
v___y_83_ = v___x_108_;
v___y_84_ = v___x_132_;
goto v___jp_81_;
}
else
{
lean_object* v___x_133_; lean_object* v___x_134_; lean_object* v___x_135_; 
v___x_133_ = l_Int_repr(v_num_101_);
lean_dec(v_num_101_);
v___x_134_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_134_, 0, v___x_133_);
v___x_135_ = l_Repr_addAppParen(v___x_134_, v___x_128_);
v___y_82_ = v___x_117_;
v___y_83_ = v___x_108_;
v___y_84_ = v___x_135_;
goto v___jp_81_;
}
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr(lean_object* v_x_158_, lean_object* v_prec_159_){
_start:
{
lean_object* v___x_160_; 
v___x_160_ = lp_lean__proofs_MachineMarkets_instReprInterval_repr___redArg(v_x_158_);
return v___x_160_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprInterval_repr___boxed(lean_object* v_x_161_, lean_object* v_prec_162_){
_start:
{
lean_object* v_res_163_; 
v_res_163_ = lp_lean__proofs_MachineMarkets_instReprInterval_repr(v_x_161_, v_prec_162_);
lean_dec(v_prec_162_);
return v_res_163_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init_GrindInstances_Ring_Rat(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_lean__proofs_Proofs_Bounds(uint8_t builtin) {
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
