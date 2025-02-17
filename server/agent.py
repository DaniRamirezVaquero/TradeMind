from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, START, END, StateGraph
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict
from typing import Dict, Any, Optional
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.tools import Tool
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables de entorno desde .env

# Defino mi modelo
llm = ChatOpenAI(model="gpt-4o", temperature=0)

class DeviceInfo(TypedDict):
    brand: str
    model: str
    storage: Optional[str]
    network: Optional[str]

def detect_brand_model(message: str) -> Dict[str, Any]:
    """Detect device brand and model from text.
    
    Parameters:
        message: Input message containing device information
    Returns:
        Dictionary with brand and model information
    """
    messages = [
        SystemMessage(content="""Analiza el mensaje y extrae marca y modelo del dispositivo.
        Marcas comunes: Apple(iPhone), Samsung, Xiaomi, Huawei, Sony, Google, OnePlus.
        Responde solo con JSON: {"brand": "marca", "model": "modelo"} o {} si no hay información."""),
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
        Responde solo con JSON: {"storage": "capacidad"} o {} si no hay información."""),
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
        Responde solo con JSON: {"network": "5G"} o {"network": "4G"} o {} si no hay información."""),
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    return {"result": response.content}

# Tools definition
tools = [detect_brand_model, detect_storage, detect_network]
llm_with_tools = llm.bind_tools(tools)

sys_msg = SystemMessage(content="""Eres un asistente de venta de dipositivos móviles, deber ayudar al usuario a vender su dispositivo,
                        para ello debes extraer la marca, modelo, capacidad de almacenamiento y si es compatible con 5G.""")

def coordinator(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph setup
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

def chat():
    """Interactive chat function"""
    from colorama import init, Fore, Style
    init()
    
    print("¡Bienvenido! Puedes preguntarme sobre dispositivos móviles. (Escribe 'salir' para terminar)")
    print("-" * 50)
    
    conversation = {"messages": []}
    last_message_count = 0
    
    while True:
        user_input = input(f"\n{Fore.GREEN}Tú:{Style.RESET_ALL} ")
        
        if user_input.lower() in ['salir', 'exit', 'quit']:
            print("\n¡Hasta luego!")
            break
            
        conversation["messages"].append(HumanMessage(content=user_input))
        result = react_graph.invoke(conversation)
        
        # Get only new messages
        new_messages = result["messages"][last_message_count:]
        last_message_count = len(result["messages"])
        
        # Update conversation state
        conversation["messages"] = result["messages"]
        
        # Print only new messages with formatting
        for message in new_messages:
            if isinstance(message, AIMessage):
                if hasattr(message, 'additional_kwargs') and 'function_call' in message.additional_kwargs:
                    tool_call = message.additional_kwargs['function_call']
                    print(f"\n{Fore.YELLOW}🔧 Llamada a herramienta:{Style.RESET_ALL}")
                    print(f"   Función: {tool_call['name']}")
                    print(f"   Argumentos: {tool_call['arguments']}")
                else:
                    print(f"\n{Fore.BLUE}🤖 Asistente:{Style.RESET_ALL} {message.content}")
            elif isinstance(message, HumanMessage):
                continue
            else:
                print(f"\n{Fore.CYAN}📎 Resultado herramienta:{Style.RESET_ALL}")
                print(f"   {message.content}")

if __name__ == "__main__":
    chat()


