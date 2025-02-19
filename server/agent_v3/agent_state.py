from langchain.schema import HumanMessage, AIMessage
from .models import ConversationState, DeviceInfo, PhysicalState

def initialize_state():
    """Initialize a new conversation state."""
    return {
        "messages": [
            AIMessage(content="¡Hola! Soy TradeMind, tu agente especializado en reventa de smartphones, ¿en qué te puedo ayudar?")
        ],
        "conversation_state": ConversationState(),
    }

def get_next_stage(current_stage: str, intent: str) -> str:
    """Determine the next conversation stage based on current state and intent."""
    stage_flow = {
        "greeting": "info_gathering",
        "info_gathering": "grade_assessment",
        "grade_assessment": "price_prediction",
        "price_prediction": "end"
    }
    return stage_flow.get(current_stage, "end")
