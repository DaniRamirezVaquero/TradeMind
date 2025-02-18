from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from agent import react_graph, get_or_create_session, DeviceInfo
from langchain.schema import HumanMessage, AIMessage

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
    
    # Convertir los mensajes a formato API
    response_messages = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage):
            response_messages.append(Message(
                content=msg.content,
                type="AI",
            ))
    
    return ChatResponse(
        messages=response_messages,
        sessionId=session_id
    )