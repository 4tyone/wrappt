from pydantic import BaseModel
from typing import Literal, List, Dict


class SiReInputSchema(BaseModel):
    messages: List[Dict]

class SiReOutputSchema(BaseModel):
    stage: Literal["Thought", "Simulate", "FinalAnswer"]
    content: str


class SimulationOutputSchema(BaseModel):
    feedback: str