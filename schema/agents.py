from pydantic import BaseModel, Field
from typing import Optional


class AgentQuerySchema(BaseModel):
    query: str
  