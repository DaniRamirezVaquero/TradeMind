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
    return SystemMessage(content=SYSTEM_PROMPT.format(
        conversation_state="Processing your request..."
    ))

def assistant(state: MessagesState) -> MessagesState:
    """Main assistant node that handles the conversation flow."""
    # Get messages from state
    messages = state["messages"]
    
    # Build prompt
    system_msg = build_system_prompt(messages)
    
    # Process with LLM and tools
    response = llm_with_tools.invoke([system_msg] + messages)
    
    # Return updated state
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
