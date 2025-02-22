
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
    brand: Optional[str] = ""
    model: Optional[str] = ""
    storage: Optional[str] = ""
    has_5g: Optional[bool] = None
    release_date: Optional[date] = None

class PhysicalState(BaseModel):
    state_screen: Optional[int] = None
    state_body: Optional[int] = None
    state_functional: Optional[int] = None
    grade: Optional[str] = None