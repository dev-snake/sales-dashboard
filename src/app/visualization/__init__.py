"""Chart factories — Plotly (interactive) + Matplotlib (static/PDF).

No database access in this package.
"""

from app.visualization.matplotlib_charts import (
    fig_to_png_bytes,
    mpl_bar,
    mpl_barh,
    mpl_histogram,
    mpl_line,
    mpl_pie,
    save_fig,
)
from app.visualization.plotly_charts import (
    create_area_chart,
    create_bar_chart,
    create_dual_line_chart,
    create_heatmap,
    create_histogram,
    create_line_chart,
    create_pie_chart,
    create_scatter_chart,
    create_treemap,
)
from app.visualization.styles import (
    CATEGORICAL,
    PRIMARY,
    format_money,
    format_number,
    format_percent,
)

__all__ = [
    "CATEGORICAL",
    "PRIMARY",
    "create_area_chart",
    "create_bar_chart",
    "create_dual_line_chart",
    "create_heatmap",
    "create_histogram",
    "create_line_chart",
    "create_pie_chart",
    "create_scatter_chart",
    "create_treemap",
    "fig_to_png_bytes",
    "format_money",
    "format_number",
    "format_percent",
    "mpl_bar",
    "mpl_barh",
    "mpl_histogram",
    "mpl_line",
    "mpl_pie",
    "save_fig",
]
