from fastapi import FastAPI
from fastapi.responses import Response, FileResponse
from pathlib import Path
import base64
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from utils import RecommendationEngine

CSV_PATH = "Data.csv"

app = FastAPI(title="Kids Screen Time Insights API")

# Enable CORS BEFORE adding routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Lazy-load the engine (will be initialized on first request)
engine = None


def get_engine():
    global engine
    if engine is None:
        engine = RecommendationEngine(CSV_PATH)
    return engine


@app.get("/")
async def root():
    return {"message": "ok"}


@app.get("/data")
def get_data():
    """Return the entire dataset as JSON records for dashboard consumption.
    This endpoint returns an array of records mirroring the CSV rows.
    """
    engine = get_engine()
    if engine.df is None or engine.df.empty:
        return []
    # Convert dataframe to records and ensure JSON-serializable types
    records = engine.df.fillna("").to_dict(orient="records")
    return records


@app.get("/favicon.ico")
async def favicon():
    # Serve a bundled tiny PNG if no static favicon is present to avoid 404s
    static_ico = Path(__file__).parent / "static" / "favicon.ico"
    if static_ico.exists():
        return FileResponse(str(static_ico), media_type="image/x-icon")
    # 1x1 transparent PNG (base64)
    png_b64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQImWNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
    return Response(content=base64.b64decode(png_b64), media_type="image/png")


class InputPayload(BaseModel):
    Age: int
    Gender: str
    Avg_Daily_Screen_Time_hr: float
    Primary_Device: str
    Educational_to_Recreational_Ratio: Optional[float] = None
    Health_Impacts: Optional[str] = ""
    Urban_or_Rural: Optional[str] = "Urban"


@app.post("/insights")
def get_insights(payload: InputPayload):
    print(f"DEBUG: Received insights request with payload: {payload}")
    engine = get_engine()
    user = payload.dict()
    print(f"DEBUG: User data: {user}")
    exceeded, insights, details = engine.generate_insights(user)
    print(f"DEBUG: Generated insights: {insights}")
    result = {
        "exceeded_recommended_limit": exceeded,
        "insights": insights,
        "details": details,
    }
    print(f"DEBUG: Returning result: {result}")
    return result
