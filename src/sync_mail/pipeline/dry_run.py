import pymysql
import logging
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional
from sync_mail.config.schema import MappingDocument
from sync_mail.db.target_probe import describe_target_columns, ColumnMetadata
from sync_mail.pipeline.extractor import extract
from sync_mail.pipeline.transformer import transform_row
from sync_mail.pipeline.anomaly import Anomaly, AnomalyCategory, AnomalySeverity
from sync_mail.pipeline.dry_run_report import DryRunReport
from sync_mail.observability import event_bus, Event, EventType, logger
from sync_mail.errors import BatchFailedError

class DryRunEngine:
    def __init__(
        self, 
        conn_source: pymysql.connections.Connection,
        conn_target: pymysql.connections.Connection,
        target_schema: str,
        mapping: MappingDocument,
        sample_limit: int = 100,
        source_host: str = "",
        source_db: str = "",
        target_host: str = "",
        target_db: str = "",
        mapping_path: str = ""
    ):
        self.conn_source = conn_source
        self.conn_target = conn_target
        self.target_schema = target_schema
        self.mapping = mapping
        self.sample_limit = sample_limit
        job_name = getattr(mapping, "job_name", f"{mapping.source_table} -> {mapping.target_table}")
        self.report = DryRunReport(
            job_name=job_name,
            source_table=mapping.source_table,
            target_table=mapping.target_table,
            sample_limit=sample_limit,
            source_host=source_host,
            source_db=source_db,
            target_host=target_host,
            target_db=target_db,
            mapping_path=mapping_path
        )
        self._should_stop = False

    def execute(self) -> DryRunReport:
        logger.info(f"Starting dry run for job '{self.report.job_name}'")
        self.report.start_time = datetime.now()
        
        event_bus.publish(Event(
            EventType.DRY_RUN_STARTED,
            {
                "job_name": self.report.job_name, 
                "sample_limit": self.sample_limit,
                "source_host": self.report.source_host,
                "source_db": self.report.source_db,
                "target_host": self.report.target_host,
                "target_db": self.report.target_db,
                "mapping_path": self.report.mapping_path
            }
        ))
        
        # 1. Probe Target Metadata
        try:
            target_metadata = describe_target_columns(
                self.conn_target, self.target_schema, self.mapping.target_table
            )
        except Exception as e:
            logger.error(f"Failed to probe target metadata: {e}")
            event_bus.publish(Event(
                EventType.JOB_ABORTED,
                {"job_name": self.report.job_name, "error": str(e), "context": "Target Probing"}
            ))
            raise

        # 2. Cross-mapping checks (once)
        self._check_missing_columns(target_metadata)
        
        # 3. Sample Extract & Transform
        current_time = datetime.now(UTC).replace(tzinfo=None)
        
        try:
            extraction_gen = extract(
                self.conn_source, 
                self.mapping, 
                last_pk=0, # Always start from beginning for dry run
                limit_override=self.sample_limit
            )
            
            rows_processed = 0
            for batch in extraction_gen:
                for row in batch:
                    if rows_processed >= self.sample_limit:
                        break
                    
                    rows_processed += 1
                    pk_val = row.get(self.mapping.pk_column)
                    
                    # Transform single row
                    try:
                        transformed_tuple = transform_row(row, self.mapping, current_time)
                        # Validate transformed row against metadata
                        self._validate_row(row, transformed_tuple, target_metadata)
                    except BatchFailedError as e:
                        # Catch transformation errors (e.g. CAST failures)
                        ctx = e.context or {}
                        self.report.anomalies.append(Anomaly(
                            category=AnomalyCategory.TRANSFORM_ERROR,
                            severity=AnomalySeverity.BLOCKER,
                            column=ctx.get("column", "unknown"),
                            row_pk=pk_val,
                            raw_value=ctx.get("source_value"),
                            message=str(e),
                            recommendation=f"Periksa konversi tipe di mapping kolom {ctx.get('column')}. Nilai source '{ctx.get('source_value')}' gagal di-cast ke {ctx.get('cast_target')}."
                        ))

                    # Emit progress
                    event_bus.publish(Event(
                        EventType.DRY_RUN_ROW_EVALUATED,
                        {
                            "job_name": self.report.job_name, 
                            "rows_processed": rows_processed, 
                            "total_sample": self.sample_limit
                        }
                    ))
                
                if rows_processed >= self.sample_limit:
                    break

            self.report.rows_extracted = rows_processed
            
        except Exception as e:
            logger.exception(f"Unexpected error during dry run: {e}")
            event_bus.publish(Event(
                EventType.JOB_ABORTED,
                {"job_name": self.report.job_name, "error": str(e), "context": "Extraction/Transformation"}
            ))

        self.report.end_time = datetime.now()
        logger.info(f"Dry run completed. Status: {self.report.status}")
        
        event_bus.publish(Event(
            EventType.DRY_RUN_COMPLETED,
            {"job_name": self.report.job_name, "report": self.report.to_dict()}
        ))
        
        return self.report

    def _check_missing_columns(self, target_metadata: Dict[str, ColumnMetadata]):
        mapped_target_cols = {m.target_column for m in self.mapping.mappings}
        for col_name, meta in target_metadata.items():
            if col_name not in mapped_target_cols:
                # Target column exists but not mapped
                if not meta.is_nullable and meta.default is None:
                    # Potential NOT NULL violation if no DB-side default
                    self.report.anomalies.append(Anomaly(
                        category=AnomalyCategory.MISSING_COLUMN,
                        severity=AnomalySeverity.BLOCKER,
                        column=col_name,
                        row_pk="METADATA",
                        raw_value=None,
                        message=f"Kolom target `{col_name}` bersifat NOT NULL tetapi tidak ada di mapping.",
                        recommendation=f"Tambahkan entry mapping untuk target_column `{col_name}`, atau pastikan kolom punya DEFAULT di DDL target."
                    ))

    def _validate_row(
        self, 
        source_row: Dict[str, Any], 
        transformed_tuple: tuple, 
        target_metadata: Dict[str, ColumnMetadata]
    ):
        pk_val = source_row.get(self.mapping.pk_column)
        
        for i, m in enumerate(self.mapping.mappings):
            val = transformed_tuple[i]
            meta = target_metadata.get(m.target_column)
            
            if not meta:
                # This should have been caught by mapping loader, but just in case
                self.report.anomalies.append(Anomaly(
                    category=AnomalyCategory.MISSING_COLUMN,
                    severity=AnomalySeverity.BLOCKER,
                    column=m.target_column,
                    row_pk=pk_val,
                    raw_value=val,
                    message=f"Kolom target `{m.target_column}` tidak ditemukan di skema database.",
                    recommendation=f"Periksa typo nama kolom target `{m.target_column}` atau sinkronkan DDL target."
                ))
                continue

            # 1. NOT NULL violation
            if val is None and not meta.is_nullable:
                self.report.anomalies.append(Anomaly(
                    category=AnomalyCategory.NOT_NULL_VIOLATION,
                    severity=AnomalySeverity.BLOCKER,
                    column=m.target_column,
                    row_pk=pk_val,
                    raw_value=val,
                    message=f"Nilai NULL untuk kolom NOT NULL `{m.target_column}`.",
                    recommendation=f"Tambahkan transformation_type INJECT_DEFAULT dengan default_value untuk kolom `{m.target_column}`, atau pastikan data source tidak NULL."
                ))

            # 2. Data Truncation
            if isinstance(val, str) and meta.max_length is not None:
                if len(val) > meta.max_length:
                    self.report.anomalies.append(Anomaly(
                        category=AnomalyCategory.DATA_TRUNCATION,
                        severity=AnomalySeverity.ADVISORY,
                        column=m.target_column,
                        row_pk=pk_val,
                        raw_value=val,
                        message=f"Panjang data ({len(val)}) melebihi batas VARCHAR({meta.max_length}).",
                        recommendation=f"Naikkan panjang VARCHAR di mapping/DDL target `{m.target_column}` menjadi minimal {len(val)}."
                    ))

            # 3. ENUM mismatch
            if meta.enum_values is not None and val is not None:
                str_val = str(val)
                if str_val not in meta.enum_values:
                    self.report.anomalies.append(Anomaly(
                        category=AnomalyCategory.ENUM_MISMATCH,
                        severity=AnomalySeverity.ADVISORY,
                        column=m.target_column,
                        row_pk=pk_val,
                        raw_value=val,
                        message=f"Nilai '{str_val}' tidak ada di ENUM target {meta.enum_values}.",
                        recommendation=f"Mapping ulang via CAST + value-map, atau tambah nilai '{str_val}' ke ENUM target `{m.target_column}`."
                    ))
            
            # 4. Basic Type compatibility (already partially handled by CAST in transformer)
            # If transformer succeeded but type is still suspicious
            if val is not None:
                if meta.data_type in ("INT", "BIGINT", "SMALLINT", "TINYINT"):
                    if not isinstance(val, (int, float)):
                        try:
                            int(val)
                        except (ValueError, TypeError):
                            self.report.anomalies.append(Anomaly(
                                category=AnomalyCategory.TYPE_MISMATCH,
                                severity=AnomalySeverity.BLOCKER,
                                column=m.target_column,
                                row_pk=pk_val,
                                raw_value=val,
                                message=f"Nilai '{val}' tidak dapat diubah menjadi integer untuk kolom `{m.target_column}`.",
                                recommendation=f"Ubah cast_target menjadi VARCHAR di mapping kolom `{m.target_column}`, atau bersihkan data source."
                            ))
