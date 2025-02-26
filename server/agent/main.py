
from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

from .utils import build_prompt, detect_intent, extract_buying_info, extract_selling_info, got_basic_buying_info, got_basic_info, intent_change_potential
from .tools import generate_graphic_dict, predict_price, recommend_device, get_release_date
from .agent_state import State

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define tools como funciones en lugar de diccionarios
tools = [predict_price, recommend_device, get_release_date, generate_graphic_dict]
llm_with_tools = llm.bind_tools(tools)


def assistant(state: State) -> State:
    """Main assistant node that handles the conversation flow."""

    # Solo detectar intent si es necesario
    if not state.get("intent"):
        state["intent"] = detect_intent(state, llm)
    elif intent_change_potential(state):
        new_intent = detect_intent(state, llm)
        if new_intent != state["intent"]:
            print(f"Intent changed from {state['intent']} to {new_intent}")
            state["intent"] = new_intent

    if state["intent"] == "sell" or state["intent"] == "graphic":
        state["device_info"] = extract_selling_info(state, llm)
        # Build prompt with stage awareness
        system_msg = build_prompt(state)
        if got_basic_info(state):
            print("Using llm_with_tools")
            response = llm_with_tools.invoke([system_msg] + state["messages"])
            
        else:
            print("Not enough information to predict price")
            response = llm.invoke([system_msg] + state["messages"])
            
    elif state["intent"] == "buy":
        state["buying_info"] = extract_buying_info(state, llm)
        system_msg = build_prompt(state)
        if got_basic_buying_info(state):
            print("Using llm_with_tools")
            response = llm_with_tools.invoke([system_msg] + state["messages"])
            
        else:
            print("Not enough information to recommend device")
            response = llm.invoke([system_msg] + state["messages"])
            
    else:
        system_msg = build_prompt(state)
        response = llm.invoke([system_msg] + state["messages"])

    # Update state
    state["messages"] = state["messages"] + [response]
    return state


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
