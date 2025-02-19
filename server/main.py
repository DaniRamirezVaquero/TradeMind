from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from langchain.schema import HumanMessage, AIMessage

from agent.agent import react_graph
from agent.session_manager import get_or_create_session
from agent.session_store import sessions

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # URL de tu cliente Angular
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str
    type: str

class ChatRequest(BaseModel):
    content: str
    type: str
    sessionId: Optional[str] = None

class ChatResponse(BaseModel):
    messages: List[Message]
    sessionId: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    
    # Obtener o crear sesión
    session_id, session_state = get_or_create_session(request.sessionId)
    
    # Actualizar mensajes de la sesión
    session_state["messages"].append(HumanMessage(content=request.content))
    
    # Invocar el agente con el estado de la sesión
    result = react_graph.invoke(session_state)
    
    # Guardar el nuevo estado en la sesión
    sessions[session_id] = result
    
    # Convertir el último mensaje a formato API
    response_messages = []
    if result["messages"]:
        last_message = result["messages"][-1]
        if isinstance(last_message, AIMessage):
            response_messages.append(Message(
                content=last_message.content,
                type="AI",
            ))
    
    return ChatResponse(
        messages=response_messages,
        sessionId=session_id
    )