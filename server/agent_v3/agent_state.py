from langchain.schema import AIMessage

def initialize_state():
    """Initialize a new conversation state."""
    return {
        "messages": [
            AIMessage(content="¡Hola! Soy TradeMind, tu agente especializado en reventa de smartphones, ¿en qué te puedo ayudar?")
        ]
    }
