import uuid
from typing import Dict
from langchain.schema import AIMessage

from .agent import MessagesState
from .models import DeviceInfo
from .session_store import sessions  # Importar sessions desde session_store

def get_or_create_session(session_id: str = None) -> tuple[str, MessagesState]:
    """Get existing session or create new one."""
    if session_id and session_id in sessions:
        print(f"Sesión existente encontrada: {session_id}")
        return session_id, sessions[session_id]
    
    new_session_id = session_id or str(uuid.uuid4())
    sessions[new_session_id] = {
        "messages": [
            AIMessage(content="Hola! Soy TradeMind, tu agente especializado en reventa de smartphones, en que te puedo ayudar?")
        ],
        "device_info": DeviceInfo(brand="", model="", storage="", network="")
    }
    print(f"Sesión creada: {new_session_id}")
    return new_session_id, sessions[new_session_id]