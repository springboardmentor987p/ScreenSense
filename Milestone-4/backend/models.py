from pydantic import BaseModel, Field
from typing import List, Optional

class UserInput(BaseModel):
    age: int = Field(..., ge=8, le=18, description="Age between 8-18")
    gender: str = Field(..., description="Male or Female")
    device: str = Field(..., description="Primary device")
    location: str = Field(..., description="Urban or Rural")
    educational_hours: float = Field(..., ge=0, le=24)
    recreational_hours: float = Field(..., ge=0, le=24)
    health_impacts: List[str] = Field(default=[], description="Health impacts")

class AnalysisResponse(BaseModel):
    age: int
    age_group: str
    gender: str
    device: str
    location: str
    screen_time: float
    educational_hours: float
    recreational_hours: float
    edu_rec_ratio: float
    recommended_limit: float
    exceeds_by: float
    severity: str
    comparisons: dict
    health_impacts: List[str]
    recommendations: List[str]
    comparison_chart: Optional[str] = None  # NEW: Base64 image
    dashboard_chart: Optional[str] = None   # NEW: Base64 image
