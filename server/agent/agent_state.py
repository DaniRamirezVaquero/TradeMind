from typing import Optional
from langgraph.graph import MessagesState
from langchain.schema import AIMessage

from .models import BuyingInfo, DeviceInfo

class State(MessagesState):
    stage: str = "greeting"  
    intent: Optional[str] = None
    device_info: DeviceInfo = DeviceInfo()
    buying_info: Optional[BuyingInfo] = None

    
def initialize_state():
    """Initialize a new conversation state."""
    return {
        "messages": [
            AIMessage(content="\n## ¡Hola! Soy TradeMind 🤖📱\n*Agente especializado en compra-venta de smartphones*\n\n¿En qué te puedo ayudar?")
        ],
        "stage": "greeting",
        "intent": None,
        "device_info": DeviceInfo(),
        "buying_info": BuyingInfo(),
    }
