"""ETL service orchestration for CLI."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session

from app.etl.manifest import Manifest, default_samples_manifest, load_manifest
from app.etl.pipeline import EtlPipeline
from app.etl.result import EtlResult
from app.etl.transformers.lookups import ensure_sample_masters
from app.utils.errors import ETLError


class EtlService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def run_entity(
        self,
        entity: str,
        path: Path,
        *,
        strict: bool | None = None,
        ensure_masters: bool = False,
    ) -> EtlResult:
        pipeline = EtlPipeline(
            self.session,
            strict=strict,
            ensure_masters=ensure_masters,
        )
        return pipeline.run(entity, path)

    def run_manifest(
        self,
        manifest: Manifest | Path | str | None = None,
        *,
        strict: bool | None = None,
        use_samples: bool = False,
    ) -> list[EtlResult]:
        if use_samples or manifest is None:
            mf = default_samples_manifest()
        elif isinstance(manifest, Manifest):
            mf = manifest
        else:
            mf = load_manifest(Path(manifest))

        if mf.ensure_sample_masters:
            ensure_sample_masters(self.session)

        results: list[EtlResult] = []
        for job in mf.jobs:
            logger.info("Manifest job | entity={} path={}", job.entity, job.path)
            if not job.path.is_file():
                raise ETLError(f"Manifest path missing: {job.path}")
            pipeline = EtlPipeline(
                self.session,
                strict=strict,
                ensure_masters=False,
            )
            results.append(pipeline.run(job.entity, job.path))
        return results
