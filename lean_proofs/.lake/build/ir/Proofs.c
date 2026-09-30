// Lean compiler output
// Module: Proofs
// Imports: public import Init public meta import Init public import Proofs.Stability public import Proofs.PBHDefect public import Proofs.Ambiguity public import Proofs.Bounds
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
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_lean__proofs_Proofs_Stability(uint8_t builtin);
lean_object* initialize_lean__proofs_Proofs_PBHDefect(uint8_t builtin);
lean_object* initialize_lean__proofs_Proofs_Ambiguity(uint8_t builtin);
lean_object* initialize_lean__proofs_Proofs_Bounds(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_lean__proofs_Proofs(uint8_t builtin) {
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
res = initialize_lean__proofs_Proofs_Stability(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_lean__proofs_Proofs_PBHDefect(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_lean__proofs_Proofs_Ambiguity(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_lean__proofs_Proofs_Bounds(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
