from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from log_parser.service import parse_log_content
from models.incident import Incident
from models.log_entry import EntrySeverity, LogEntry
from models.log_file import LogFile, LogStatus


class LogParserService:
    @staticmethod
    def _severity_enum(raw: str) -> EntrySeverity:
        try:
            return EntrySeverity(raw.upper())
        except ValueError:
            return EntrySeverity.UNKNOWN

    @staticmethod
    def parse_log_file(db: Session, log_file: LogFile) -> list[LogEntry]:
        file_path = Path(log_file.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file not found on disk",
            )

        log_file.status = LogStatus.PROCESSING
        db.commit()

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            parsed = parse_log_content(content, log_file.file_type, log_file.filename)

            db.query(Incident).filter(Incident.log_file_id == log_file.id).update(
                {"log_entry_id": None}, synchronize_session=False
            )
            db.query(LogEntry).filter(LogEntry.log_file_id == log_file.id).delete()

            entries: list[LogEntry] = []
            for item in parsed:
                entry = LogEntry(
                    log_file_id=log_file.id,
                    timestamp=item.timestamp,
                    severity=LogParserService._severity_enum(item.severity),
                    message=item.message,
                    source=item.source,
                    line_number=item.line_number,
                )
                db.add(entry)
                entries.append(entry)

            log_file.status = LogStatus.PARSED
            db.commit()
            for entry in entries:
                db.refresh(entry)
            return entries

        except Exception as exc:
            log_file.status = LogStatus.FAILED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to parse log file: {exc}",
            ) from exc

    @staticmethod
    def get_entries(db: Session, log_file_id: int) -> list[LogEntry]:
        return (
            db.query(LogEntry)
            .filter(LogEntry.log_file_id == log_file_id)
            .order_by(LogEntry.line_number)
            .all()
        )

    @staticmethod
    def severity_summary(entries: list[LogEntry]) -> dict[str, int]:
        summary: dict[str, int] = {}
        for entry in entries:
            key = entry.severity.value
            summary[key] = summary.get(key, 0) + 1
        return summary
