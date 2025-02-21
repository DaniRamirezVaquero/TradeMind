from typing import Dict, Any, TypedDict, Sequence
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.schema import SystemMessage, BaseMessage
from langgraph.graph import MessagesState

from .tools import predict_price, recommend_device, get_release_date
from .prompts import SYSTEM_PROMPT, GRADING_PROMPT
from .models import ConversationState
from .agent_state import get_next_stage
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define tools como funciones en lugar de diccionarios
tools = [predict_price, recommend_device, get_release_date]

llm_with_tools = llm.bind_tools(tools)

# Define el tipo de estado personalizado que incluye conversation_state
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    conversation_state: ConversationState

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

def can_predict_price(messages: Sequence[BaseMessage]) -> bool:
    """Verifica si tenemos toda la información necesaria para predecir el precio."""
    required_info = {
        "brand": False,
        "model": False,
        "storage": False,
        "has_5g": False,
        "release_date": False,
        "grade": False
    }
    
    # Buscar en los últimos mensajes por la información necesaria
    for msg in messages:
        content = msg.content.lower()
        if "grade" in content and any(grade in content for grade in ["b", "c", "d", "e"]):
            required_info["grade"] = True
        if "fecha de lanzamiento" in content and "/" in content:
            required_info["release_date"] = True
        if "5g" in content:
            required_info["has_5g"] = True
        if "almacenamiento" in content:
            required_info["storage"] = True
        if "modelo" in content:
            required_info["model"] = True
        if "marca" in content:
            required_info["brand"] = True
            
    print("Required info:", required_info)  
    
    return all(required_info.values())

def assistant(state: MessagesState) -> MessagesState:
    """Main assistant node that handles the conversation flow."""
    messages = state["messages"]
    
    # Build prompt with stage awareness
    system_msg = build_system_prompt(messages, state)
    
    # Process with LLM and tools
    if can_predict_price(messages):
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
