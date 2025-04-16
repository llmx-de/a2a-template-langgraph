from pydantic import BaseModel
from typing import List

class AgentCapabilities(BaseModel):
    streaming: bool = True
    pushNotifications: bool = False

class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]

class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    capabilities: AgentCapabilities
    skills: List[AgentSkill] 