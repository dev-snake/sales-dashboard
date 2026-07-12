"""Report generation service — collect + export Excel/PDF."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session

from app.config import get_settings
from app.reports.collector import collect_report
from app.reports.excel.workbook_builder import build_excel
from app.reports.package import ReportDataPackage
from app.reports.pdf.pdf_builder import build_pdf
from app.reports.periods import ReportType, parse_report_type, resolve_period


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()

    def collect(
        self,
        report_type: str | ReportType,
        *,
        as_of: date | None = None,
        store_ids: list[int] | None = None,
    ) -> ReportDataPackage:
        rt = parse_report_type(str(report_type))
        period = resolve_period(rt, as_of)
        logger.info("Collecting report | type={} period={}", rt, period.label)
        return collect_report(self.session, period, store_ids=store_ids)

    def export(
        self,
        package: ReportDataPackage,
        *,
        fmt: str = "both",
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Write excel and/or pdf under output/reports/."""
        root = output_dir or (self.settings.project_root / "output" / "reports")
        excel_dir = root / "excel"
        pdf_dir = root / "pdf"
        stem = f"{package.report_type}_{package.period.label.replace('/', '-')}"
        written: dict[str, Path] = {}

        fmt_l = fmt.lower()
        if fmt_l in {"excel", "both", "xlsx"}:
            path = build_excel(package, excel_dir / f"{stem}.xlsx")
            written["excel"] = path
            logger.info("Excel report written | {}", path)
        if fmt_l in {"pdf", "both"}:
            path = build_pdf(package, pdf_dir / f"{stem}.pdf")
            written["pdf"] = path
            logger.info("PDF report written | {}", path)
        if not written:
            raise ValueError(f"Unknown format {fmt!r}; use excel|pdf|both")
        return written

    def generate(
        self,
        report_type: str,
        *,
        as_of: date | None = None,
        fmt: str = "both",
        store_ids: list[int] | None = None,
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        package = self.collect(report_type, as_of=as_of, store_ids=store_ids)
        return self.export(package, fmt=fmt, output_dir=output_dir)
