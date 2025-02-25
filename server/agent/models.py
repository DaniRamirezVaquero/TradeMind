
from pydantic import BaseModel
from typing import Optional
from datetime import date

class DeviceInfo(BaseModel):
    brand: Optional[str] = ""
    model: Optional[str] = ""
    storage: Optional[str] = ""
    has_5g: Optional[bool] = None
    release_date: Optional[date] = None

class PhysicalState(BaseModel):
    state_screen: Optional[int] = None
    state_body: Optional[int] = None
    state_functional: Optional[int] = None
