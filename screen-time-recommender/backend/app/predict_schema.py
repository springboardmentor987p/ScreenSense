from pydantic import BaseModel
from typing import Optional


class UserInput(BaseModel):
    age: int
    gender: str
    educational_screentime: float
    recreational_screentime: float
    device_type: Optional[str] = None
    sleep_hours: Optional[float] = None
    eye_strain_score: Optional[float] = None
    physical_activity_minutes: Optional[float] = None
    

