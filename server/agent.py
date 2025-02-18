from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, START, END, StateGraph
from langchain.schema import SystemMessage, HumanMessage, AIMessage, BaseMessage
from typing_extensions import TypedDict
from typing import Dict, Any, Optional, List
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.tools import Tool
from dotenv import load_dotenv
import os
import uuid

load_dotenv()  # Cargar variables de entorno desde .env

# Defino mi modelo
llm = ChatOpenAI(model="gpt-4o", temperature=0)

class DeviceInfo(TypedDict):
    brand: str
    model: str
    storage: Optional[str]
    network: Optional[str]

class MessagesState(TypedDict):
    messages: List[BaseMessage]
    device_info: DeviceInfo

def detect_brand_model(message: str) -> Dict[str, Any]:
    """Detect device brand and model from text."""
    messages = [
        SystemMessage(content="""Analiza el mensaje y extrae marca y modelo del dispositivo.
        Marcas comunes: Apple(iPhone), Samsung, Xiaomi, Huawei, Sony, Google, OnePlus.
        Solo responde con un JSON válido. Ejemplo:
        {"brand": "Samsung", "model": "S25"} o {} si no hay información clara.
        No incluyas texto adicional, solo el JSON."""),
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    return {"result": response.content}

def detect_storage(message: str) -> Dict[str, Any]:
    """Detect device storage capacity.
    
    Parameters:
        message: Input message containing storage information
    Returns:
        Dictionary with storage information
    """
    messages = [
        SystemMessage(content="""Analiza el mensaje y extrae la capacidad de almacenamiento.
        Formato común: 64GB, 128GB, 256GB, 512GB, 1TB
        Responde solo con JSON válido.
        Ejemplo:
        {"storage": "128GB"} o {} si no hay información clara.
        No incluyas texto adicional, solo el JSON."""),
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    return {"result": response.content}

def detect_network(message: str) -> Dict[str, Any]:
    """Detect if device supports 5G.
    
    Parameters:
        message: Input message containing network information
    Returns:
        Dictionary with network support information
    """
    messages = [
        SystemMessage(content="""Analiza si el dispositivo es compatible con 5G.
        Responde solo con JSON: {"network": "5G"} o {"network": "4G"}o {} si no hay información clara.
        No incluyas texto adicional, solo el JSON."""),
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    return {"result": response.content}

def extract_info_from_response(response: str) -> Dict[str, Any]:
    """Extract information from JSON response string.
    
    Parameters:
        response: JSON string from tool response
    Returns:
        Dictionary with extracted information
    """
    try:
        import json
        return json.loads(response)
    except:
        return {}

def update_device_info(current_info: DeviceInfo, new_info: Dict[str, Any]) -> DeviceInfo:
    """Update device information with new data.
    
    Parameters:
        current_info: Current device information
        new_info: New information to add
    Returns:
        Updated device information
    """
    # Crear una copia del estado actual
    updated_info = dict(current_info)
    
    # Solo actualizar los campos que vienen con nueva información
    for key in ['brand', 'model', 'storage', 'network']:
        if key in new_info and new_info[key]:
            updated_info[key] = new_info[key]
    
    print(f"Estado anterior: {current_info}")
    print(f"Nueva información: {new_info}")
    print(f"Estado actualizado: {updated_info}")
    
    return DeviceInfo(**updated_info)

# Modificar la definición de las herramientas
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

def format_pending_info(device_info: DeviceInfo) -> str:
    """Format pending device information as a Markdown list.
    
    Parameters:
        device_info: Current device information
    Returns:
        Markdown formatted string with pending information
    """
    pending = []
    if not device_info.get('brand') or not device_info.get('model'):
        pending.append("- Marca y modelo del dispositivo")
    if not device_info.get('storage'):
        pending.append("- Capacidad de almacenamiento")
    if not device_info.get('network'):
        pending.append("- Compatibilidad con 5G")
    
    if pending:
        return "Necesito la siguiente información:\n" + "\n".join(pending)
    return ""

sys_msg = SystemMessage(content="""Eres un asistente de venta de dispositivos móviles. Tu objetivo es ayudar al usuario a vender su dispositivo.

Para ello, necesitas recopilar la siguiente información:
* Marca y modelo del dispositivo
* Capacidad de almacenamiento
* Compatibilidad con 5G

Si falta información, pregunta por ella de manera educada usando el formato de lista proporcionado.
Si el usuario proporciona nueva información, actualiza los datos y solicita la información restante.
Cuando tengas toda la información, resume los detalles del dispositivo.""")

# Almacén de sesiones
sessions: Dict[str, MessagesState] = {}

def get_or_create_session(session_id: str = None) -> tuple[str, MessagesState]:
    """Get existing session or create new one."""
    if session_id and session_id in sessions:
        return session_id, sessions[session_id]
    
    new_session_id = session_id or str(uuid.uuid4())
    sessions[new_session_id] = {
        "messages": [],
        "device_info": DeviceInfo(brand="", model="", storage="", network="")
    }
    return new_session_id, sessions[new_session_id]

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
