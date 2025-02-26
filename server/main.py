from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from langchain.schema import HumanMessage, AIMessage
from uuid import uuid4

from agent.main import react_graph
from agent.agent_state import initialize_state

# Dictionary to store session data
sessions = {}

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
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


def get_or_create_session(session_id: Optional[str] = None) -> tuple[str, dict]:
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]

    new_session_id = session_id or str(uuid4())
    # Initialize with the new agent state
    sessions[new_session_id] = initialize_state()
    return new_session_id, sessions[new_session_id]


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Obtener o crear sesión
    session_id, session_state = get_or_create_session(request.sessionId)

    # Guardar el índice del último mensaje antes de añadir el nuevo
    last_message_index = len(session_state["messages"])

    # Añadir el mensaje del usuario al estado
    session_state["messages"].append(HumanMessage(content=request.content))

    # Invocar el agente con el estado de la sesión y actualizarlo
    result = react_graph.invoke(session_state)
    sessions[session_id] = result

    # Obtener todos los mensajes nuevos (después del mensaje del usuario)
    new_messages = result["messages"][last_message_index + 1:]
    
    # Convertir los nuevos mensajes al formato de respuesta
    response_messages = []
    for msg in new_messages:
        msg_type = "AI" if isinstance(msg, AIMessage) else "Human" if isinstance(
            msg, HumanMessage) else "tool_result"
        response_messages.append(Message(
            content=msg.content,
            type=msg_type,
        ))

    return ChatResponse(
        messages=response_messages,
        sessionId=session_id
    )


@app.post("/init-session", response_model=ChatResponse)
async def init_session():
    # Crear nueva sesión
    session_id, session_state = get_or_create_session()

    # Convertir mensajes a formato API
    response_messages = []
    for msg in session_state["messages"]:
        msg_type = "AI" if isinstance(msg, AIMessage) else "Human" if isinstance(
            msg, HumanMessage) else "tool_result"
        response_messages.append(Message(
            content=msg.content,
            type=msg_type,
        ))

    return ChatResponse(
        messages=response_messages,
        sessionId=session_id
    )


@app.get("/messages/{session_id}", response_model=ChatResponse)
async def get_messages(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_state = sessions[session_id]

    # Convertir mensajes a formato API
    response_messages = []
    for msg in session_state["messages"]:
        msg_type = "AI" if isinstance(msg, AIMessage) else "Human" if isinstance(
            msg, HumanMessage) else "tool_result"
        response_messages.append(Message(
            content=msg.content,
            type=msg_type,
        ))

    return ChatResponse(
        messages=response_messages,
        sessionId=session_id
    )
