from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from typing import Dict, Any
from dotenv import load_dotenv

from .utils import extract_info_from_response


load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

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
    """Detect device storage capacity."""
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
    storage_info = extract_info_from_response(response.content)
    
    valid_storage_options = {"32GB", "64GB", "128GB", "256GB", "512GB", "1TB"}
    if storage_info.get("storage") not in valid_storage_options:
        return {"result": "{}"}
    
    return {"result": response.content}

def detect_network(message: str) -> Dict[str, Any]:
    """Detect if device supports 5G."""
    messages = [
        SystemMessage(content="""Analiza si el dispositivo es compatible con 5G.
        Responde solo con JSON: {"network": "5G"} o {"network": "4G"} o {} si no hay información clara.
        No incluyas texto adicional, solo el JSON."""), 
        HumanMessage(content=message)
    ]
    response = llm.invoke(messages)
    return {"result": response.content}
