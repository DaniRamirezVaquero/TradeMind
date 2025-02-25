import json
from typing import Sequence, Union
from langchain.schema import SystemMessage, BaseMessage
from datetime import date, datetime

from .models import State
from .models import DeviceInfo
from .prompts import SELLING_PROMPT, GRADING_PROMPT, BASIC_INFO_EXTRACTION_PROMPT

def extract_info(messages: Sequence[BaseMessage], llm, state) -> DeviceInfo:
    # Obtener la información existente del state
    current_info = state.device_info if hasattr(state, 'device_info') else DeviceInfo()
    
    # Extraer solo el contenido de los mensajes del usuario
    conversation_text = "\n".join([
        f"Usuario: {msg.content}" if msg.type == "human" else f"Asistente: {msg.content}"
        for msg in messages
    ])
    
    result = llm.invoke([
        SystemMessage(content=BASIC_INFO_EXTRACTION_PROMPT.format(conversation=conversation_text))
    ])
    
    try:
        cleaned_content = result.content.strip()
        result_dict = json.loads(cleaned_content)
        
        # Preservar datos existentes que no sean vacíos
        if current_info:
            # Preservar brand si existe
            if current_info.brand:
                result_dict['brand'] = current_info.brand
            
            # Preservar model si existe
            if current_info.model:
                result_dict['model'] = current_info.model
            
            # Preservar storage si existe
            if current_info.storage:
                result_dict['storage'] = current_info.storage
            
            # Preservar has_5g si existe
            if current_info.has_5g is not None:
                result_dict['has_5g'] = current_info.has_5g
            
            # Preservar release_date si existe
            if current_info.release_date:
                result_dict['release_date'] = current_info.release_date
        
        # Asegurar que los campos string no sean None
        result_dict['brand'] = result_dict.get('brand') or ""
        result_dict['model'] = result_dict.get('model') or ""
        result_dict['storage'] = result_dict.get('storage') or ""
        
                # Procesar fecha si existe y no había una fecha válida previamente
        if result_dict.get('release_date') and not current_info.release_date:
            try:
                date_str = result_dict['release_date']
                if isinstance(date_str, str):
                    if len(date_str.split('/')) == 2:  # Formato MM/YYYY
                        month, year = date_str.split('/')
                        result_dict['release_date'] = f"{year}-{month.zfill(2)}-01"
                    elif len(date_str.split('-')) == 2:  # Formato YYYY-MM
                        result_dict['release_date'] = f"{date_str}-01"
                    elif len(date_str.split('-')) == 3:  # Ya está en formato YYYY-MM-DD
                        # Validar que la fecha sea correcta
                        datetime.strptime(date_str, "%Y-%m-%d")
                        result_dict['release_date'] = date_str
                    else:
                        result_dict['release_date'] = None
            except (ValueError, IndexError):
                # Si hay cualquier error en el procesamiento de la fecha
                result_dict['release_date'] = None
        
        return DeviceInfo(**result_dict)
    
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        print("Contenido del resultado:", cleaned_content)
        # En caso de error, devolver la información existente
        return DeviceInfo()

# Define el tipo de estado personalizado que incluye conversation_state
def build_prompt(messages: Sequence[BaseMessage], state: State) -> SystemMessage:
    """Build system prompt based on conversation stage."""
    # Detectar la etapa actual basándonos en el último mensaje
    state["stage"] = "info_gathering"  # default
    
    # Buscar palabras clave en los últimos mensajes para determinar la etapa
    last_messages = messages[-3:] if len(messages) > 3 else messages
    for msg in reversed(last_messages):
        if isinstance(msg, BaseMessage):
            content = msg.content.lower()
            if "lanzamiento" in content or "fecha" in content or got_basic_info(state):
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
    INFORMACIÓN INFERIDA:
    - Marca: {device_info.brand}
    - Modelo: {device_info.model}
    - Almacenamiento: {device_info.storage}
    - Conectividad 5G: {device_info.has_5g}
    - Fecha de lanzamiento: {device_info.release_date}
    """
    
    base_prompt = SELLING_PROMPT.format(conversation_state="Current stage: " + state["stage"]) + inferred_info

    # Añadir el GRADING_PROMPT si estamos en la fase de evaluación
    if state["stage"] == "grade_assessment":
        return SystemMessage(content=base_prompt + "\n\n" + GRADING_PROMPT)
    
    return SystemMessage(content=base_prompt)

def got_basic_info(state: State) -> bool:
    current_device_info = state["device_info"]
    
    print("device_info:", current_device_info)
    
    for field in current_device_info.model_dump().values():
        if field is None or field == "":
            print("Missing information to predict price")
            return False
    
    print("All information available to predict price")
    return True
  
def parse_date(date_str: Union[str, date]) -> date:
  """Convierte una string de fecha en objeto date."""
  if isinstance(date_str, date):
      return date_str
  try:
      # Intenta parsear primero como MM/YYYY
      if '/' in date_str and len(date_str.split('/')) == 2:
          month, year = date_str.split('/')
          return date(int(year), int(month), 1)
      # Intenta diferentes formatos comunes
      for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
          try:
              return datetime.strptime(date_str, fmt).date()
          except ValueError:
              continue
      raise ValueError(f"No se pudo convertir '{date_str}' a fecha")
  except ValueError as e:
      raise ValueError(f"Error al procesar la fecha: {e}")