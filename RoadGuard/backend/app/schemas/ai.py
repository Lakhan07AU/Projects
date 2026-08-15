from pydantic import BaseModel


class ReportRequest(BaseModel):
    pothole_id: str


class AssistantRequest(BaseModel):
    question: str
