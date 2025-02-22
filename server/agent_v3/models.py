
from pydantic import BaseModel

from typing import Optional, List
from datetime import date
from enum import Enum

class State(Enum):
    IMPECABLE = 1
    BUENO = 2
    USADO = 3
    ROTO = 4

class Functional(Enum):
    SI = 1
    NO = 2

class DeviceInfo(BaseModel):
    brand: str = ""
    model: str = ""
    storage: str = ""
    has_5g: Optional[bool] = None
    release_date: Optional[date] = None

class PhysicalState(BaseModel):
    state_screen: Optional[int] = None
    state_body: Optional[int] = None
    state_functional: Optional[int] = None
    grade: Optional[str] = None

class ConversationState(BaseModel):
    stage: str = "greeting"  # greeting, info_gathering, grade_assessment, price_prediction
    intent: Optional[str] = None  # buy, sell
    device_info: DeviceInfo = DeviceInfo()
    physical_state: PhysicalState = PhysicalState()
