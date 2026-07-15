from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.log_file import LogStatus


class LogUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_size: int
    file_type: str
    status: LogStatus
    uploaded_by: int
    created_at: datetime
    message: str = "File uploaded successfully"


class LogFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_size: int
    file_type: str
    status: LogStatus
    uploaded_by: int
    created_at: datetime


class LogListResponse(BaseModel):
    total: int
    logs: list[LogFileResponse]
