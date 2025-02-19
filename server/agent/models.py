from typing_extensions import TypedDict
from typing import Optional

class DeviceInfo(TypedDict):
    brand: str
    model: str
    storage: Optional[str]
    network: Optional[str]