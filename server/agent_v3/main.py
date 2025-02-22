from datetime import datetime
from typing import Optional, Sequence
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.schema import SystemMessage, BaseMessage
from langgraph.graph import MessagesState
import json

from .tools import predict_price, recommend_device, get_release_date
from .prompts import SYSTEM_PROMPT, GRADING_PROMPT
from .models import DeviceInfo, PhysicalState
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define tools como funciones en lugar de diccionarios
tools = [predict_price, recommend_device, get_release_date]

llm_with_tools = llm.bind_tools(tools)

class State(MessagesState):
    stage: str = "greeting"  # greeting, info_gathering, grade_assessment, price_prediction
    intent: Optional[str] = None  # buy, sell
    device_info: DeviceInfo = DeviceInfo()
    physical_state: PhysicalState = PhysicalState()

def extract_info(messages: Sequence[BaseMessage], llm) -> DeviceInfo:
    # Extraer solo el contenido de los mensajes del usuario
    conversation_text = "\n".join([
        f"Usuario: {msg.content}" if msg.type == "human" else f"Asistente: {msg.content}"
        for msg in messages
    ])
    
    sys_msg = """AActúa como un parseador de información con capacidad de inferencia. Tu tarea es:
    1. Analizar el texto proporcionado
    2. Extraer información explícita sobre el dispositivo móvil
    3. Inferir información implícita basada en tu conocimiento (ejemplo: si mencionan iPhone 12, puedes inferir que es Apple, tiene 5G, etc.)
    4. Generar un JSON con toda la información, tanto explícita como inferida
    
    NO debes interactuar ni hacer preguntas. Solo extrae la información disponible y genera un JSON.

    FORMATO DE SALIDA REQUERIDO:
    {{
        "brand": string or "",
        "model": string or "",
        "storage": string or "",
        "has_5g": boolean or null,
        "release_date": "YYYY-MM-DD" or null
    }}

    REGLAS:
    1. NO incluyas texto explicativo
    2. NO hagas preguntas
    3. NO interactúes con el usuario
    4. Si un dato no está presente en el texto, usa "" para strings o null para el resto
    5. La respuesta debe ser SOLO el JSON

    CONVERSACIÓN A ANALIZAR:
    ===
    {conversation}
    ===

    RESPONDE ÚNICAMENTE CON EL JSON.
    
    EJEMPLO DE SALIDA CORRECTA:
    {{"brand": "Apple", "model": "iPhone 12", "storage": "128GB", "has_5g": true, "release_date": "2020-10-23"}}
    
    EJEMPLO DE SALIDA CON DATOS FALTANTES:
    {{"brand": "", "model": "", "storage": "", "has_5g": null, "release_date": null}}
    """
    
    result = llm.invoke([
        SystemMessage(content=sys_msg.format(conversation=conversation_text))
    ])
    
    try:
        cleaned_content = result.content.strip()
        result_dict = json.loads(cleaned_content)
        
        # Asegurar que los campos string no sean None
        result_dict['brand'] = result_dict.get('brand') or ""
        result_dict['model'] = result_dict.get('model') or ""
        result_dict['storage'] = result_dict.get('storage') or ""
        
        # Procesar fecha si existe
        if result_dict.get('release_date'):
            try:
                # Intentar convertir varios formatos de fecha comunes
                date_str = result_dict['release_date']
                if len(date_str.split('/')) == 2:  # Formato MM/YYYY
                    date_obj = datetime.strptime(date_str, "%m/%Y")
                    result_dict['release_date'] = date_obj.replace(day=1).strftime("%Y-%m-%d")
                elif len(date_str.split('-')) == 3:  # Ya está en formato YYYY-MM-DD
                    datetime.strptime(date_str, "%Y-%m-%d")  # Validar formato
                else:
                    result_dict['release_date'] = None
            except ValueError:
                result_dict['release_date'] = None
        
        return DeviceInfo(**result_dict)
    
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        print("Contenido del resultado:", cleaned_content)
        # En caso de error, devolver un DeviceInfo vacío
        return DeviceInfo()

# Define el tipo de estado personalizado que incluye conversation_state
def build_system_prompt(messages: Sequence[BaseMessage], state: State) -> SystemMessage:
    """Build system prompt based on conversation stage."""
    # Detectar la etapa actual basándonos en el último mensaje
    state["stage"] = "info_gathering"  # default
    
    # Buscar palabras clave en los últimos mensajes para determinar la etapa
    last_messages = messages[-3:] if len(messages) > 3 else messages
    for msg in reversed(last_messages):
        if isinstance(msg, BaseMessage):
            content = msg.content.lower()
            if "lanzamiento" in content or "fecha" in content or can_predict_price(state):
                state["stage"] = "grade_assessment"
                break
            elif any(word in content for word in ["5g", "almacenamiento", "modelo"]):
                state["stage"] = "info_gathering"
            elif any(word in content for word in ["estado", "condición", "pantalla"]):
                state["stage"] = "grade_assessment"
                break

    # Construir el prompt base
    device_info = state["device_info"]
    inferred_info = f"""
    Información inferida:
    - Marca: {device_info.brand}
    - Modelo: {device_info.model}
    - Almacenamiento: {device_info.storage}
    - Conectividad 5G: {device_info.has_5g}
    - Fecha de lanzamiento: {device_info.release_date}
    """
    
    base_prompt = SYSTEM_PROMPT.format(conversation_state="Current stage: " + state["stage"]) + inferred_info

    
    # Añadir el GRADING_PROMPT si estamos en la fase de evaluación
    if state["stage"] == "grade_assessment":
        return SystemMessage(content=base_prompt + "\n\n" + GRADING_PROMPT)
    
    return SystemMessage(content=base_prompt)

def can_predict_price(state: State) -> bool:
    current_device_info = state["device_info"]
    
    print("device_info:", current_device_info)
    
    for field in current_device_info.model_dump().values():
        if field is None or field == "":
            print("Missing information to predict price")
            return False
    
    print("All information available to predict price")
    return True

def assistant(state: State) -> State:
    """Main assistant node that handles the conversation flow."""
    messages = state["messages"]
    
    state["device_info"] = extract_info(messages, llm)
    
    # Build prompt with stage awareness
    system_msg = build_system_prompt(messages, state)
    
    # Process with LLM and tools
    if can_predict_price(state):
        print("Using llm_with_tools")
        response = llm_with_tools.invoke([system_msg] + messages)
    else:
        print("Not enough information to predict")
        response = llm.invoke([system_msg] + messages)
    
    return {"messages": messages + [response]}

# Build graph
builder = StateGraph(State)

# Define nodes
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    tools_condition,  # Esto determina si vamos a tools o END
)
builder.add_edge("tools", "assistant")

# Compile graph
react_graph = builder.compile()
