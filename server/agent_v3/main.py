
from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from .utils import build_prompt, extract_info, got_basic_info
from .tools import predict_price, recommend_device, get_release_date
from .models import State

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define tools como funciones en lugar de diccionarios
tools = [predict_price, recommend_device, get_release_date]
llm_with_tools = llm.bind_tools(tools)

def assistant(state: State) -> State:
    """Main assistant node that handles the conversation flow."""
    messages = state["messages"]
    
    state["device_info"] = extract_info(messages, llm, state)
    
    # Build prompt with stage awareness
    system_msg = build_prompt(messages, state)
    
    
    # Process with LLM and tools
    if got_basic_info(state):
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
