// Lean compiler output
// Module: Proofs.PBHDefect
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
lean_object* lean_string_length(lean_object*);
lean_object* lean_nat_to_int(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* l_Int_repr(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
uint8_t lean_int_dec_lt(lean_object*, lean_object*);
lean_object* l_Repr_addAppParen(lean_object*, lean_object*);
uint8_t l_instDecidableEqRat_decEq(lean_object*, lean_object*);
lean_object* l_Nat_cast___at___00Dyadic_toRat_spec__0(lean_object*);
lean_object* l_Rat_neg(lean_object*);
lean_object* l_Rat_mul(lean_object*, lean_object*);
lean_object* l_Rat_add(lean_object*, lean_object*);
lean_object* l_Rat_sub(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqVec3_decEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqVec3_decEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqVec3(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqVec3___boxed(lean_object*, lean_object*);
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__0 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__0_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__1 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__1_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__3;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__0_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__4 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__4_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__1_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__5 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__5_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "x"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__6 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__6_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__6_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__7 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__7_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__7_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__8 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__8_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__9 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__9_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__9_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__10 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__10_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "y2"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__11 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__11_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__11_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__12 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__12_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "("};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__13 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__13_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " : Rat)/"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__14 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__14_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__8_value),((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__10_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__16 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__16_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__17;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__18 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__18_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__18_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__19 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__19_value;
static const lean_string_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "y1"};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__20 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__20_value;
static const lean_ctor_object lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__20_value)}};
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__21 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__21_value;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__22_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__22;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_lean__proofs_MachineMarkets_instReprVec3___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_lean__proofs_MachineMarkets_instReprVec3_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3___closed__0 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3___closed__0_value;
LEAN_EXPORT const lean_object* lp_lean__proofs_MachineMarkets_instReprVec3 = (const lean_object*)&lp_lean__proofs_MachineMarkets_instReprVec3___closed__0_value;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_C__dot(lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_C__dot___boxed(lean_object*);
static lean_once_cell_t lp_lean__proofs_MachineMarkets_J__mul___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_J__mul___closed__0;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_J__mul(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_J__mul___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__2;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_pbh__null__vec;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_transferDenom(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_channelResponse(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_channelResponse___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqVec3_decEq(lean_object* v_x_1_, lean_object* v_x_2_){
_start:
{
lean_object* v_x_3_; lean_object* v_y1_4_; lean_object* v_y2_5_; lean_object* v_x_6_; lean_object* v_y1_7_; lean_object* v_y2_8_; uint8_t v___x_9_; 
v_x_3_ = lean_ctor_get(v_x_1_, 0);
v_y1_4_ = lean_ctor_get(v_x_1_, 1);
v_y2_5_ = lean_ctor_get(v_x_1_, 2);
v_x_6_ = lean_ctor_get(v_x_2_, 0);
v_y1_7_ = lean_ctor_get(v_x_2_, 1);
v_y2_8_ = lean_ctor_get(v_x_2_, 2);
v___x_9_ = l_instDecidableEqRat_decEq(v_x_3_, v_x_6_);
if (v___x_9_ == 0)
{
return v___x_9_;
}
else
{
uint8_t v___x_10_; 
v___x_10_ = l_instDecidableEqRat_decEq(v_y1_4_, v_y1_7_);
if (v___x_10_ == 0)
{
return v___x_10_;
}
else
{
uint8_t v___x_11_; 
v___x_11_ = l_instDecidableEqRat_decEq(v_y2_5_, v_y2_8_);
return v___x_11_;
}
}
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqVec3_decEq___boxed(lean_object* v_x_12_, lean_object* v_x_13_){
_start:
{
uint8_t v_res_14_; lean_object* v_r_15_; 
v_res_14_ = lp_lean__proofs_MachineMarkets_instDecidableEqVec3_decEq(v_x_12_, v_x_13_);
lean_dec_ref(v_x_13_);
lean_dec_ref(v_x_12_);
v_r_15_ = lean_box(v_res_14_);
return v_r_15_;
}
}
LEAN_EXPORT uint8_t lp_lean__proofs_MachineMarkets_instDecidableEqVec3(lean_object* v_x_16_, lean_object* v_x_17_){
_start:
{
uint8_t v___x_18_; 
v___x_18_ = lp_lean__proofs_MachineMarkets_instDecidableEqVec3_decEq(v_x_16_, v_x_17_);
return v___x_18_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instDecidableEqVec3___boxed(lean_object* v_x_19_, lean_object* v_x_20_){
_start:
{
uint8_t v_res_21_; lean_object* v_r_22_; 
v_res_21_ = lp_lean__proofs_MachineMarkets_instDecidableEqVec3(v_x_19_, v_x_20_);
lean_dec_ref(v_x_20_);
lean_dec_ref(v_x_19_);
v_r_22_ = lean_box(v_res_21_);
return v_r_22_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__2(void){
_start:
{
lean_object* v___x_25_; lean_object* v___x_26_; 
v___x_25_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__0));
v___x_26_ = lean_string_length(v___x_25_);
return v___x_26_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__3(void){
_start:
{
lean_object* v___x_27_; lean_object* v___x_28_; 
v___x_27_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__2, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__2_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__2);
v___x_28_ = lean_nat_to_int(v___x_27_);
return v___x_28_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15(void){
_start:
{
lean_object* v___x_47_; lean_object* v___x_48_; 
v___x_47_ = lean_unsigned_to_nat(0u);
v___x_48_ = lean_nat_to_int(v___x_47_);
return v___x_48_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__17(void){
_start:
{
lean_object* v___x_52_; lean_object* v___x_53_; 
v___x_52_ = lean_unsigned_to_nat(5u);
v___x_53_ = lean_nat_to_int(v___x_52_);
return v___x_53_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__22(void){
_start:
{
lean_object* v___x_60_; lean_object* v___x_61_; 
v___x_60_ = lean_unsigned_to_nat(6u);
v___x_61_ = lean_nat_to_int(v___x_60_);
return v___x_61_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg(lean_object* v_x_62_){
_start:
{
lean_object* v_x_63_; lean_object* v_y1_64_; lean_object* v_y2_65_; lean_object* v_num_66_; lean_object* v_den_67_; lean_object* v___x_69_; uint8_t v_isShared_70_; uint8_t v_isSharedCheck_190_; 
v_x_63_ = lean_ctor_get(v_x_62_, 0);
lean_inc_ref(v_x_63_);
v_y1_64_ = lean_ctor_get(v_x_62_, 1);
lean_inc_ref(v_y1_64_);
v_y2_65_ = lean_ctor_get(v_x_62_, 2);
lean_inc_ref(v_y2_65_);
lean_dec_ref(v_x_62_);
v_num_66_ = lean_ctor_get(v_x_63_, 0);
v_den_67_ = lean_ctor_get(v_x_63_, 1);
v_isSharedCheck_190_ = !lean_is_exclusive(v_x_63_);
if (v_isSharedCheck_190_ == 0)
{
v___x_69_ = v_x_63_;
v_isShared_70_ = v_isSharedCheck_190_;
goto v_resetjp_68_;
}
else
{
lean_inc(v_den_67_);
lean_inc(v_num_66_);
lean_dec(v_x_63_);
v___x_69_ = lean_box(0);
v_isShared_70_ = v_isSharedCheck_190_;
goto v_resetjp_68_;
}
v_resetjp_68_:
{
lean_object* v___y_72_; lean_object* v___y_73_; uint8_t v___y_74_; lean_object* v___y_75_; lean_object* v___x_88_; lean_object* v___y_90_; lean_object* v___y_91_; lean_object* v___y_92_; uint8_t v___y_93_; lean_object* v___y_94_; lean_object* v___y_95_; lean_object* v___x_130_; lean_object* v___x_131_; lean_object* v___y_133_; lean_object* v___x_172_; uint8_t v___x_173_; 
v___x_88_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__10));
v___x_130_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__16));
v___x_131_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__17, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__17_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__17);
v___x_172_ = lean_unsigned_to_nat(1u);
v___x_173_ = lean_nat_dec_eq(v_den_67_, v___x_172_);
if (v___x_173_ == 0)
{
lean_object* v___x_174_; lean_object* v___x_175_; lean_object* v___x_176_; lean_object* v___x_177_; lean_object* v___x_178_; lean_object* v___x_179_; lean_object* v___x_180_; lean_object* v___x_181_; 
v___x_174_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__13));
v___x_175_ = l_Int_repr(v_num_66_);
lean_dec(v_num_66_);
v___x_176_ = lean_string_append(v___x_174_, v___x_175_);
lean_dec_ref(v___x_175_);
v___x_177_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__14));
v___x_178_ = lean_string_append(v___x_176_, v___x_177_);
v___x_179_ = l_Nat_reprFast(v_den_67_);
v___x_180_ = lean_string_append(v___x_178_, v___x_179_);
lean_dec_ref(v___x_179_);
v___x_181_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_181_, 0, v___x_180_);
v___y_133_ = v___x_181_;
goto v___jp_132_;
}
else
{
lean_object* v___x_182_; lean_object* v___x_183_; uint8_t v___x_184_; 
lean_dec(v_den_67_);
v___x_182_ = lean_unsigned_to_nat(0u);
v___x_183_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15);
v___x_184_ = lean_int_dec_lt(v_num_66_, v___x_183_);
if (v___x_184_ == 0)
{
lean_object* v___x_185_; lean_object* v___x_186_; 
v___x_185_ = l_Int_repr(v_num_66_);
lean_dec(v_num_66_);
v___x_186_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_186_, 0, v___x_185_);
v___y_133_ = v___x_186_;
goto v___jp_132_;
}
else
{
lean_object* v___x_187_; lean_object* v___x_188_; lean_object* v___x_189_; 
v___x_187_ = l_Int_repr(v_num_66_);
lean_dec(v_num_66_);
v___x_188_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_188_, 0, v___x_187_);
v___x_189_ = l_Repr_addAppParen(v___x_188_, v___x_182_);
v___y_133_ = v___x_189_;
goto v___jp_132_;
}
}
v___jp_71_:
{
lean_object* v___x_77_; 
lean_inc(v___y_72_);
if (v_isShared_70_ == 0)
{
lean_ctor_set_tag(v___x_69_, 4);
lean_ctor_set(v___x_69_, 1, v___y_75_);
lean_ctor_set(v___x_69_, 0, v___y_72_);
v___x_77_ = v___x_69_;
goto v_reusejp_76_;
}
else
{
lean_object* v_reuseFailAlloc_87_; 
v_reuseFailAlloc_87_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_87_, 0, v___y_72_);
lean_ctor_set(v_reuseFailAlloc_87_, 1, v___y_75_);
v___x_77_ = v_reuseFailAlloc_87_;
goto v_reusejp_76_;
}
v_reusejp_76_:
{
lean_object* v___x_78_; lean_object* v___x_79_; lean_object* v___x_80_; lean_object* v___x_81_; lean_object* v___x_82_; lean_object* v___x_83_; lean_object* v___x_84_; lean_object* v___x_85_; lean_object* v___x_86_; 
v___x_78_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_78_, 0, v___x_77_);
lean_ctor_set_uint8(v___x_78_, sizeof(void*)*1, v___y_74_);
v___x_79_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_79_, 0, v___y_73_);
lean_ctor_set(v___x_79_, 1, v___x_78_);
v___x_80_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__3, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__3_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__3);
v___x_81_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__4));
v___x_82_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_82_, 0, v___x_81_);
lean_ctor_set(v___x_82_, 1, v___x_79_);
v___x_83_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__5));
v___x_84_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_84_, 0, v___x_82_);
lean_ctor_set(v___x_84_, 1, v___x_83_);
v___x_85_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_85_, 0, v___x_80_);
lean_ctor_set(v___x_85_, 1, v___x_84_);
v___x_86_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_86_, 0, v___x_85_);
lean_ctor_set_uint8(v___x_86_, sizeof(void*)*1, v___y_74_);
return v___x_86_;
}
}
v___jp_89_:
{
lean_object* v_num_96_; lean_object* v_den_97_; lean_object* v___x_99_; uint8_t v_isShared_100_; uint8_t v_isSharedCheck_129_; 
v_num_96_ = lean_ctor_get(v_y2_65_, 0);
v_den_97_ = lean_ctor_get(v_y2_65_, 1);
v_isSharedCheck_129_ = !lean_is_exclusive(v_y2_65_);
if (v_isSharedCheck_129_ == 0)
{
v___x_99_ = v_y2_65_;
v_isShared_100_ = v_isSharedCheck_129_;
goto v_resetjp_98_;
}
else
{
lean_inc(v_den_97_);
lean_inc(v_num_96_);
lean_dec(v_y2_65_);
v___x_99_ = lean_box(0);
v_isShared_100_ = v_isSharedCheck_129_;
goto v_resetjp_98_;
}
v_resetjp_98_:
{
lean_object* v___x_102_; 
lean_inc(v___y_90_);
if (v_isShared_100_ == 0)
{
lean_ctor_set_tag(v___x_99_, 4);
lean_ctor_set(v___x_99_, 1, v___y_95_);
lean_ctor_set(v___x_99_, 0, v___y_90_);
v___x_102_ = v___x_99_;
goto v_reusejp_101_;
}
else
{
lean_object* v_reuseFailAlloc_128_; 
v_reuseFailAlloc_128_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_128_, 0, v___y_90_);
lean_ctor_set(v_reuseFailAlloc_128_, 1, v___y_95_);
v___x_102_ = v_reuseFailAlloc_128_;
goto v_reusejp_101_;
}
v_reusejp_101_:
{
lean_object* v___x_103_; lean_object* v___x_104_; lean_object* v___x_105_; lean_object* v___x_106_; lean_object* v___x_107_; lean_object* v___x_108_; lean_object* v___x_109_; lean_object* v___x_110_; uint8_t v___x_111_; 
v___x_103_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_103_, 0, v___x_102_);
lean_ctor_set_uint8(v___x_103_, sizeof(void*)*1, v___y_93_);
v___x_104_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_104_, 0, v___y_94_);
lean_ctor_set(v___x_104_, 1, v___x_103_);
lean_inc(v___y_91_);
v___x_105_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_105_, 0, v___x_104_);
lean_ctor_set(v___x_105_, 1, v___y_91_);
lean_inc(v___y_92_);
v___x_106_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_106_, 0, v___x_105_);
lean_ctor_set(v___x_106_, 1, v___y_92_);
v___x_107_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__12));
v___x_108_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_108_, 0, v___x_106_);
lean_ctor_set(v___x_108_, 1, v___x_107_);
v___x_109_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_109_, 0, v___x_108_);
lean_ctor_set(v___x_109_, 1, v___x_88_);
v___x_110_ = lean_unsigned_to_nat(1u);
v___x_111_ = lean_nat_dec_eq(v_den_97_, v___x_110_);
if (v___x_111_ == 0)
{
lean_object* v___x_112_; lean_object* v___x_113_; lean_object* v___x_114_; lean_object* v___x_115_; lean_object* v___x_116_; lean_object* v___x_117_; lean_object* v___x_118_; lean_object* v___x_119_; 
v___x_112_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__13));
v___x_113_ = l_Int_repr(v_num_96_);
lean_dec(v_num_96_);
v___x_114_ = lean_string_append(v___x_112_, v___x_113_);
lean_dec_ref(v___x_113_);
v___x_115_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__14));
v___x_116_ = lean_string_append(v___x_114_, v___x_115_);
v___x_117_ = l_Nat_reprFast(v_den_97_);
v___x_118_ = lean_string_append(v___x_116_, v___x_117_);
lean_dec_ref(v___x_117_);
v___x_119_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_119_, 0, v___x_118_);
v___y_72_ = v___y_90_;
v___y_73_ = v___x_109_;
v___y_74_ = v___y_93_;
v___y_75_ = v___x_119_;
goto v___jp_71_;
}
else
{
lean_object* v___x_120_; lean_object* v___x_121_; uint8_t v___x_122_; 
lean_dec(v_den_97_);
v___x_120_ = lean_unsigned_to_nat(0u);
v___x_121_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15);
v___x_122_ = lean_int_dec_lt(v_num_96_, v___x_121_);
if (v___x_122_ == 0)
{
lean_object* v___x_123_; lean_object* v___x_124_; 
v___x_123_ = l_Int_repr(v_num_96_);
lean_dec(v_num_96_);
v___x_124_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_124_, 0, v___x_123_);
v___y_72_ = v___y_90_;
v___y_73_ = v___x_109_;
v___y_74_ = v___y_93_;
v___y_75_ = v___x_124_;
goto v___jp_71_;
}
else
{
lean_object* v___x_125_; lean_object* v___x_126_; lean_object* v___x_127_; 
v___x_125_ = l_Int_repr(v_num_96_);
lean_dec(v_num_96_);
v___x_126_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_126_, 0, v___x_125_);
v___x_127_ = l_Repr_addAppParen(v___x_126_, v___x_120_);
v___y_72_ = v___y_90_;
v___y_73_ = v___x_109_;
v___y_74_ = v___y_93_;
v___y_75_ = v___x_127_;
goto v___jp_71_;
}
}
}
}
}
v___jp_132_:
{
lean_object* v_num_134_; lean_object* v_den_135_; lean_object* v___x_137_; uint8_t v_isShared_138_; uint8_t v_isSharedCheck_171_; 
v_num_134_ = lean_ctor_get(v_y1_64_, 0);
v_den_135_ = lean_ctor_get(v_y1_64_, 1);
v_isSharedCheck_171_ = !lean_is_exclusive(v_y1_64_);
if (v_isSharedCheck_171_ == 0)
{
v___x_137_ = v_y1_64_;
v_isShared_138_ = v_isSharedCheck_171_;
goto v_resetjp_136_;
}
else
{
lean_inc(v_den_135_);
lean_inc(v_num_134_);
lean_dec(v_y1_64_);
v___x_137_ = lean_box(0);
v_isShared_138_ = v_isSharedCheck_171_;
goto v_resetjp_136_;
}
v_resetjp_136_:
{
lean_object* v___x_140_; 
if (v_isShared_138_ == 0)
{
lean_ctor_set_tag(v___x_137_, 4);
lean_ctor_set(v___x_137_, 1, v___y_133_);
lean_ctor_set(v___x_137_, 0, v___x_131_);
v___x_140_ = v___x_137_;
goto v_reusejp_139_;
}
else
{
lean_object* v_reuseFailAlloc_170_; 
v_reuseFailAlloc_170_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v_reuseFailAlloc_170_, 0, v___x_131_);
lean_ctor_set(v_reuseFailAlloc_170_, 1, v___y_133_);
v___x_140_ = v_reuseFailAlloc_170_;
goto v_reusejp_139_;
}
v_reusejp_139_:
{
uint8_t v___x_141_; lean_object* v___x_142_; lean_object* v___x_143_; lean_object* v___x_144_; lean_object* v___x_145_; lean_object* v___x_146_; lean_object* v___x_147_; lean_object* v___x_148_; lean_object* v___x_149_; lean_object* v___x_150_; lean_object* v___x_151_; lean_object* v___x_152_; uint8_t v___x_153_; 
v___x_141_ = 0;
v___x_142_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_142_, 0, v___x_140_);
lean_ctor_set_uint8(v___x_142_, sizeof(void*)*1, v___x_141_);
v___x_143_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_143_, 0, v___x_130_);
lean_ctor_set(v___x_143_, 1, v___x_142_);
v___x_144_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__19));
v___x_145_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_145_, 0, v___x_143_);
lean_ctor_set(v___x_145_, 1, v___x_144_);
v___x_146_ = lean_box(1);
v___x_147_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_147_, 0, v___x_145_);
lean_ctor_set(v___x_147_, 1, v___x_146_);
v___x_148_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__21));
v___x_149_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_149_, 0, v___x_147_);
lean_ctor_set(v___x_149_, 1, v___x_148_);
v___x_150_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_150_, 0, v___x_149_);
lean_ctor_set(v___x_150_, 1, v___x_88_);
v___x_151_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__22, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__22_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__22);
v___x_152_ = lean_unsigned_to_nat(1u);
v___x_153_ = lean_nat_dec_eq(v_den_135_, v___x_152_);
if (v___x_153_ == 0)
{
lean_object* v___x_154_; lean_object* v___x_155_; lean_object* v___x_156_; lean_object* v___x_157_; lean_object* v___x_158_; lean_object* v___x_159_; lean_object* v___x_160_; lean_object* v___x_161_; 
v___x_154_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__13));
v___x_155_ = l_Int_repr(v_num_134_);
lean_dec(v_num_134_);
v___x_156_ = lean_string_append(v___x_154_, v___x_155_);
lean_dec_ref(v___x_155_);
v___x_157_ = ((lean_object*)(lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__14));
v___x_158_ = lean_string_append(v___x_156_, v___x_157_);
v___x_159_ = l_Nat_reprFast(v_den_135_);
v___x_160_ = lean_string_append(v___x_158_, v___x_159_);
lean_dec_ref(v___x_159_);
v___x_161_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_161_, 0, v___x_160_);
v___y_90_ = v___x_151_;
v___y_91_ = v___x_144_;
v___y_92_ = v___x_146_;
v___y_93_ = v___x_141_;
v___y_94_ = v___x_150_;
v___y_95_ = v___x_161_;
goto v___jp_89_;
}
else
{
lean_object* v___x_162_; lean_object* v___x_163_; uint8_t v___x_164_; 
lean_dec(v_den_135_);
v___x_162_ = lean_unsigned_to_nat(0u);
v___x_163_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15, &lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15_once, _init_lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg___closed__15);
v___x_164_ = lean_int_dec_lt(v_num_134_, v___x_163_);
if (v___x_164_ == 0)
{
lean_object* v___x_165_; lean_object* v___x_166_; 
v___x_165_ = l_Int_repr(v_num_134_);
lean_dec(v_num_134_);
v___x_166_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_166_, 0, v___x_165_);
v___y_90_ = v___x_151_;
v___y_91_ = v___x_144_;
v___y_92_ = v___x_146_;
v___y_93_ = v___x_141_;
v___y_94_ = v___x_150_;
v___y_95_ = v___x_166_;
goto v___jp_89_;
}
else
{
lean_object* v___x_167_; lean_object* v___x_168_; lean_object* v___x_169_; 
v___x_167_ = l_Int_repr(v_num_134_);
lean_dec(v_num_134_);
v___x_168_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_168_, 0, v___x_167_);
v___x_169_ = l_Repr_addAppParen(v___x_168_, v___x_162_);
v___y_90_ = v___x_151_;
v___y_91_ = v___x_144_;
v___y_92_ = v___x_146_;
v___y_93_ = v___x_141_;
v___y_94_ = v___x_150_;
v___y_95_ = v___x_169_;
goto v___jp_89_;
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr(lean_object* v_x_191_, lean_object* v_prec_192_){
_start:
{
lean_object* v___x_193_; 
v___x_193_ = lp_lean__proofs_MachineMarkets_instReprVec3_repr___redArg(v_x_191_);
return v___x_193_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_instReprVec3_repr___boxed(lean_object* v_x_194_, lean_object* v_prec_195_){
_start:
{
lean_object* v_res_196_; 
v_res_196_ = lp_lean__proofs_MachineMarkets_instReprVec3_repr(v_x_194_, v_prec_195_);
lean_dec(v_prec_195_);
return v_res_196_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_C__dot(lean_object* v_v_199_){
_start:
{
lean_object* v_x_200_; 
v_x_200_ = lean_ctor_get(v_v_199_, 0);
lean_inc_ref(v_x_200_);
return v_x_200_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_C__dot___boxed(lean_object* v_v_201_){
_start:
{
lean_object* v_res_202_; 
v_res_202_ = lp_lean__proofs_MachineMarkets_C__dot(v_v_201_);
lean_dec_ref(v_v_201_);
return v_res_202_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_J__mul___closed__0(void){
_start:
{
lean_object* v___x_203_; lean_object* v___x_204_; 
v___x_203_ = lean_unsigned_to_nat(1u);
v___x_204_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_203_);
return v___x_204_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_J__mul(lean_object* v_a_205_, lean_object* v_eta_206_, lean_object* v_q1_207_, lean_object* v_q2_208_, lean_object* v_v_209_){
_start:
{
lean_object* v_x_210_; lean_object* v_y1_211_; lean_object* v_y2_212_; lean_object* v___x_214_; uint8_t v_isShared_215_; uint8_t v_isSharedCheck_232_; 
v_x_210_ = lean_ctor_get(v_v_209_, 0);
v_y1_211_ = lean_ctor_get(v_v_209_, 1);
v_y2_212_ = lean_ctor_get(v_v_209_, 2);
v_isSharedCheck_232_ = !lean_is_exclusive(v_v_209_);
if (v_isSharedCheck_232_ == 0)
{
v___x_214_ = v_v_209_;
v_isShared_215_ = v_isSharedCheck_232_;
goto v_resetjp_213_;
}
else
{
lean_inc(v_y2_212_);
lean_inc(v_y1_211_);
lean_inc(v_x_210_);
lean_dec(v_v_209_);
v___x_214_ = lean_box(0);
v_isShared_215_ = v_isSharedCheck_232_;
goto v_resetjp_213_;
}
v_resetjp_213_:
{
lean_object* v___x_216_; lean_object* v___x_217_; lean_object* v___x_218_; lean_object* v___x_219_; lean_object* v___x_220_; lean_object* v___x_221_; lean_object* v___x_222_; lean_object* v___x_223_; lean_object* v___x_224_; lean_object* v___x_225_; lean_object* v___x_226_; lean_object* v___x_227_; lean_object* v___x_228_; lean_object* v___x_230_; 
lean_inc_ref_n(v_x_210_, 2);
v___x_216_ = l_Rat_mul(v_a_205_, v_x_210_);
lean_inc_ref(v_y1_211_);
v___x_217_ = l_Rat_add(v___x_216_, v_y1_211_);
lean_inc_ref(v_y2_212_);
v___x_218_ = l_Rat_add(v___x_217_, v_y2_212_);
v___x_219_ = l_Rat_mul(v_eta_206_, v_q1_207_);
v___x_220_ = l_Rat_mul(v___x_219_, v_x_210_);
lean_dec_ref(v___x_219_);
v___x_221_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_J__mul___closed__0, &lp_lean__proofs_MachineMarkets_J__mul___closed__0_once, _init_lp_lean__proofs_MachineMarkets_J__mul___closed__0);
lean_inc_ref(v_eta_206_);
v___x_222_ = l_Rat_sub(v___x_221_, v_eta_206_);
v___x_223_ = l_Rat_mul(v___x_222_, v_y1_211_);
v___x_224_ = l_Rat_add(v___x_220_, v___x_223_);
v___x_225_ = l_Rat_mul(v_eta_206_, v_q2_208_);
lean_dec_ref(v_eta_206_);
v___x_226_ = l_Rat_mul(v___x_225_, v_x_210_);
lean_dec_ref(v___x_225_);
v___x_227_ = l_Rat_mul(v___x_222_, v_y2_212_);
lean_dec_ref(v___x_222_);
v___x_228_ = l_Rat_add(v___x_226_, v___x_227_);
if (v_isShared_215_ == 0)
{
lean_ctor_set(v___x_214_, 2, v___x_228_);
lean_ctor_set(v___x_214_, 1, v___x_224_);
lean_ctor_set(v___x_214_, 0, v___x_218_);
v___x_230_ = v___x_214_;
goto v_reusejp_229_;
}
else
{
lean_object* v_reuseFailAlloc_231_; 
v_reuseFailAlloc_231_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v_reuseFailAlloc_231_, 0, v___x_218_);
lean_ctor_set(v_reuseFailAlloc_231_, 1, v___x_224_);
lean_ctor_set(v_reuseFailAlloc_231_, 2, v___x_228_);
v___x_230_ = v_reuseFailAlloc_231_;
goto v_reusejp_229_;
}
v_reusejp_229_:
{
return v___x_230_;
}
}
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_J__mul___boxed(lean_object* v_a_233_, lean_object* v_eta_234_, lean_object* v_q1_235_, lean_object* v_q2_236_, lean_object* v_v_237_){
_start:
{
lean_object* v_res_238_; 
v_res_238_ = lp_lean__proofs_MachineMarkets_J__mul(v_a_233_, v_eta_234_, v_q1_235_, v_q2_236_, v_v_237_);
lean_dec_ref(v_a_233_);
return v_res_238_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__0(void){
_start:
{
lean_object* v___x_239_; lean_object* v___x_240_; 
v___x_239_ = lean_unsigned_to_nat(0u);
v___x_240_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_239_);
return v___x_240_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__1(void){
_start:
{
lean_object* v___x_241_; lean_object* v___x_242_; 
v___x_241_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_J__mul___closed__0, &lp_lean__proofs_MachineMarkets_J__mul___closed__0_once, _init_lp_lean__proofs_MachineMarkets_J__mul___closed__0);
v___x_242_ = l_Rat_neg(v___x_241_);
return v___x_242_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__2(void){
_start:
{
lean_object* v___x_243_; lean_object* v___x_244_; lean_object* v___x_245_; lean_object* v___x_246_; 
v___x_243_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__1, &lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__1_once, _init_lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__1);
v___x_244_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_J__mul___closed__0, &lp_lean__proofs_MachineMarkets_J__mul___closed__0_once, _init_lp_lean__proofs_MachineMarkets_J__mul___closed__0);
v___x_245_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__0, &lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__0_once, _init_lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__0);
v___x_246_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v___x_246_, 0, v___x_245_);
lean_ctor_set(v___x_246_, 1, v___x_244_);
lean_ctor_set(v___x_246_, 2, v___x_243_);
return v___x_246_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_pbh__null__vec(void){
_start:
{
lean_object* v___x_247_; 
v___x_247_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__2, &lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__2_once, _init_lp_lean__proofs_MachineMarkets_pbh__null__vec___closed__2);
return v___x_247_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_transferDenom(lean_object* v_a_248_, lean_object* v_eta_249_, lean_object* v_Q_250_, lean_object* v_z_251_){
_start:
{
lean_object* v___x_252_; lean_object* v___x_253_; lean_object* v___x_254_; lean_object* v___x_255_; lean_object* v___x_256_; lean_object* v___x_257_; lean_object* v___x_258_; 
lean_inc_ref(v_z_251_);
v___x_252_ = l_Rat_sub(v_z_251_, v_a_248_);
v___x_253_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_J__mul___closed__0, &lp_lean__proofs_MachineMarkets_J__mul___closed__0_once, _init_lp_lean__proofs_MachineMarkets_J__mul___closed__0);
v___x_254_ = l_Rat_sub(v_z_251_, v___x_253_);
lean_inc_ref(v_eta_249_);
v___x_255_ = l_Rat_add(v___x_254_, v_eta_249_);
v___x_256_ = l_Rat_mul(v___x_252_, v___x_255_);
lean_dec_ref(v___x_252_);
v___x_257_ = l_Rat_mul(v_eta_249_, v_Q_250_);
lean_dec_ref(v_eta_249_);
v___x_258_ = l_Rat_sub(v___x_256_, v___x_257_);
return v___x_258_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_channelResponse(lean_object* v_eta_259_, lean_object* v_u1_260_, lean_object* v_u2_261_, lean_object* v_q1_262_, lean_object* v_q2_263_){
_start:
{
lean_object* v___x_264_; lean_object* v___x_265_; lean_object* v___x_266_; lean_object* v___x_267_; 
v___x_264_ = l_Rat_mul(v_u1_260_, v_q1_262_);
v___x_265_ = l_Rat_mul(v_u2_261_, v_q2_263_);
v___x_266_ = l_Rat_add(v___x_264_, v___x_265_);
v___x_267_ = l_Rat_mul(v_eta_259_, v___x_266_);
return v___x_267_;
}
}
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_channelResponse___boxed(lean_object* v_eta_268_, lean_object* v_u1_269_, lean_object* v_u2_270_, lean_object* v_q1_271_, lean_object* v_q2_272_){
_start:
{
lean_object* v_res_273_; 
v_res_273_ = lp_lean__proofs_MachineMarkets_channelResponse(v_eta_268_, v_u1_269_, v_u2_270_, v_q1_271_, v_q2_272_);
lean_dec_ref(v_u2_270_);
lean_dec_ref(v_u1_269_);
lean_dec_ref(v_eta_268_);
return v_res_273_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init_GrindInstances_Ring_Rat(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_lean__proofs_Proofs_PBHDefect(uint8_t builtin) {
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
lp_lean__proofs_MachineMarkets_pbh__null__vec = _init_lp_lean__proofs_MachineMarkets_pbh__null__vec();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_pbh__null__vec);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
