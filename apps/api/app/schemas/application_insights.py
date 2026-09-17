from pydantic import BaseModel


class ApplicationFunnel(BaseModel):
    saved: int
    applied: int
    interview: int
    offer: int
    rejected: int
    withdrawn: int


class ApplicationInsightsResponse(BaseModel):
    total_applications: int
    applied: int
    interviews: int
    offers: int

    response_count: int
    response_rate: float
    interview_rate: float
    offer_rate: float

    funnel: ApplicationFunnel

    status_transitions: dict[str, int]