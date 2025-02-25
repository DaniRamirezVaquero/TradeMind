
from pydantic import BaseModel
from typing import Optional
from datetime import date
from langgraph.graph import MessagesState

class DeviceInfo(BaseModel):
    brand: Optional[str] = ""
    model: Optional[str] = ""
    storage: Optional[str] = ""
    has_5g: Optional[bool] = None
    release_date: Optional[date] = None


class PhysicalState(BaseModel):
    state_screen: Optional[int] = None
    state_body: Optional[int] = None
    state_functional: Optional[int] = None


class State(MessagesState):
    stage: str = "greeting"  
    intent: Optional[str] = None
    device_info: DeviceInfo = DeviceInfo()
    physical_state: PhysicalState = PhysicalState()
    grade: Optional[str] = None