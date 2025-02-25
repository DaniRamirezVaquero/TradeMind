from typing import Optional
from langgraph.graph import MessagesState

from .models import DeviceInfo, PhysicalState

class State(MessagesState):
    stage: str = "greeting"  
    intent: Optional[str] = None
    device_info: DeviceInfo = DeviceInfo()
    physical_state: PhysicalState = PhysicalState()
    grade: Optional[str] = None