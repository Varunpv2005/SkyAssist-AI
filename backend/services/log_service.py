import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database.config import settings
from models.log_file import LogFile, LogStatus
from models.user import User

ALLOWED_EXTENSIONS = {".log", ".txt", ".csv"}
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


class LogService:
    @staticmethod
    def _get_logs_dir() -> Path:
        logs_dir = Path(settings.LOGS_DIR)
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    @staticmethod
    def _validate_filename(filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )
        return ext.lstrip(".")

    @staticmethod
    async def upload_log(db: Session, file: UploadFile, user: User) -> LogFile:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required",
            )

        file_type = LogService._validate_filename(file.filename)

        safe_filename = Path(file.filename).name
        if not safe_filename or safe_filename in (".", ".."):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename",
            )

        stored_filename = f"{uuid.uuid4().hex}_{safe_filename}"
        logs_dir = LogService._get_logs_dir()
        file_path = (logs_dir / stored_filename).resolve()
        if not str(file_path).startswith(str(logs_dir.resolve())):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename",
            )

        total_size = 0
        chunk_size = 1024 * 64  # 64KB chunks
        try:
            with open(file_path, "wb") as f:
                while True:
                    chunk = await file.read(chunk_size)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    if total_size > MAX_FILE_SIZE:
                        f.close()
                        if file_path.exists():
                            file_path.unlink()
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB",
                        )
                    f.write(chunk)
        except HTTPException:
            raise
        except Exception as exc:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading file: {exc}",
            )

        if total_size == 0:
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        log_record = LogFile(
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_size=total_size,
            file_type=file_type,
            status=LogStatus.UPLOADED,
            uploaded_by=user.id,
        )
        db.add(log_record)
        db.commit()
        db.refresh(log_record)
        return log_record

    @staticmethod
    def list_logs(db: Session, user: User) -> list[LogFile]:
        return (
            db.query(LogFile)
            .filter(LogFile.uploaded_by == user.id)
            .order_by(LogFile.created_at.desc())
            .all()
        )

    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> LogFile | None:
        return db.query(LogFile).filter(LogFile.id == log_id).first()

    @staticmethod
    def get_log_for_user(db: Session, log_id: int, user: User) -> LogFile:
        log_file = LogService.get_log_by_id(db, log_id)
        if not log_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Log file not found",
            )
        if log_file.uploaded_by != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this log file",
            )
        return log_file
