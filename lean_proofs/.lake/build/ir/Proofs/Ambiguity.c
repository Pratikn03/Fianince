// Lean compiler output
// Module: Proofs.Ambiguity
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
lean_object* l_Rat_div(lean_object*, lean_object*);
lean_object* l_Rat_sub(lean_object*, lean_object*);
lean_object* l_Rat_mul(lean_object*, lean_object*);
lean_object* l_Rat_add(lean_object*, lean_object*);
lean_object* l_Rat_pow(lean_object*, lean_object*);
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q0__1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q0__1___closed__0;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_q0__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q0__2___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q0__2___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q0__2___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q0__2___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q0__2___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q0__2___closed__2;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_q0__2;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_q0__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q1__1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q1__1___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q1__1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q1__1___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q1__1___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q1__1___closed__2;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_q1__1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_q1__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q1__3___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q1__3___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q1__3___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q1__3___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_q1__3___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_q1__3___closed__2;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_q1__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_eta__1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_eta__1___closed__0;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_eta__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_eta__2___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_eta__2___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_eta__2___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_eta__2___closed__1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_eta__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_eta__3___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_eta__3___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_eta__3___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_eta__3___closed__1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_eta__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_a__market___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_a__market___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_a__market___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_a__market___closed__1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_a__market;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_Q0___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_Q0___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_Q0___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_Q0___closed__1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_Q0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_Q1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_Q1___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_Q1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_Q1___closed__1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_Q1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod0___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod0___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod0___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod0___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod0___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod0___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod0___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod0___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod0___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod0___closed__4;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_k0__mod0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod1___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod1___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod1___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod1___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod1___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod1___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k0__mod1___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k0__mod1___closed__4;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_k0__mod1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__4;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__5;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__6;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod0___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod0___closed__7;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_k1__mod0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod1___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod1___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod1___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod1___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod1___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod1___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k1__mod1___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k1__mod1___closed__4;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_k1__mod1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__4;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__5;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__6;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod0___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod0___closed__7;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_k2__mod0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod1___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod1___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod1___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod1___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod1___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod1___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_k2__mod1___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_k2__mod1___closed__4;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_k2__mod1;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_h0;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_h1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h2___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h2___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h2___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h2___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h2___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h2___closed__2;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_h2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h3___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h3___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h3___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h3___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h3___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h3___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h3___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h3___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h3___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h3___closed__4;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_h3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__4;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__5;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod0___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod0___closed__6;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_h4__mod0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod1___closed__0;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod1___closed__1;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod1___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod1___closed__2;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod1___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod1___closed__3;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod1___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod1___closed__4;
static lean_once_cell_t lp_lean__proofs_MachineMarkets_h4__mod1___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_lean__proofs_MachineMarkets_h4__mod1___closed__5;
LEAN_EXPORT lean_object* lp_lean__proofs_MachineMarkets_h4__mod1;
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__1___closed__0(void){
_start:
{
lean_object* v___x_1_; lean_object* v___x_2_; 
v___x_1_ = lean_unsigned_to_nat(0u);
v___x_2_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_1_);
return v___x_2_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__1(void){
_start:
{
lean_object* v___x_3_; 
v___x_3_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q0__1___closed__0, &lp_lean__proofs_MachineMarkets_q0__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_q0__1___closed__0);
return v___x_3_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__2___closed__0(void){
_start:
{
lean_object* v___x_4_; lean_object* v___x_5_; 
v___x_4_ = lean_unsigned_to_nat(12u);
v___x_5_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_4_);
return v___x_5_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__2___closed__1(void){
_start:
{
lean_object* v___x_6_; lean_object* v___x_7_; 
v___x_6_ = lean_unsigned_to_nat(65u);
v___x_7_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_6_);
return v___x_7_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__2___closed__2(void){
_start:
{
lean_object* v___x_8_; lean_object* v___x_9_; lean_object* v___x_10_; 
v___x_8_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q0__2___closed__1, &lp_lean__proofs_MachineMarkets_q0__2___closed__1_once, _init_lp_lean__proofs_MachineMarkets_q0__2___closed__1);
v___x_9_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q0__2___closed__0, &lp_lean__proofs_MachineMarkets_q0__2___closed__0_once, _init_lp_lean__proofs_MachineMarkets_q0__2___closed__0);
v___x_10_ = l_Rat_div(v___x_9_, v___x_8_);
return v___x_10_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__2(void){
_start:
{
lean_object* v___x_11_; 
v___x_11_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q0__2___closed__2, &lp_lean__proofs_MachineMarkets_q0__2___closed__2_once, _init_lp_lean__proofs_MachineMarkets_q0__2___closed__2);
return v___x_11_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q0__3(void){
_start:
{
lean_object* v___x_12_; 
v___x_12_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q0__1___closed__0, &lp_lean__proofs_MachineMarkets_q0__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_q0__1___closed__0);
return v___x_12_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__1___closed__0(void){
_start:
{
lean_object* v___x_13_; lean_object* v___x_14_; 
v___x_13_ = lean_unsigned_to_nat(54u);
v___x_14_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_13_);
return v___x_14_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__1___closed__1(void){
_start:
{
lean_object* v___x_15_; lean_object* v___x_16_; 
v___x_15_ = lean_unsigned_to_nat(1235u);
v___x_16_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_15_);
return v___x_16_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__1___closed__2(void){
_start:
{
lean_object* v___x_17_; lean_object* v___x_18_; lean_object* v___x_19_; 
v___x_17_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q1__1___closed__1, &lp_lean__proofs_MachineMarkets_q1__1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_q1__1___closed__1);
v___x_18_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q1__1___closed__0, &lp_lean__proofs_MachineMarkets_q1__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_q1__1___closed__0);
v___x_19_ = l_Rat_div(v___x_18_, v___x_17_);
return v___x_19_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__1(void){
_start:
{
lean_object* v___x_20_; 
v___x_20_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q1__1___closed__2, &lp_lean__proofs_MachineMarkets_q1__1___closed__2_once, _init_lp_lean__proofs_MachineMarkets_q1__1___closed__2);
return v___x_20_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__2(void){
_start:
{
lean_object* v___x_21_; 
v___x_21_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q0__1___closed__0, &lp_lean__proofs_MachineMarkets_q0__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_q0__1___closed__0);
return v___x_21_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__3___closed__0(void){
_start:
{
lean_object* v___x_22_; lean_object* v___x_23_; 
v___x_22_ = lean_unsigned_to_nat(240u);
v___x_23_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_22_);
return v___x_23_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__3___closed__1(void){
_start:
{
lean_object* v___x_24_; lean_object* v___x_25_; 
v___x_24_ = lean_unsigned_to_nat(247u);
v___x_25_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_24_);
return v___x_25_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__3___closed__2(void){
_start:
{
lean_object* v___x_26_; lean_object* v___x_27_; lean_object* v___x_28_; 
v___x_26_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q1__3___closed__1, &lp_lean__proofs_MachineMarkets_q1__3___closed__1_once, _init_lp_lean__proofs_MachineMarkets_q1__3___closed__1);
v___x_27_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q1__3___closed__0, &lp_lean__proofs_MachineMarkets_q1__3___closed__0_once, _init_lp_lean__proofs_MachineMarkets_q1__3___closed__0);
v___x_28_ = l_Rat_div(v___x_27_, v___x_26_);
return v___x_28_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_q1__3(void){
_start:
{
lean_object* v___x_29_; 
v___x_29_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_q1__3___closed__2, &lp_lean__proofs_MachineMarkets_q1__3___closed__2_once, _init_lp_lean__proofs_MachineMarkets_q1__3___closed__2);
return v___x_29_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0(void){
_start:
{
lean_object* v___x_30_; lean_object* v___x_31_; 
v___x_30_ = lean_unsigned_to_nat(1u);
v___x_31_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_30_);
return v___x_31_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__1(void){
_start:
{
lean_object* v___x_32_; 
v___x_32_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
return v___x_32_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__2___closed__0(void){
_start:
{
lean_object* v___x_33_; lean_object* v___x_34_; 
v___x_33_ = lean_unsigned_to_nat(2u);
v___x_34_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_33_);
return v___x_34_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__2___closed__1(void){
_start:
{
lean_object* v___x_35_; lean_object* v___x_36_; lean_object* v___x_37_; 
v___x_35_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__2___closed__0, &lp_lean__proofs_MachineMarkets_eta__2___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__2___closed__0);
v___x_36_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
v___x_37_ = l_Rat_div(v___x_36_, v___x_35_);
return v___x_37_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__2(void){
_start:
{
lean_object* v___x_38_; 
v___x_38_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__2___closed__1, &lp_lean__proofs_MachineMarkets_eta__2___closed__1_once, _init_lp_lean__proofs_MachineMarkets_eta__2___closed__1);
return v___x_38_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__3___closed__0(void){
_start:
{
lean_object* v___x_39_; lean_object* v___x_40_; 
v___x_39_ = lean_unsigned_to_nat(20u);
v___x_40_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_39_);
return v___x_40_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__3___closed__1(void){
_start:
{
lean_object* v___x_41_; lean_object* v___x_42_; lean_object* v___x_43_; 
v___x_41_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__3___closed__0, &lp_lean__proofs_MachineMarkets_eta__3___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__3___closed__0);
v___x_42_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
v___x_43_ = l_Rat_div(v___x_42_, v___x_41_);
return v___x_43_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_eta__3(void){
_start:
{
lean_object* v___x_44_; 
v___x_44_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__3___closed__1, &lp_lean__proofs_MachineMarkets_eta__3___closed__1_once, _init_lp_lean__proofs_MachineMarkets_eta__3___closed__1);
return v___x_44_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_a__market___closed__0(void){
_start:
{
lean_object* v___x_45_; lean_object* v___x_46_; 
v___x_45_ = lean_unsigned_to_nat(5u);
v___x_46_ = l_Nat_cast___at___00Dyadic_toRat_spec__0(v___x_45_);
return v___x_46_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_a__market___closed__1(void){
_start:
{
lean_object* v___x_47_; lean_object* v___x_48_; lean_object* v___x_49_; 
v___x_47_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_a__market___closed__0, &lp_lean__proofs_MachineMarkets_a__market___closed__0_once, _init_lp_lean__proofs_MachineMarkets_a__market___closed__0);
v___x_48_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__2___closed__0, &lp_lean__proofs_MachineMarkets_eta__2___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__2___closed__0);
v___x_49_ = l_Rat_div(v___x_48_, v___x_47_);
return v___x_49_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_a__market(void){
_start:
{
lean_object* v___x_50_; 
v___x_50_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_a__market___closed__1, &lp_lean__proofs_MachineMarkets_a__market___closed__1_once, _init_lp_lean__proofs_MachineMarkets_a__market___closed__1);
return v___x_50_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_Q0___closed__0(void){
_start:
{
lean_object* v___x_51_; lean_object* v___x_52_; lean_object* v___x_53_; 
v___x_51_ = lp_lean__proofs_MachineMarkets_q0__2;
v___x_52_ = lp_lean__proofs_MachineMarkets_q0__1;
v___x_53_ = l_Rat_add(v___x_52_, v___x_51_);
return v___x_53_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_Q0___closed__1(void){
_start:
{
lean_object* v___x_54_; lean_object* v___x_55_; lean_object* v___x_56_; 
v___x_54_ = lp_lean__proofs_MachineMarkets_q0__3;
v___x_55_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_Q0___closed__0, &lp_lean__proofs_MachineMarkets_Q0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_Q0___closed__0);
v___x_56_ = l_Rat_add(v___x_55_, v___x_54_);
return v___x_56_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_Q0(void){
_start:
{
lean_object* v___x_57_; 
v___x_57_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_Q0___closed__1, &lp_lean__proofs_MachineMarkets_Q0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_Q0___closed__1);
return v___x_57_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_Q1___closed__0(void){
_start:
{
lean_object* v___x_58_; lean_object* v___x_59_; lean_object* v___x_60_; 
v___x_58_ = lp_lean__proofs_MachineMarkets_q1__2;
v___x_59_ = lp_lean__proofs_MachineMarkets_q1__1;
v___x_60_ = l_Rat_add(v___x_59_, v___x_58_);
return v___x_60_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_Q1___closed__1(void){
_start:
{
lean_object* v___x_61_; lean_object* v___x_62_; lean_object* v___x_63_; 
v___x_61_ = lp_lean__proofs_MachineMarkets_q1__3;
v___x_62_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_Q1___closed__0, &lp_lean__proofs_MachineMarkets_Q1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_Q1___closed__0);
v___x_63_ = l_Rat_add(v___x_62_, v___x_61_);
return v___x_63_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_Q1(void){
_start:
{
lean_object* v___x_64_; 
v___x_64_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_Q1___closed__1, &lp_lean__proofs_MachineMarkets_Q1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_Q1___closed__1);
return v___x_64_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__0(void){
_start:
{
lean_object* v___x_65_; lean_object* v___x_66_; lean_object* v___x_67_; 
v___x_65_ = lp_lean__proofs_MachineMarkets_eta__1;
v___x_66_ = lp_lean__proofs_MachineMarkets_q0__1;
v___x_67_ = l_Rat_mul(v___x_66_, v___x_65_);
return v___x_67_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__1(void){
_start:
{
lean_object* v___x_68_; lean_object* v___x_69_; lean_object* v___x_70_; 
v___x_68_ = lp_lean__proofs_MachineMarkets_eta__2;
v___x_69_ = lp_lean__proofs_MachineMarkets_q0__2;
v___x_70_ = l_Rat_mul(v___x_69_, v___x_68_);
return v___x_70_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__2(void){
_start:
{
lean_object* v___x_71_; lean_object* v___x_72_; lean_object* v___x_73_; 
v___x_71_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__1, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__1);
v___x_72_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__0);
v___x_73_ = l_Rat_add(v___x_72_, v___x_71_);
return v___x_73_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__3(void){
_start:
{
lean_object* v___x_74_; lean_object* v___x_75_; lean_object* v___x_76_; 
v___x_74_ = lp_lean__proofs_MachineMarkets_eta__3;
v___x_75_ = lp_lean__proofs_MachineMarkets_q0__3;
v___x_76_ = l_Rat_mul(v___x_75_, v___x_74_);
return v___x_76_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__4(void){
_start:
{
lean_object* v___x_77_; lean_object* v___x_78_; lean_object* v___x_79_; 
v___x_77_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__3, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__3);
v___x_78_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__2, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__2);
v___x_79_ = l_Rat_add(v___x_78_, v___x_77_);
return v___x_79_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod0(void){
_start:
{
lean_object* v___x_80_; 
v___x_80_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__4, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__4_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__4);
return v___x_80_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__0(void){
_start:
{
lean_object* v___x_81_; lean_object* v___x_82_; lean_object* v___x_83_; 
v___x_81_ = lp_lean__proofs_MachineMarkets_eta__1;
v___x_82_ = lp_lean__proofs_MachineMarkets_q1__1;
v___x_83_ = l_Rat_mul(v___x_82_, v___x_81_);
return v___x_83_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__1(void){
_start:
{
lean_object* v___x_84_; lean_object* v___x_85_; lean_object* v___x_86_; 
v___x_84_ = lp_lean__proofs_MachineMarkets_eta__2;
v___x_85_ = lp_lean__proofs_MachineMarkets_q1__2;
v___x_86_ = l_Rat_mul(v___x_85_, v___x_84_);
return v___x_86_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__2(void){
_start:
{
lean_object* v___x_87_; lean_object* v___x_88_; lean_object* v___x_89_; 
v___x_87_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__1, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__1);
v___x_88_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__0, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__0);
v___x_89_ = l_Rat_add(v___x_88_, v___x_87_);
return v___x_89_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__3(void){
_start:
{
lean_object* v___x_90_; lean_object* v___x_91_; lean_object* v___x_92_; 
v___x_90_ = lp_lean__proofs_MachineMarkets_eta__3;
v___x_91_ = lp_lean__proofs_MachineMarkets_q1__3;
v___x_92_ = l_Rat_mul(v___x_91_, v___x_90_);
return v___x_92_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__4(void){
_start:
{
lean_object* v___x_93_; lean_object* v___x_94_; lean_object* v___x_95_; 
v___x_93_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__3, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__3);
v___x_94_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__2, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__2);
v___x_95_ = l_Rat_add(v___x_94_, v___x_93_);
return v___x_95_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k0__mod1(void){
_start:
{
lean_object* v___x_96_; 
v___x_96_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__4, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__4_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__4);
return v___x_96_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__0(void){
_start:
{
lean_object* v___x_97_; lean_object* v___x_98_; lean_object* v___x_99_; 
v___x_97_ = lp_lean__proofs_MachineMarkets_eta__1;
v___x_98_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
v___x_99_ = l_Rat_sub(v___x_98_, v___x_97_);
return v___x_99_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__1(void){
_start:
{
lean_object* v___x_100_; lean_object* v___x_101_; lean_object* v___x_102_; 
v___x_100_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__0);
v___x_101_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__0);
v___x_102_ = l_Rat_mul(v___x_101_, v___x_100_);
return v___x_102_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__2(void){
_start:
{
lean_object* v___x_103_; lean_object* v___x_104_; lean_object* v___x_105_; 
v___x_103_ = lp_lean__proofs_MachineMarkets_eta__2;
v___x_104_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
v___x_105_ = l_Rat_sub(v___x_104_, v___x_103_);
return v___x_105_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__3(void){
_start:
{
lean_object* v___x_106_; lean_object* v___x_107_; lean_object* v___x_108_; 
v___x_106_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__2, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__2);
v___x_107_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__1, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__1);
v___x_108_ = l_Rat_mul(v___x_107_, v___x_106_);
return v___x_108_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__4(void){
_start:
{
lean_object* v___x_109_; lean_object* v___x_110_; lean_object* v___x_111_; 
v___x_109_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__3, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__3);
v___x_110_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__1, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__1);
v___x_111_ = l_Rat_add(v___x_110_, v___x_109_);
return v___x_111_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__5(void){
_start:
{
lean_object* v___x_112_; lean_object* v___x_113_; lean_object* v___x_114_; 
v___x_112_ = lp_lean__proofs_MachineMarkets_eta__3;
v___x_113_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
v___x_114_ = l_Rat_sub(v___x_113_, v___x_112_);
return v___x_114_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__6(void){
_start:
{
lean_object* v___x_115_; lean_object* v___x_116_; lean_object* v___x_117_; 
v___x_115_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__5, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__5_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__5);
v___x_116_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__3, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__3);
v___x_117_ = l_Rat_mul(v___x_116_, v___x_115_);
return v___x_117_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__7(void){
_start:
{
lean_object* v___x_118_; lean_object* v___x_119_; lean_object* v___x_120_; 
v___x_118_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__6, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__6_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__6);
v___x_119_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__4, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__4_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__4);
v___x_120_ = l_Rat_add(v___x_119_, v___x_118_);
return v___x_120_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod0(void){
_start:
{
lean_object* v___x_121_; 
v___x_121_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__7, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__7_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__7);
return v___x_121_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__0(void){
_start:
{
lean_object* v___x_122_; lean_object* v___x_123_; lean_object* v___x_124_; 
v___x_122_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__0);
v___x_123_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__0, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__0);
v___x_124_ = l_Rat_mul(v___x_123_, v___x_122_);
return v___x_124_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__1(void){
_start:
{
lean_object* v___x_125_; lean_object* v___x_126_; lean_object* v___x_127_; 
v___x_125_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__2, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__2);
v___x_126_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__1, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__1);
v___x_127_ = l_Rat_mul(v___x_126_, v___x_125_);
return v___x_127_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__2(void){
_start:
{
lean_object* v___x_128_; lean_object* v___x_129_; lean_object* v___x_130_; 
v___x_128_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod1___closed__1, &lp_lean__proofs_MachineMarkets_k1__mod1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__1);
v___x_129_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod1___closed__0, &lp_lean__proofs_MachineMarkets_k1__mod1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__0);
v___x_130_ = l_Rat_add(v___x_129_, v___x_128_);
return v___x_130_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__3(void){
_start:
{
lean_object* v___x_131_; lean_object* v___x_132_; lean_object* v___x_133_; 
v___x_131_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__5, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__5_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__5);
v___x_132_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__3, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__3);
v___x_133_ = l_Rat_mul(v___x_132_, v___x_131_);
return v___x_133_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__4(void){
_start:
{
lean_object* v___x_134_; lean_object* v___x_135_; lean_object* v___x_136_; 
v___x_134_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod1___closed__3, &lp_lean__proofs_MachineMarkets_k1__mod1___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__3);
v___x_135_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod1___closed__2, &lp_lean__proofs_MachineMarkets_k1__mod1___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__2);
v___x_136_ = l_Rat_add(v___x_135_, v___x_134_);
return v___x_136_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k1__mod1(void){
_start:
{
lean_object* v___x_137_; 
v___x_137_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod1___closed__4, &lp_lean__proofs_MachineMarkets_k1__mod1___closed__4_once, _init_lp_lean__proofs_MachineMarkets_k1__mod1___closed__4);
return v___x_137_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__0(void){
_start:
{
lean_object* v___x_138_; lean_object* v___x_139_; lean_object* v___x_140_; 
v___x_138_ = lean_unsigned_to_nat(2u);
v___x_139_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__0);
v___x_140_ = l_Rat_pow(v___x_139_, v___x_138_);
return v___x_140_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__1(void){
_start:
{
lean_object* v___x_141_; lean_object* v___x_142_; lean_object* v___x_143_; 
v___x_141_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__0);
v___x_142_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__0);
v___x_143_ = l_Rat_mul(v___x_142_, v___x_141_);
return v___x_143_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__2(void){
_start:
{
lean_object* v___x_144_; lean_object* v___x_145_; lean_object* v___x_146_; 
v___x_144_ = lean_unsigned_to_nat(2u);
v___x_145_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__2, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__2);
v___x_146_ = l_Rat_pow(v___x_145_, v___x_144_);
return v___x_146_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__3(void){
_start:
{
lean_object* v___x_147_; lean_object* v___x_148_; lean_object* v___x_149_; 
v___x_147_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__2, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__2);
v___x_148_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__1, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__1);
v___x_149_ = l_Rat_mul(v___x_148_, v___x_147_);
return v___x_149_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__4(void){
_start:
{
lean_object* v___x_150_; lean_object* v___x_151_; lean_object* v___x_152_; 
v___x_150_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__3, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__3);
v___x_151_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__1, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__1);
v___x_152_ = l_Rat_add(v___x_151_, v___x_150_);
return v___x_152_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__5(void){
_start:
{
lean_object* v___x_153_; lean_object* v___x_154_; lean_object* v___x_155_; 
v___x_153_ = lean_unsigned_to_nat(2u);
v___x_154_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k1__mod0___closed__5, &lp_lean__proofs_MachineMarkets_k1__mod0___closed__5_once, _init_lp_lean__proofs_MachineMarkets_k1__mod0___closed__5);
v___x_155_ = l_Rat_pow(v___x_154_, v___x_153_);
return v___x_155_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__6(void){
_start:
{
lean_object* v___x_156_; lean_object* v___x_157_; lean_object* v___x_158_; 
v___x_156_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__5, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__5_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__5);
v___x_157_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod0___closed__3, &lp_lean__proofs_MachineMarkets_k0__mod0___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k0__mod0___closed__3);
v___x_158_ = l_Rat_mul(v___x_157_, v___x_156_);
return v___x_158_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__7(void){
_start:
{
lean_object* v___x_159_; lean_object* v___x_160_; lean_object* v___x_161_; 
v___x_159_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__6, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__6_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__6);
v___x_160_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__4, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__4_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__4);
v___x_161_ = l_Rat_add(v___x_160_, v___x_159_);
return v___x_161_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod0(void){
_start:
{
lean_object* v___x_162_; 
v___x_162_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__7, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__7_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__7);
return v___x_162_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__0(void){
_start:
{
lean_object* v___x_163_; lean_object* v___x_164_; lean_object* v___x_165_; 
v___x_163_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__0, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__0);
v___x_164_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__0, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__0);
v___x_165_ = l_Rat_mul(v___x_164_, v___x_163_);
return v___x_165_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__1(void){
_start:
{
lean_object* v___x_166_; lean_object* v___x_167_; lean_object* v___x_168_; 
v___x_166_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__2, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__2);
v___x_167_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__1, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__1);
v___x_168_ = l_Rat_mul(v___x_167_, v___x_166_);
return v___x_168_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__2(void){
_start:
{
lean_object* v___x_169_; lean_object* v___x_170_; lean_object* v___x_171_; 
v___x_169_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod1___closed__1, &lp_lean__proofs_MachineMarkets_k2__mod1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__1);
v___x_170_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod1___closed__0, &lp_lean__proofs_MachineMarkets_k2__mod1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__0);
v___x_171_ = l_Rat_add(v___x_170_, v___x_169_);
return v___x_171_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__3(void){
_start:
{
lean_object* v___x_172_; lean_object* v___x_173_; lean_object* v___x_174_; 
v___x_172_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod0___closed__5, &lp_lean__proofs_MachineMarkets_k2__mod0___closed__5_once, _init_lp_lean__proofs_MachineMarkets_k2__mod0___closed__5);
v___x_173_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k0__mod1___closed__3, &lp_lean__proofs_MachineMarkets_k0__mod1___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k0__mod1___closed__3);
v___x_174_ = l_Rat_mul(v___x_173_, v___x_172_);
return v___x_174_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__4(void){
_start:
{
lean_object* v___x_175_; lean_object* v___x_176_; lean_object* v___x_177_; 
v___x_175_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod1___closed__3, &lp_lean__proofs_MachineMarkets_k2__mod1___closed__3_once, _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__3);
v___x_176_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod1___closed__2, &lp_lean__proofs_MachineMarkets_k2__mod1___closed__2_once, _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__2);
v___x_177_ = l_Rat_add(v___x_176_, v___x_175_);
return v___x_177_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_k2__mod1(void){
_start:
{
lean_object* v___x_178_; 
v___x_178_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_k2__mod1___closed__4, &lp_lean__proofs_MachineMarkets_k2__mod1___closed__4_once, _init_lp_lean__proofs_MachineMarkets_k2__mod1___closed__4);
return v___x_178_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h0(void){
_start:
{
lean_object* v___x_179_; 
v___x_179_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_eta__1___closed__0, &lp_lean__proofs_MachineMarkets_eta__1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_eta__1___closed__0);
return v___x_179_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h1(void){
_start:
{
lean_object* v___x_180_; 
v___x_180_ = lp_lean__proofs_MachineMarkets_a__market;
return v___x_180_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h2___closed__0(void){
_start:
{
lean_object* v___x_181_; lean_object* v___x_182_; 
v___x_181_ = lp_lean__proofs_MachineMarkets_a__market;
v___x_182_ = l_Rat_mul(v___x_181_, v___x_181_);
return v___x_182_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h2___closed__1(void){
_start:
{
lean_object* v___x_183_; lean_object* v___x_184_; lean_object* v___x_185_; 
v___x_183_ = lp_lean__proofs_MachineMarkets_h0;
v___x_184_ = lp_lean__proofs_MachineMarkets_k0__mod0;
v___x_185_ = l_Rat_mul(v___x_184_, v___x_183_);
return v___x_185_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h2___closed__2(void){
_start:
{
lean_object* v___x_186_; lean_object* v___x_187_; lean_object* v___x_188_; 
v___x_186_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h2___closed__1, &lp_lean__proofs_MachineMarkets_h2___closed__1_once, _init_lp_lean__proofs_MachineMarkets_h2___closed__1);
v___x_187_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h2___closed__0, &lp_lean__proofs_MachineMarkets_h2___closed__0_once, _init_lp_lean__proofs_MachineMarkets_h2___closed__0);
v___x_188_ = l_Rat_add(v___x_187_, v___x_186_);
return v___x_188_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h2(void){
_start:
{
lean_object* v___x_189_; 
v___x_189_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h2___closed__2, &lp_lean__proofs_MachineMarkets_h2___closed__2_once, _init_lp_lean__proofs_MachineMarkets_h2___closed__2);
return v___x_189_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h3___closed__0(void){
_start:
{
lean_object* v___x_190_; lean_object* v___x_191_; lean_object* v___x_192_; 
v___x_190_ = lp_lean__proofs_MachineMarkets_h2;
v___x_191_ = lp_lean__proofs_MachineMarkets_a__market;
v___x_192_ = l_Rat_mul(v___x_191_, v___x_190_);
return v___x_192_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h3___closed__1(void){
_start:
{
lean_object* v___x_193_; lean_object* v___x_194_; lean_object* v___x_195_; 
v___x_193_ = lp_lean__proofs_MachineMarkets_a__market;
v___x_194_ = lp_lean__proofs_MachineMarkets_k0__mod0;
v___x_195_ = l_Rat_mul(v___x_194_, v___x_193_);
return v___x_195_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h3___closed__2(void){
_start:
{
lean_object* v___x_196_; lean_object* v___x_197_; lean_object* v___x_198_; 
v___x_196_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h3___closed__1, &lp_lean__proofs_MachineMarkets_h3___closed__1_once, _init_lp_lean__proofs_MachineMarkets_h3___closed__1);
v___x_197_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h3___closed__0, &lp_lean__proofs_MachineMarkets_h3___closed__0_once, _init_lp_lean__proofs_MachineMarkets_h3___closed__0);
v___x_198_ = l_Rat_add(v___x_197_, v___x_196_);
return v___x_198_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h3___closed__3(void){
_start:
{
lean_object* v___x_199_; lean_object* v___x_200_; lean_object* v___x_201_; 
v___x_199_ = lp_lean__proofs_MachineMarkets_h0;
v___x_200_ = lp_lean__proofs_MachineMarkets_k1__mod0;
v___x_201_ = l_Rat_mul(v___x_200_, v___x_199_);
return v___x_201_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h3___closed__4(void){
_start:
{
lean_object* v___x_202_; lean_object* v___x_203_; lean_object* v___x_204_; 
v___x_202_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h3___closed__3, &lp_lean__proofs_MachineMarkets_h3___closed__3_once, _init_lp_lean__proofs_MachineMarkets_h3___closed__3);
v___x_203_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h3___closed__2, &lp_lean__proofs_MachineMarkets_h3___closed__2_once, _init_lp_lean__proofs_MachineMarkets_h3___closed__2);
v___x_204_ = l_Rat_add(v___x_203_, v___x_202_);
return v___x_204_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h3(void){
_start:
{
lean_object* v___x_205_; 
v___x_205_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h3___closed__4, &lp_lean__proofs_MachineMarkets_h3___closed__4_once, _init_lp_lean__proofs_MachineMarkets_h3___closed__4);
return v___x_205_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__0(void){
_start:
{
lean_object* v___x_206_; lean_object* v___x_207_; lean_object* v___x_208_; 
v___x_206_ = lp_lean__proofs_MachineMarkets_h3;
v___x_207_ = lp_lean__proofs_MachineMarkets_a__market;
v___x_208_ = l_Rat_mul(v___x_207_, v___x_206_);
return v___x_208_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__1(void){
_start:
{
lean_object* v___x_209_; lean_object* v___x_210_; lean_object* v___x_211_; 
v___x_209_ = lp_lean__proofs_MachineMarkets_h2;
v___x_210_ = lp_lean__proofs_MachineMarkets_k0__mod0;
v___x_211_ = l_Rat_mul(v___x_210_, v___x_209_);
return v___x_211_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__2(void){
_start:
{
lean_object* v___x_212_; lean_object* v___x_213_; lean_object* v___x_214_; 
v___x_212_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__1, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__1_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__1);
v___x_213_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__0, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__0);
v___x_214_ = l_Rat_add(v___x_213_, v___x_212_);
return v___x_214_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__3(void){
_start:
{
lean_object* v___x_215_; lean_object* v___x_216_; lean_object* v___x_217_; 
v___x_215_ = lp_lean__proofs_MachineMarkets_a__market;
v___x_216_ = lp_lean__proofs_MachineMarkets_k1__mod0;
v___x_217_ = l_Rat_mul(v___x_216_, v___x_215_);
return v___x_217_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__4(void){
_start:
{
lean_object* v___x_218_; lean_object* v___x_219_; lean_object* v___x_220_; 
v___x_218_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__3, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__3_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__3);
v___x_219_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__2, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__2_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__2);
v___x_220_ = l_Rat_add(v___x_219_, v___x_218_);
return v___x_220_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__5(void){
_start:
{
lean_object* v___x_221_; lean_object* v___x_222_; lean_object* v___x_223_; 
v___x_221_ = lp_lean__proofs_MachineMarkets_h0;
v___x_222_ = lp_lean__proofs_MachineMarkets_k2__mod0;
v___x_223_ = l_Rat_mul(v___x_222_, v___x_221_);
return v___x_223_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__6(void){
_start:
{
lean_object* v___x_224_; lean_object* v___x_225_; lean_object* v___x_226_; 
v___x_224_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__5, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__5_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__5);
v___x_225_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__4, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__4_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__4);
v___x_226_ = l_Rat_add(v___x_225_, v___x_224_);
return v___x_226_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod0(void){
_start:
{
lean_object* v___x_227_; 
v___x_227_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__6, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__6_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__6);
return v___x_227_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__0(void){
_start:
{
lean_object* v___x_228_; lean_object* v___x_229_; lean_object* v___x_230_; 
v___x_228_ = lp_lean__proofs_MachineMarkets_h2;
v___x_229_ = lp_lean__proofs_MachineMarkets_k0__mod1;
v___x_230_ = l_Rat_mul(v___x_229_, v___x_228_);
return v___x_230_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__1(void){
_start:
{
lean_object* v___x_231_; lean_object* v___x_232_; lean_object* v___x_233_; 
v___x_231_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod1___closed__0, &lp_lean__proofs_MachineMarkets_h4__mod1___closed__0_once, _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__0);
v___x_232_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod0___closed__0, &lp_lean__proofs_MachineMarkets_h4__mod0___closed__0_once, _init_lp_lean__proofs_MachineMarkets_h4__mod0___closed__0);
v___x_233_ = l_Rat_add(v___x_232_, v___x_231_);
return v___x_233_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__2(void){
_start:
{
lean_object* v___x_234_; lean_object* v___x_235_; lean_object* v___x_236_; 
v___x_234_ = lp_lean__proofs_MachineMarkets_a__market;
v___x_235_ = lp_lean__proofs_MachineMarkets_k1__mod1;
v___x_236_ = l_Rat_mul(v___x_235_, v___x_234_);
return v___x_236_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__3(void){
_start:
{
lean_object* v___x_237_; lean_object* v___x_238_; lean_object* v___x_239_; 
v___x_237_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod1___closed__2, &lp_lean__proofs_MachineMarkets_h4__mod1___closed__2_once, _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__2);
v___x_238_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod1___closed__1, &lp_lean__proofs_MachineMarkets_h4__mod1___closed__1_once, _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__1);
v___x_239_ = l_Rat_add(v___x_238_, v___x_237_);
return v___x_239_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__4(void){
_start:
{
lean_object* v___x_240_; lean_object* v___x_241_; lean_object* v___x_242_; 
v___x_240_ = lp_lean__proofs_MachineMarkets_h0;
v___x_241_ = lp_lean__proofs_MachineMarkets_k2__mod1;
v___x_242_ = l_Rat_mul(v___x_241_, v___x_240_);
return v___x_242_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__5(void){
_start:
{
lean_object* v___x_243_; lean_object* v___x_244_; lean_object* v___x_245_; 
v___x_243_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod1___closed__4, &lp_lean__proofs_MachineMarkets_h4__mod1___closed__4_once, _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__4);
v___x_244_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod1___closed__3, &lp_lean__proofs_MachineMarkets_h4__mod1___closed__3_once, _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__3);
v___x_245_ = l_Rat_add(v___x_244_, v___x_243_);
return v___x_245_;
}
}
static lean_object* _init_lp_lean__proofs_MachineMarkets_h4__mod1(void){
_start:
{
lean_object* v___x_246_; 
v___x_246_ = lean_obj_once(&lp_lean__proofs_MachineMarkets_h4__mod1___closed__5, &lp_lean__proofs_MachineMarkets_h4__mod1___closed__5_once, _init_lp_lean__proofs_MachineMarkets_h4__mod1___closed__5);
return v___x_246_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init_GrindInstances_Ring_Rat(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_lean__proofs_Proofs_Ambiguity(uint8_t builtin) {
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
lp_lean__proofs_MachineMarkets_q0__1 = _init_lp_lean__proofs_MachineMarkets_q0__1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_q0__1);
lp_lean__proofs_MachineMarkets_q0__2 = _init_lp_lean__proofs_MachineMarkets_q0__2();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_q0__2);
lp_lean__proofs_MachineMarkets_q0__3 = _init_lp_lean__proofs_MachineMarkets_q0__3();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_q0__3);
lp_lean__proofs_MachineMarkets_q1__1 = _init_lp_lean__proofs_MachineMarkets_q1__1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_q1__1);
lp_lean__proofs_MachineMarkets_q1__2 = _init_lp_lean__proofs_MachineMarkets_q1__2();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_q1__2);
lp_lean__proofs_MachineMarkets_q1__3 = _init_lp_lean__proofs_MachineMarkets_q1__3();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_q1__3);
lp_lean__proofs_MachineMarkets_eta__1 = _init_lp_lean__proofs_MachineMarkets_eta__1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_eta__1);
lp_lean__proofs_MachineMarkets_eta__2 = _init_lp_lean__proofs_MachineMarkets_eta__2();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_eta__2);
lp_lean__proofs_MachineMarkets_eta__3 = _init_lp_lean__proofs_MachineMarkets_eta__3();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_eta__3);
lp_lean__proofs_MachineMarkets_a__market = _init_lp_lean__proofs_MachineMarkets_a__market();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_a__market);
lp_lean__proofs_MachineMarkets_Q0 = _init_lp_lean__proofs_MachineMarkets_Q0();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_Q0);
lp_lean__proofs_MachineMarkets_Q1 = _init_lp_lean__proofs_MachineMarkets_Q1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_Q1);
lp_lean__proofs_MachineMarkets_k0__mod0 = _init_lp_lean__proofs_MachineMarkets_k0__mod0();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_k0__mod0);
lp_lean__proofs_MachineMarkets_k0__mod1 = _init_lp_lean__proofs_MachineMarkets_k0__mod1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_k0__mod1);
lp_lean__proofs_MachineMarkets_k1__mod0 = _init_lp_lean__proofs_MachineMarkets_k1__mod0();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_k1__mod0);
lp_lean__proofs_MachineMarkets_k1__mod1 = _init_lp_lean__proofs_MachineMarkets_k1__mod1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_k1__mod1);
lp_lean__proofs_MachineMarkets_k2__mod0 = _init_lp_lean__proofs_MachineMarkets_k2__mod0();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_k2__mod0);
lp_lean__proofs_MachineMarkets_k2__mod1 = _init_lp_lean__proofs_MachineMarkets_k2__mod1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_k2__mod1);
lp_lean__proofs_MachineMarkets_h0 = _init_lp_lean__proofs_MachineMarkets_h0();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_h0);
lp_lean__proofs_MachineMarkets_h1 = _init_lp_lean__proofs_MachineMarkets_h1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_h1);
lp_lean__proofs_MachineMarkets_h2 = _init_lp_lean__proofs_MachineMarkets_h2();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_h2);
lp_lean__proofs_MachineMarkets_h3 = _init_lp_lean__proofs_MachineMarkets_h3();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_h3);
lp_lean__proofs_MachineMarkets_h4__mod0 = _init_lp_lean__proofs_MachineMarkets_h4__mod0();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_h4__mod0);
lp_lean__proofs_MachineMarkets_h4__mod1 = _init_lp_lean__proofs_MachineMarkets_h4__mod1();
lean_mark_persistent(lp_lean__proofs_MachineMarkets_h4__mod1);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
