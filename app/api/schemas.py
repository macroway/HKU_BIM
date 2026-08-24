from pydantic import BaseModel, Field


class SampleInfo(BaseModel):
    id: str
    name: str
    path: str
    format: str


class ModelRegisterResponse(BaseModel):
    model_id: str
    source: str
    format: str


class ChatRequest(BaseModel):
    model_id: str
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str
    tool_traces: list[dict]
    results: dict
    did_run_tools: bool
    planner: str
