from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApplicationChecklistItem(BaseModel):
    item: str
    completed: bool


class ApplicationAssistantResponse(BaseModel):
    job_id: UUID
    status: str

    missing_information: list[str]
    checklist: list[ApplicationChecklistItem]
    next_actions: list[str]

    follow_up_needed: bool
    last_activity_at: datetime | None
    days_since_activity: int | None