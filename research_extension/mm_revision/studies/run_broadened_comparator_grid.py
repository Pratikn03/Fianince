"""Corrective 120-cell comparator grid; historical JSON is read-only evidence.

The prior grid included x0 instead of starting at x1. A rerun after repair is
post-hoc, not a preregistered confirmation. Five panels per cell is the saved
historical denominator (600 total), despite the old docstring claiming ten.
"""
from pathlib import Path
from research_extension.evidence_repair.statistical_repair import run_grid


def run_broadened_comparator_study(replications_per_cell=5, seed_base=20260924,
                                  output_dir=None, workers=1):
    if output_dir is None:
        raise ValueError('A new output directory is required; historical results are immutable')
    return run_grid(Path(output_dir), replications=replications_per_cell,
                    seed_base=seed_base, workers=workers)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    run_broadened_comparator_study(output_dir=args.output_dir, workers=args.workers)
