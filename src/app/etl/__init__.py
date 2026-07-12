"""ETL package: extract → validate → clean → transform → load."""

from app.etl.pipeline import EtlPipeline
from app.etl.result import EtlResult

__all__ = ["EtlPipeline", "EtlResult"]
