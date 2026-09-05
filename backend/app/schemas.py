from typing import Any, List
from pydantic import BaseModel, Field


class TaskPlan(BaseModel):
    id: str
    tool: str
    arguments: dict[str, Any]
    depends_on: List[str] = Field(default_factory=list)


class SupervisorPlan(BaseModel):
    reason: str
    tasks: List[TaskPlan] = Field(default_factory=list)