from pydantic import BaseModel, ConfigDict

from models.log_entry import EntrySeverity


class ParsedEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: str | None
    severity: EntrySeverity
    message: str
    source: str | None
    line_number: int


class ParseLogResponse(BaseModel):
    log_file_id: int
    filename: str
    total_entries: int
    entries: list[ParsedEntryResponse]
    severity_summary: dict[str, int]
    message: str = "Log parsed successfully"


class ParsedEntryJSON(BaseModel):
    timestamp: str | None
    severity: str
    message: str
    source: str | None
    line_number: int
