"""PDF executive report (reportlab + matplotlib charts)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.reports.package import ReportDataPackage
from app.visualization.matplotlib_charts import fig_to_png_bytes, mpl_barh, mpl_line
from app.visualization.styles import format_money, format_number, format_percent


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleVN",
            parent=base["Title"],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "h2": ParagraphStyle(
            "H2VN",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=12,
            spaceAfter=8,
        ),
        "body": ParagraphStyle(
            "BodyVN",
            parent=base["Normal"],
            fontSize=10,
            alignment=TA_LEFT,
            leading=14,
        ),
        "small": ParagraphStyle(
            "SmallVN",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.grey,
        ),
    }


def _kpi_table(package: ReportDataPackage) -> Table:
    kpi = package.kpi
    prev = package.kpi_previous
    data = [
        ["Metric", "Current", "Previous", "Δ %"],
        [
            "Revenue",
            format_money(kpi.revenue),
            format_money(prev.revenue),
            _fmt_delta(package.kpi_delta_pct("revenue")),
        ],
        [
            "Gross Profit",
            format_money(kpi.gross_profit),
            format_money(prev.gross_profit),
            _fmt_delta(package.kpi_delta_pct("gross_profit")),
        ],
        [
            "Gross Margin",
            format_percent(kpi.gross_margin_pct),
            format_percent(prev.gross_margin_pct),
            _fmt_delta(package.kpi_delta_pct("gross_margin_pct")),
        ],
        [
            "Orders",
            format_number(kpi.order_count),
            format_number(prev.order_count),
            _fmt_delta(package.kpi_delta_pct("order_count")),
        ],
        [
            "AOV",
            format_money(kpi.aov),
            format_money(prev.aov),
            _fmt_delta(package.kpi_delta_pct("aov")),
        ],
        [
            "Buyers",
            format_number(kpi.buyer_count),
            format_number(prev.buyer_count),
            _fmt_delta(package.kpi_delta_pct("buyer_count")),
        ],
    ]
    t = Table(data, colWidths=[3.5 * cm, 4 * cm, 4 * cm, 2.5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _fmt_delta(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{v:+.1f}%"


def _df_table(df: pd.DataFrame, columns: list[str], max_rows: int = 10) -> Table | Paragraph:
    if df is None or df.empty:
        return Paragraph("(no data)", _styles()["body"])
    cols = [c for c in columns if c in df.columns]
    if not cols:
        cols = list(df.columns)[:5]
    head = cols
    body = df[cols].head(max_rows).astype(str).values.tolist()
    data = [head, *body]
    t = Table(data, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D9488")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    return t


def _chart_image_from_trend(package: ReportDataPackage) -> Image | None:
    trend = package.trend
    if trend is None or trend.empty:
        return None
    x_col = "period_key" if "period_key" in trend.columns else trend.columns[0]
    y_col = "revenue" if "revenue" in trend.columns else trend.columns[1]
    fig = mpl_line(trend, x_col, y_col, title="Revenue trend", figsize=(7.5, 3.2))
    png = fig_to_png_bytes(fig, dpi=130)
    return Image(BytesIO(png), width=16 * cm, height=7 * cm)


def _chart_image_top_products(package: ReportDataPackage) -> Image | None:
    df = package.top_products
    if df is None or df.empty:
        return None
    plot_df = df.head(10).copy()
    if "sku" in plot_df.columns:
        plot_df["label"] = plot_df["sku"].astype(str)
    else:
        plot_df["label"] = plot_df.iloc[:, 0].astype(str)
    y_col = "revenue" if "revenue" in plot_df.columns else plot_df.columns[1]
    fig = mpl_barh(plot_df, "label", y_col, title="Top products", figsize=(7.5, 4))
    png = fig_to_png_bytes(fig, dpi=130)
    return Image(BytesIO(png), width=16 * cm, height=8 * cm)


def build_pdf(package: ReportDataPackage, path: Path) -> Path:
    """Write executive PDF; return path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    styles = _styles()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=package.title,
    )
    story: list = []

    story.append(Paragraph(package.title, styles["title"]))
    story.append(
        Paragraph(
            f"Period: {package.period.start} → {package.period.end} "
            f"(as of {package.period.as_of}) · Generated {package.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
            styles["small"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("1. Executive KPI summary", styles["h2"]))
    story.append(_kpi_table(package))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            f"Repeat customer rate: "
            f"{format_percent(package.repeat_rate.get('repeat_customer_rate_pct', 0))} "
            f"({package.repeat_rate.get('repeat_buyers', 0)} / "
            f"{package.repeat_rate.get('total_buyers', 0)} buyers)",
            styles["body"],
        )
    )

    story.append(Paragraph("2. Revenue trend", styles["h2"]))
    img = _chart_image_from_trend(package)
    if img:
        story.append(img)
    else:
        story.append(Paragraph("No trend data for this period.", styles["body"]))

    story.append(PageBreak())
    story.append(Paragraph("3. Rankings", styles["h2"]))
    img2 = _chart_image_top_products(package)
    if img2:
        story.append(img2)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Top products", styles["body"]))
    story.append(
        _df_table(
            package.top_products,
            ["sku", "product_name", "revenue", "units", "profit"],
            max_rows=12,
        )
    )
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Top stores", styles["body"]))
    story.append(_df_table(package.top_stores, ["store_code", "revenue", "orders", "units"], 10))

    if package.report_type in ("monthly", "quarterly", "yearly"):
        story.append(PageBreak())
        story.append(Paragraph("4. Customer analytics (RFM)", styles["h2"]))
        story.append(
            _df_table(
                package.rfm_summary, ["segment", "customers", "monetary", "avg_frequency"], 12
            )
        )
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph("5. ABC products (head)", styles["h2"]))
        story.append(
            _df_table(package.abc, ["sku", "product_name", "revenue", "cum_pct", "abc_class"], 15)
        )

    story.append(PageBreak())
    story.append(Paragraph("Appendix — Metric definitions", styles["h2"]))
    defs = [
        "Revenue = SUM(line_total) for order status paid/completed.",
        "COGS = SUM(quantity × unit_cost).",
        "Gross Profit = Revenue − COGS; Margin % = Profit / Revenue × 100.",
        "AOV = Revenue / distinct order count.",
        "RFM = Recency / Frequency / Monetary customer segments.",
        "ABC = Pareto classes on cumulative product revenue (A ≤ 80%, B ≤ 95%).",
        "This report is generated from synthetic/demo data for portfolio learning.",
    ]
    for d in defs:
        story.append(Paragraph(f"• {d}", styles["body"]))
        story.append(Spacer(1, 0.15 * cm))

    doc.build(story)
    return path
