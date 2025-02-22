from datetime import datetime
from typing import Dict, Any, TypedDict, Sequence
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.schema import SystemMessage, BaseMessage
from langgraph.graph import MessagesState
import json

from .tools import predict_price, recommend_device, get_release_date
from .prompts import SYSTEM_PROMPT, GRADING_PROMPT
from .models import ConversationState, DeviceInfo
from .agent_state import get_next_stage
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define tools como funciones en lugar de diccionarios
tools = [predict_price, recommend_device, get_release_date]

llm_with_tools = llm.bind_tools(tools)

# Extrae información relevante de los mensajes del usuario
def extract_info(messages: Sequence[BaseMessage], llm):
    sys_msg = """Tu objetivo es analizar estos mensaje y extraer la siguente información de ellos:
    - Marca del dispositivo:
    - Modelo del dispositivo:
    - Almacenamiento del dispositivo:
    - Conectividad 5G (sí/no):
    - Fecha de lanzamiento del dispositivo (MM/YYYY):
    
    Si hay algún dato que el usuario no proporcionó, puedes asumir un valor por defecto, asignalo.
    
    Debes devolver un json con formato válido, para este modelo:
    
    class DeviceInfo(BaseModel):
    brand: str = ""
    model: str = ""
    storage: str = ""
    has_5g: Optional[bool] = None
    release_date: Optional[date] = None
    """
    result = llm.invoke([SystemMessage(content=sys_msg)] + messages)
    result_dict = json.loads(result.content)  # Convertir la cadena JSON a un diccionario
    
        # Convertir la fecha de lanzamiento al formato YYYY-MM-DD
    if 'release_date' in result_dict and result_dict['release_date']:
        try:
            result_dict['release_date'] = datetime.strptime(result_dict['release_date'], "%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            result_dict['release_date'] = None  # Manejar fechas inválidas
            
    return DeviceInfo(**result_dict)

# Define el tipo de estado personalizado que incluye conversation_state
def build_system_prompt(messages: Sequence[BaseMessage], state: Dict) -> SystemMessage:
    """Build system prompt based on conversation stage."""
    # Detectar la etapa actual basándonos en el último mensaje
    current_stage = "info_gathering"  # default
    
    # Buscar palabras clave en los últimos mensajes para determinar la etapa
    last_messages = messages[-3:] if len(messages) > 3 else messages
    for msg in reversed(last_messages):
        if isinstance(msg, BaseMessage):
            content = msg.content.lower()
            if "lanzamiento" in content or "fecha" in content:
                current_stage = "grade_assessment"
                break
            elif any(word in content for word in ["5g", "almacenamiento", "modelo"]):
                current_stage = "info_gathering"
            elif any(word in content for word in ["estado", "condición", "pantalla"]):
                current_stage = "grade_assessment"
                break

    # Construir el prompt base
    base_prompt = SYSTEM_PROMPT.format(conversation_state="Current stage: " + current_stage)
    
    # Añadir el GRADING_PROMPT si estamos en la fase de evaluación
    if current_stage == "grade_assessment":
        return SystemMessage(content=base_prompt + "\n\n" + GRADING_PROMPT)
    
    return SystemMessage(content=base_prompt)

def can_predict_price(conversation_state: ConversationState) -> bool:
    current_device_info = conversation_state.device_info
    
    print("device_info:", current_device_info)
    
    for field in current_device_info.dict().values():
        if field is None or field == "":
            print("Missing information to predict price")
            return False
    
    print("All information available to predict price")
    return True

def assistant(state: MessagesState) -> MessagesState:
    """Main assistant node that handles the conversation flow."""
    messages = state["messages"]
    
    # Recupera o crea la instancia de ConversatiónState
    conversation_state = state.get("conversation_state", ConversationState())
    
    conversation_state.device_info = extract_info(messages, llm)
    
    # Build prompt with stage awareness
    system_msg = build_system_prompt(messages, state)
    
    # Process with LLM and tools
    if can_predict_price(conversation_state):
        print("Predicting price")
        response = llm_with_tools.invoke([system_msg] + messages)
    else:
        print("Not enough information to predict")
        response = llm.invoke([system_msg] + messages)
    
    return {"messages": messages + [response]}

# Build graph
builder = StateGraph(MessagesState)

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
