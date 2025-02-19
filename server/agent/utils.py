import json
from typing import Dict, Any

from .models import DeviceInfo

def extract_info_from_response(response: str) -> Dict[str, Any]:
    """Extract information from JSON response string."""
    try:
        return json.loads(response)
    except:
        return {}

def update_device_info(current_info: DeviceInfo, new_info: Dict[str, Any]) -> DeviceInfo:
    """Update device information with new data."""
    updated_info = dict(current_info)
    for key in ['brand', 'model', 'storage', 'network']:
        if key in new_info and new_info[key]:
            updated_info[key] = new_info[key]
    
    print(f"Estado anterior: {current_info}")
    print(f"Nueva información: {new_info}")
    print(f"Estado actualizado: {updated_info}")
    
    return DeviceInfo(**updated_info)

def format_pending_info(device_info: DeviceInfo) -> str:
    """Format pending device information as a Markdown list."""
    pending = []
    if not device_info.get('brand') or not device_info.get('model'):
        pending.append("- Marca y modelo del dispositivo")
    if not device_info.get('storage'):
        pending.append("- Capacidad de almacenamiento")
    if not device_info.get('network'):
        pending.append("- Compatibilidad con 5G")
    
    if pending:
        return "Necesito la siguiente información:\n" + "\n".join(pending)
    return ""
