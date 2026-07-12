"""ETL package: extract → validate → clean → transform → load.

Import submodules directly to avoid circular imports with schemas:
``from app.etl.pipeline import EtlPipeline``
"""

__all__ = ["EtlPipeline", "EtlResult"]


def __getattr__(name: str) -> object:
    if name == "EtlPipeline":
        from app.etl.pipeline import EtlPipeline

        return EtlPipeline
    if name == "EtlResult":
        from app.etl.result import EtlResult

        return EtlResult
    raise AttributeError(name)
