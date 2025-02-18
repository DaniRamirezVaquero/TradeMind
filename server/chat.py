from agent import react_graph
from langchain.schema import HumanMessage, AIMessage

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