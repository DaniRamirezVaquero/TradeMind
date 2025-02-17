from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from agent import react_graph
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

class ChatResponse(BaseModel):
    messages: List[Message]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: Message):
    # Inicializar el estado de la conversación
    conversation = {"messages": [HumanMessage(content=message.content)]}
    
    # Invocar el agente
    result = react_graph.invoke(conversation)
    
    # Convertir los mensajes a formato API
    response_messages = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage):
            response_messages.append(Message(
                content=msg.content,
                type="AI",
            ))
    
    return ChatResponse(messages=response_messages)