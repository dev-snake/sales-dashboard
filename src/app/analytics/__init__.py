"""Pure analytics transforms (DataFrame in → DataFrame/metrics out)."""

from app.analytics.abc import abc_classify, pareto_products_for_share
from app.analytics.cohort import build_cohort_matrix, cohort_pivot
from app.analytics.descriptive import describe_numeric, margin_pct, safe_div
from app.analytics.rfm import compute_rfm_raw, score_rfm, segment_summary
from app.analytics.trends import add_mom_change, monthly_aggregate, rolling_mean

__all__ = [
    "abc_classify",
    "add_mom_change",
    "build_cohort_matrix",
    "cohort_pivot",
    "compute_rfm_raw",
    "describe_numeric",
    "margin_pct",
    "monthly_aggregate",
    "pareto_products_for_share",
    "rolling_mean",
    "safe_div",
    "score_rfm",
    "segment_summary",
]
