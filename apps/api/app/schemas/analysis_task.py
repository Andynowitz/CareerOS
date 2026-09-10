from pydantic import BaseModel


class AnalysisTaskResponse(BaseModel):
    task_id: str
    status: str