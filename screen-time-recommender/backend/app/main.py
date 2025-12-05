from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os
from .predict_schema import UserInput
from .model_utils import MODEL_PATH
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(title="ScreenTime Recommender API")

MODEL = None

# Allow requests from your React frontend
origins = [
    "http://localhost:3000",  # React dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)


# Load model on startup
@app.on_event("startup")
async def load_model():
    global MODEL
    if os.path.exists(MODEL_PATH):
        MODEL = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")
    else:
        MODEL = None
        print("Model not found at path:", MODEL_PATH)


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": MODEL is not None}


@app.post("/predict")
async def predict(inp: UserInput):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train model first.")

    # --- Numeric inputs with safe conversion ---
    try:
        age = float(inp.age)
        educational_screentime = float(inp.educational_screentime)
        recreational_screentime = float(inp.recreational_screentime)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid numeric input")

    # --- Calculations ---
    total_screen_time = educational_screentime + recreational_screentime
    rec_ratio = educational_screentime / max(recreational_screentime, 1)

    # --- Encode categorical ---
    gender_map = {"Male": 0, "Female": 1}
    device_map = {"Phone": 0, "Tablet": 1, "TV": 2}
    urban_map = {"Urban": 1, "Rural": 0}

    gender_encoded = gender_map.get(inp.gender, 0)
    device_encoded = device_map.get(inp.device_type, 0)
    urban_encoded = urban_map.get("Urban", 1)

    # --- Prepare DataFrame with EXACT columns the model expects ---
    df = pd.DataFrame([{
        "Age": age,
        "Gender": str(gender_encoded),                 # OneHotEncoder expects string
        "Primary_Device": str(device_encoded),         # OneHotEncoder expects string
        "Educational_to_Recreational_Ratio": rec_ratio,
        "Exceeded_Recommended_Limit": str(int(total_screen_time > 2)), # categorical
        "Urban_or_Rural": str(urban_encoded),
        "Health_Impacts": "0"
    }])

    # --- Ensure column order matches training ---
    df = df[["Age", "Gender", "Primary_Device", "Educational_to_Recreational_Ratio",
             "Exceeded_Recommended_Limit", "Urban_or_Rural", "Health_Impacts"]]

    # --- Predict ---
    try:
        pred = MODEL.predict(df)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    risk_score = min(float(pred) / 5.0, 1.0)
    high_risk = risk_score > 0.5

    return {
        "predicted_screen_time": float(pred),
        "risk_score": float(risk_score),
        "high_risk": high_risk,
        "total_screen_time": total_screen_time
    }


@app.post("/recommend")
async def recommend(inp: UserInput):
    pred_data = await predict(inp)
    score = pred_data["risk_score"]
    age = float(inp.age)
    recs = []

    # --- Risk-based recommendations ---
    if score >= 0.75:
        recs.append("High risk detected: Limit total screen time. Set a daily cap and enable app-level time limits.")
        recs.append("Introduce at least 60 minutes of physical play daily and maintain consistent sleep schedule.")
    elif score >= 0.5:
        recs.append("Moderate risk: Reduce recreational screen time by 20% and encourage educational content.")
    else:
        recs.append("Low risk: Maintain current healthy habits and monitor any upward trends.")

    # --- Age-specific tips ---
    if age < 6:
        recs.append("Prefer co-viewing educational videos with a guardian and avoid solo device time before bed.")
    elif age < 12:
        recs.append("Use parental controls for game purchases and set device-free family times.")
    else:
        recs.append("Encourage self-regulation: use app timers and focus on balanced routines.")

    # --- Device-specific tips ---
    if inp.device_type and inp.device_type.lower() == "tv":
        recs.append("TV use: avoid long consecutive sessions; schedule movement breaks every 30 minutes.")

    return {"recommendations": recs, "risk": pred_data}


@app.get("/dashboard/aggregates")
async def dashboard_aggregates():
    agg_path = "./data/aggregates.csv"
    if not os.path.exists(agg_path):
        raise HTTPException(status_code=404, detail="Aggregates not found. Generate aggregates from dataset.")
    
    df = pd.read_csv(agg_path)
    return df.to_dict(orient="records")
