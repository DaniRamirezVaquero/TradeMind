from typing import Optional
from langgraph.graph import MessagesState
from langchain.schema import AIMessage

from .models import DeviceInfo, PhysicalState

class State(MessagesState):
    stage: str = "greeting"  
    intent: Optional[str] = None
    device_info: DeviceInfo = DeviceInfo()
    physical_state: PhysicalState = PhysicalState()
    grade: Optional[str] = None
    
def initialize_state():
    """Initialize a new conversation state."""
    return {
        "messages": [
            AIMessage(content="¡Hola! Soy TradeMind, tu agente especializado en reventa de smartphones, ¿en qué te puedo ayudar?")
        ]
    }
