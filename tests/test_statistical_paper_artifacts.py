"""Paper rendering binds to raw corrective observations, not hand-copied rates."""
import importlib
import importlib.util
import copy
import pytest


def renderer():
    name = 'research_extension.evidence_repair.render_statistical_artifacts'
    assert importlib.util.find_spec(name), 'statistical paper renderer missing'
    return importlib.import_module(name)


@pytest.fixture(scope='module')
def evidence(tmp_path_factory):
    from research_extension.evidence_repair.statistical_repair import run_grid, calibrate_response_pivots
    from research_extension.mm_revision.studies.conic_informativeness_curve import run_conic_informativeness_study
    from research_extension.mm_revision.studies.output_error_misspecification_diagnostic import run_output_error_diagnostic
    grid = run_grid(tmp_path_factory.mktemp('render')/'grid', cells=[(.82,.5,12,4.,4)], replications=1)
    return dict(grid=grid, calibration=calibrate_response_pivots(trials=400,p=3,R=12),
        diagnostic=run_output_error_diagnostic(n_panels=2,H=6),
        **{f'sweep_{mode}': run_conic_informativeness_study(budgets=[16,32],
            n_replications=1,H=4,covariance_mode=mode) for mode in ('known','estimated')})


def test_paper_fragments_report_unverified_and_exact_denominators(evidence):
    out = renderer().render(evidence)
    assert 'post-hoc' in out['section_tex']
    assert 'withheld' in out['section_tex']
    assert '1 independent panels' in out['section_tex']
    assert 'C1/C3 are single deterministic cases' in out['section_tex']
    assert 'tab:comparator_comparison' in out['section_tex']
    assert 'fig:conic_contraction' in out['section_tex']
    assert out['denominators']['diagnostic_attempts'] == 6
    assert out['denominators']['grid_panels'] == 1
    assert '\t' not in out['section_tex']
    assert r'p{.25\textwidth}' in out['section_tex']
    assert 'cut-limit stop' in out['section_tex']
    assert 'not a converged second-order-cone optimum' in out['section_tex']


def test_renderer_rejects_summary_drift(evidence):
    bad = copy.deepcopy(evidence)
    bad['grid']['summary']['conic_certificate']['metrics']['coverage_rate'] = -1
    with pytest.raises(AssertionError, match='summary'):
        renderer().render(bad)


def test_renderer_rejects_changed_source_run(evidence):
    bad = copy.deepcopy(evidence)
    bad['grid']['status'] = 'source_changed_during_run'
    with pytest.raises(AssertionError, match='complete'):
        renderer().render(bad)


def test_funded_figure_uses_actual_effective_dynamics_and_contrast():
    from research_extension.mm_revision.studies.funded_stress import run_paired_mechanism_controls
    data=run_paired_mechanism_controls(n_replicates=2)
    text=renderer().render_funded(data)
    assert '1.07409' in text
    assert 'tab:funded_controls' in text
    value=data['paired_contrasts']['adaptive_minus_zero_feedback']['dislocation_diff_mean']
    assert f'{value:.5f}' in text
    assert 'not a permanent trading ban' in text
