from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, START, END, StateGraph
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from typing_extensions import TypedDict
from typing import Dict, Any, Optional, List
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.tools import Tool
from dotenv import load_dotenv

from .tools import detect_brand_model, detect_storage, detect_network
from .utils import update_device_info, format_pending_info, extract_info_from_response
from .models import DeviceInfo
from .session_store import sessions 

load_dotenv()

# Defino mi modelo
llm = ChatOpenAI(model="gpt-4o", temperature=0)

class MessagesState(TypedDict):
    messages: List[BaseMessage]
    device_info: DeviceInfo

tools = [
    Tool(
        name="detect_brand_model",
        func=detect_brand_model,
        description="Detecta la marca y modelo del dispositivo"
    ),
    Tool(
        name="detect_storage",
        func=detect_storage,
        description="Detecta la capacidad de almacenamiento"
    ),
    Tool(
        name="detect_network",
        func=detect_network,
        description="Detecta la compatibilidad con redes"
    )
]

sys_msg = SystemMessage(content="""Eres un asistente de venta de dispositivos móviles. Tu objetivo es ayudar al usuario a vender su dispositivo.

Para ello, necesitas recopilar la siguiente información:
* Marca y modelo del dispositivo
* Capacidad de almacenamiento
* Compatibilidad con 5G

Si falta información, pregunta por ella de manera educada usando el formato de lista proporcionado.
Si el usuario proporciona nueva información, actualiza los datos y solicita la información restante.
Cuando tengas toda la información, resume los detalles del dispositivo.""")


def coordinator(state: MessagesState):
    # Obtener el ID de la sesión actual
    session_id = None
    for sid, session in sessions.items():
        if session["messages"] == state["messages"]:
            session_id = sid
            break
    
    if not session_id:
        print("Warning: Session not found")
        device_info = state["device_info"]
    else:
        # Usar el device_info de la sesión almacenada
        device_info = sessions[session_id]["device_info"]
    
    # Procesar el último mensaje para actualizar la información
    if state["messages"]:
        last_message = state["messages"][-1]
        if isinstance(last_message, HumanMessage):
            # Procesar el mensaje una vez y guardar todos los resultados
            results = {}
            for tool in tools:
                tool_result = tool.invoke(last_message.content)
                if "result" in tool_result:
                    try:
                        new_info = extract_info_from_response(tool_result["result"])
                        if new_info:
                            results.update(new_info)
                    except Exception as e:
                        print(f"Error processing tool result: {e}")

            # Actualizar device_info una sola vez con todos los resultados
            if results:
                print(f"Resultados de la herramienta: {results}")
                device_info = update_device_info(device_info, results)
                
    # Vemos el estado actual del dispositivo
    print(f"Estado actual del dispositivo: {device_info}")
    
    # Actualizar el estado con la nueva información
    state["device_info"] = device_info
    
    # Crear contexto con la información actual y pendiente
    context = (f"{sys_msg.content}\n\n"
              f"Información actual:\n"
              f"- Marca: {device_info.get('brand', 'No disponible')}\n"
              f"- Modelo: {device_info.get('model', 'No disponible')}\n"
              f"- Almacenamiento: {device_info.get('storage', 'No disponible')}\n"
              f"- Red: {device_info.get('network', 'No disponible')}\n\n")
    
    pending_info = format_pending_info(device_info)
    if pending_info:
        context += pending_info
    
    system_message = SystemMessage(content=context)
    
    # Crear una nueva lista de mensajes que incluya solo el sistema y el último mensaje del usuario
    current_messages = [system_message]
    if state["messages"]:
        current_messages.append(state["messages"][-1])
    
    try:
        response = llm.invoke(current_messages)
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        return state

    # Actualizar la sesión almacenada
    if session_id:
        sessions[session_id]["device_info"] = device_info
    
    return {
        "messages": state["messages"] + [response],
        "device_info": device_info
    }

# Graph setup
initial_state = {
    "messages": [],
    "device_info": DeviceInfo(brand="", model="", storage="", network="")
}

builder = StateGraph(MessagesState)

# Node definition
builder.add_node("coordinator", coordinator)
builder.add_node("tools", ToolNode(tools))

# Edge definition
builder.add_edge(START, "coordinator")
builder.add_conditional_edges(
    "coordinator",
    tools_condition,
)
builder.add_edge("tools", "coordinator")

react_graph = builder.compile()
