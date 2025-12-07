from pydantic import BaseModel
from fastapi import FastAPI
app = FastAPI()
import recommend
import pandas as pd
from recommend import load_and_preprocess_data
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.responses import HTMLResponse

# Pydantic models for request bodies
class LoginRequest(BaseModel):
    username: str
    password: str

class LogoutRequest(BaseModel):
    session_id: str

class VerifySessionRequest(BaseModel):
    session_id: str

# Global variable to store API key
GEMINI_API_KEY = None

# Read API key directly from .env file
def load_api_key():
    global GEMINI_API_KEY
    env_path = Path(__file__).parent / '.env'
    print(f"[STARTUP] Checking for .env at: {env_path}")
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[STARTUP] .env file contents (first 100 chars): {content[:100]}")
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('GEMINI_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        print(f"[STARTUP] Found GEMINI_API_KEY: {key[:20]}...")
                        if key and key != 'YOUR_ACTUAL_KEY_HERE' and key != 'YOUR_GEMINI_API_KEY_HERE':
                            GEMINI_API_KEY = key
                            os.environ['GEMINI_API_KEY'] = key
                            print(f"[STARTUP] API Key loaded successfully!")
                            return key
                        else:
                            print(f"[STARTUP] API Key is placeholder or empty")
        except Exception as e:
            print(f"[STARTUP] Error reading .env: {e}")
    else:
        print(f"[STARTUP] .env file not found at {env_path}")
    
    # Fallback to hardcoded key if .env fails
    fallback_key = "AIzaSyAQ89jrJYaN_o5c_TLEQA6lJD1S6rXH6G8"
    print(f"[STARTUP] Using fallback API key")
    GEMINI_API_KEY = fallback_key
    os.environ['GEMINI_API_KEY'] = fallback_key
    return fallback_key

api_key_loaded = load_api_key()
print(f"[STARTUP] API key load result: {api_key_loaded[:20] if api_key_loaded else 'FAILED'}")

# Global variable to store if data is loaded
data_loaded = False

# Mount a `static` directory for any local assets and enable CORS for development
if not os.path.exists("static"):
    try:
        os.makedirs("static")
    except Exception:
        pass

app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow all origins during local development – tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

@app.on_event("startup")
def startup_event():
    """Load data on startup if CSV file exists"""
    global data_loaded
    csv_path = "Indian_Kids_Screen_Time.csv"
    if os.path.exists(csv_path):
        try:
            load_and_preprocess_data(csv_path)
            data_loaded = True
            print("[OK] Data loaded successfully on startup")
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
    else:
        print(f"[WARNING] CSV file not found at {csv_path}. Please upload the dataset.")

# Simple in-memory user store (username: password mapping)
# Single shared password for all external users
SHARED_PASSWORD = "screen123"

# Session store (session_id: username mapping)
SESSIONS = {}

@app.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate user with shared password - any username works"""
    username = request.username
    password = request.password
    print(f"[AUTH] Login attempt for user: {username}")
    
    # Check if password matches the shared password
    if password != SHARED_PASSWORD:
        print(f"[AUTH] Incorrect password for user: {username}")
        return {"status": "error", "message": "Invalid password"}
    
    # Generate a simple session ID (in production, use secure tokens like JWT)
    import uuid
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = username
    
    print(f"[AUTH] Login successful for user: {username}, session: {session_id[:8]}...")
    return {
        "status": "success",
        "session_id": session_id,
        "username": username,
        "message": f"Welcome, {username}!"
    }

@app.post("/auth/logout")
def logout(request: LogoutRequest):
    """Logout user by removing session"""
    session_id = request.session_id
    if session_id in SESSIONS:
        username = SESSIONS.pop(session_id)
        print(f"[AUTH] User logged out: {username}")
        return {"status": "success", "message": "Logged out successfully"}
    return {"status": "error", "message": "Invalid session"}

@app.post("/auth/verify")
def verify_session(request: VerifySessionRequest):
    """Verify if session is valid"""
    session_id = request.session_id
    if session_id in SESSIONS:
        return {
            "status": "success",
            "username": SESSIONS[session_id],
            "valid": True
        }
    return {
        "status": "error",
        "valid": False,
        "message": "Session expired or invalid"
    }

@app.get("/", response_class=HTMLResponse)
def style():
    """Serve the main application page (style.html)"""
    try:
        # Try to serve index.html (the artifact I created)
        html_file = "index.html"
        if os.path.exists(html_file):
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Inject the API key into the HTML
            content = content.replace(
                'const GEMINI_API_KEY = "AIzaSyAQ89jrJYaN_o5c_TLEQA6lJD1S6rXH6G8";',
                f'const GEMINI_API_KEY = "{GEMINI_API_KEY}";'
            )
            return HTMLResponse(content=content, status_code=200)
        
        # Fallback to style.html if index.html doesn't exist
        with open("style.html", "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>404 - HTML file not found. Please create index.html or style.html</h1>", status_code=404)
    except Exception as e:
        print(f"[ERROR] Exception in index route: {e}")
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"<h1>500 - Server Error: {str(e)}</h1>", status_code=500)


@app.get("/health")
def health_check():
    """Basic health check for server and data status."""
    return {
        "status": "ok", 
        "data_loaded": data_loaded,
        "api_key_loaded": bool(GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE")
    }


@app.get("/api/config")
def get_api_config():
    """Return API configuration for frontend"""
    return {
        "gemini_api_key": GEMINI_API_KEY,
        "gemini_model": "gemini-2.0-flash-exp",
        "api_available": bool(GEMINI_API_KEY),
        "data_loaded": data_loaded
    }


@app.get("/comparison")
def comparison_by_age(age: int):
    """Return comparison of Avg_Daily_Screen_Time_hr and counts per Primary_Device for a given age."""
    if recommend.df is None:
        return {"status": "error", "message": "Data not loaded. Call /load-data first."}

    df = recommend.df
    df_age = df[df['Age'] == age]
    if df_age.empty:
        return {"status": "error", "message": f"No records for age={age}."}

    grouped = df_age.groupby('Primary_Device').agg(
        avg_hours=('Avg_Daily_Screen_Time_hr', 'mean'),
        count=('Avg_Daily_Screen_Time_hr', 'count')
    ).reset_index()

    devices = []
    for _, row in grouped.sort_values('avg_hours', ascending=False).iterrows():
        devices.append({
            'device': row['Primary_Device'],
            'avg_hours': float(round(row['avg_hours'], 2)) if not pd.isna(row['avg_hours']) else None,
            'count': int(row['count'])
        })

    return {"status": "success", "age": age, "devices": devices}


@app.get('/dashboard-data')
def dashboard_data():
    """Return several precomputed aggregations used by the dashboard charts."""
    if recommend.df is None:
        return {"status":"error","message":"Data not loaded. Call /load-data first."}

    df = recommend.df.copy()

    # Average screen time by Age (sorted ascending)
    try:
        avg_by_age = df.groupby('Age').agg(avg_hours=('Avg_Daily_Screen_Time_hr','mean')).reset_index().sort_values('Age')
        avg_by_age_list = [{"age": int(r['Age']), "avg_hours": float(round(r['avg_hours'],2))} for _,r in avg_by_age.iterrows()]
    except Exception:
        avg_by_age_list = []

    # Device share (average hours per Primary_Device)
    try:
        device_share = df.groupby('Primary_Device').agg(avg_hours=('Avg_Daily_Screen_Time_hr','mean'), count=('Avg_Daily_Screen_Time_hr','count')).reset_index()
        device_share_list = [{"device": str(r['Primary_Device']), "avg_hours": float(round(r['avg_hours'],2)), "count": int(r['count'])} for _,r in device_share.sort_values('avg_hours', ascending=False).iterrows()]
    except Exception:
        device_share_list = []

    # Gender distribution counts
    try:
        gender_dist = df.groupby('Gender').size().reset_index(name='count')
        gender_list = [{"gender": str(r['Gender']), "count": int(r['count'])} for _,r in gender_dist.iterrows()]
    except Exception:
        gender_list = []

    # Health impacts counts (if column exists)
    try:
        if 'Health_Impacts' in df.columns:
            health = df.groupby('Health_Impacts').size().reset_index(name='count')
            health_list = [{"health": str(r['Health_Impacts']), "count": int(r['count'])} for _,r in health.iterrows()]
        else:
            health_list = []
    except Exception:
        health_list = []

    return {
        "status":"success",
        "avg_by_age": avg_by_age_list,
        "device_share": device_share_list,
        "gender_distribution": gender_list,
        "health_impacts": health_list
    }


@app.get('/dashboard-insights')
def dashboard_insights():
    """Return detailed insights and metrics for the dashboard"""
    if recommend.df is None:
        return {"status":"error","message":"Data not loaded."}

    df = recommend.df.copy()
    
    insights = {
        "status": "success",
        "summary": {
            "total_children": len(df),
            "avg_screen_time": float(round(df['Avg_Daily_Screen_Time_hr'].mean(), 2)),
            "max_screen_time": float(round(df['Avg_Daily_Screen_Time_hr'].max(), 2)),
            "min_screen_time": float(round(df['Avg_Daily_Screen_Time_hr'].min(), 2)),
            "exceeded_limit_percent": float(round((df['Exceeded_Recommended_Limit'].sum() / len(df)) * 100, 2))
        },
        "age_insights": {},
        "gender_insights": {},
        "device_insights": {},
        "health_insights": {},
        "location_insights": {},
        "education_insights": {}
    }
    
    # Age-based insights
    for age in sorted(df['Age'].unique()):
        age_data = df[df['Age'] == age]
        insights["age_insights"][int(age)] = {
            "count": int(len(age_data)),
            "avg_screen_time": float(round(age_data['Avg_Daily_Screen_Time_hr'].mean(), 2)),
            "percent_exceeded": float(round((age_data['Exceeded_Recommended_Limit'].sum() / len(age_data)) * 100, 2)),
            "top_device": str(age_data['Primary_Device'].mode()[0]) if len(age_data['Primary_Device'].mode()) > 0 else "N/A"
        }
    
    # Gender-based insights
    for gender in df['Gender'].unique():
        gender_data = df[df['Gender'] == gender]
        insights["gender_insights"][str(gender)] = {
            "count": int(len(gender_data)),
            "avg_screen_time": float(round(gender_data['Avg_Daily_Screen_Time_hr'].mean(), 2)),
            "percent_exceeded": float(round((gender_data['Exceeded_Recommended_Limit'].sum() / len(gender_data)) * 100, 2))
        }
    
    # Device-based insights
    for device in df['Primary_Device'].unique():
        device_data = df[df['Primary_Device'] == device]
        insights["device_insights"][str(device)] = {
            "count": int(len(device_data)),
            "avg_screen_time": float(round(device_data['Avg_Daily_Screen_Time_hr'].mean(), 2)),
            "percent_exceeded": float(round((device_data['Exceeded_Recommended_Limit'].sum() / len(device_data)) * 100, 2))
        }
    
    # Health impacts
    health_impact_counts = df['Health_Impacts'].value_counts().to_dict()
    insights["health_insights"] = {str(k): int(v) for k, v in health_impact_counts.items()}
    
    # Location insights
    for location in df['Urban_or_Rural'].unique():
        loc_data = df[df['Urban_or_Rural'] == location]
        insights["location_insights"][str(location)] = {
            "count": int(len(loc_data)),
            "avg_screen_time": float(round(loc_data['Avg_Daily_Screen_Time_hr'].mean(), 2)),
            "percent_exceeded": float(round((loc_data['Exceeded_Recommended_Limit'].sum() / len(loc_data)) * 100, 2))
        }
    
    # Educational ratio insights
    insights["education_insights"] = {
        "avg_edu_ratio": float(round(df['Educational_to_Recreational_Ratio'].mean(), 3)),
        "min_edu_ratio": float(round(df['Educational_to_Recreational_Ratio'].min(), 3)),
        "max_edu_ratio": float(round(df['Educational_to_Recreational_Ratio'].max(), 3))
    }
    
    return insights


@app.post("/api/analyze-user-data")
def analyze_user_data(request_body: dict):
    """Analyze user data against the Indian Kids Screen Time dataset."""
    try:
        print(f"[ANALYZE] Received user data analysis request")
        
        age = request_body.get('age')
        gender = request_body.get('gender', '').lower()
        screen_time = request_body.get('screen_time')
        device = request_body.get('device', '').lower()
        
        print(f"[ANALYZE] User: Age={age}, Gender={gender}, ScreenTime={screen_time}h, Device={device}")
        
        global data_loaded
        if not data_loaded:
            csv_path = "Indian_Kids_Screen_Time.csv"
            if os.path.exists(csv_path):
                try:
                    from recommend import load_and_preprocess_data
                    load_and_preprocess_data(csv_path)
                    data_loaded = True
                except Exception as e:
                    print(f"[ANALYZE] Error loading data: {e}")
                    return {"error": "Cannot load dataset"}
        
        from recommend import get_analysis_insights
        insights = get_analysis_insights(age, gender, screen_time, device)
        
        print(f"[ANALYZE] Generated insights: {insights}")
        
        dataset_context = f"""
Dataset Statistics:
- Avg Screen Time: {insights.get('avg_screen_time', 0)}h
- Avg Screen Time for {age}yo {gender}: {insights.get('age_gender_avg', 0)}h
- Most common device: {insights.get('most_common_device', 'Unknown')}
- {insights.get('exceeds_limit_pct', 0):.1f}% of kids exceed recommended limits
- Most common health impacts: {insights.get('common_health_impacts', 'None')}
"""
        
        return {
            "success": True,
            "insights": insights,
            "dataset_context": dataset_context
        }
    
    except Exception as e:
        print(f"[ANALYZE] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


@app.post("/api/recommend-gemini")
def recommend_gemini_proxy(request_body: dict):
    """Proxy endpoint to call Google Gemini API server-side."""
    import requests
    import time
    
    print(f"[ENDPOINT] Received request at /api/recommend-gemini")
    
    def get_demo_response(reason=""):
        """Return demo response for when API is unavailable"""
        demo_text = """**Health Impact:** Based on your profile, you're showing good digital health awareness.

**Merits:**
• Balanced approach to device usage
• Appropriate screen time for your age group

**Demerits:**
• Potential for longer usage periods without breaks
• May benefit from scheduled offline time

**Further Improvements:**
• Implement the 20-20-20 rule: every 20 minutes, look 20 feet away for 20 seconds
• Create device-free zones during meals and before bedtime
• Schedule outdoor activities daily to balance screen time"""
        
        print(f"[ENDPOINT] Using DEMO response. Reason: {reason}")
        return {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": demo_text
                    }]
                }
            }]
        }
    
    try:
        gemini_api_key = GEMINI_API_KEY
        print(f"[ENDPOINT] API key status: {'LOADED' if gemini_api_key else 'NOT SET'}")
        
        if not gemini_api_key or gemini_api_key == "YOUR_GEMINI_API_KEY_HERE":
            return get_demo_response("No valid API key")
        
        gemini_model = "gemini-2.0-flash-exp"
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{gemini_model}:generateContent?key={gemini_api_key}"
        
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"[ENDPOINT] Making Gemini API request (attempt {retry_count + 1}/{max_retries})...")
                response = requests.post(api_url, json=request_body, timeout=30)
                
                if response.status_code == 200:
                    print(f"[ENDPOINT] ✅ Gemini API success on attempt {retry_count + 1}")
                    return response.json()
                
                if response.status_code == 429:
                    print(f"[ENDPOINT] ⚠️ Rate limit (429). Waiting before retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
                    if retry_count < max_retries:
                        # Exponential backoff: 5, 10, 20, 40, 80 seconds
                        wait_time = 5 * (2 ** (retry_count - 1))
                        print(f"[ENDPOINT] Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[ENDPOINT] Max retries exceeded. Using demo response.")
                        return get_demo_response("Rate limit exceeded after retries")
                
                if response.status_code in [500, 502, 503, 504]:
                    print(f"[ENDPOINT] Server error ({response.status_code}). Retry {retry_count + 1}/{max_retries}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(3 * retry_count)
                        continue
                    else:
                        return get_demo_response(f"Server error {response.status_code}")
                
                print(f"[ENDPOINT] API error: {response.status_code}")
                return get_demo_response(f"API error {response.status_code}")
            
            except requests.exceptions.Timeout:
                print(f"[ENDPOINT] Timeout on attempt {retry_count + 1}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2 * retry_count)
                    continue
                return get_demo_response("Timeout after retries")
            except requests.exceptions.ConnectionError as ce:
                print(f"[ENDPOINT] Connection error: {str(ce)}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2 * retry_count)
                    continue
                return get_demo_response("Connection error after retries")
        
    except Exception as e:
        print(f"[ENDPOINT ERROR]: {str(e)}")
        import traceback
        traceback.print_exc()
        return get_demo_response("Exception occurred")


@app.post("/api/save-feedback")
def save_feedback(feedback_data: dict):
    """Save user feedback to a JSON file"""
    try:
        print(f"[FEEDBACK] Received feedback: {feedback_data}")
        
        import json
        feedback_file = "feedback_responses.json"
        
        if os.path.exists(feedback_file):
            with open(feedback_file, 'r', encoding='utf-8') as f:
                try:
                    feedback_list = json.load(f)
                except:
                    feedback_list = []
        else:
            feedback_list = []
        
        feedback_entry = {
            **feedback_data,
            "timestamp": pd.Timestamp.now().isoformat()
        }
        feedback_list.append(feedback_entry)
        
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_list, f, indent=2)
        
        print(f"[FEEDBACK] Saved. Total: {len(feedback_list)}")
        return {
            "status": "success",
            "message": "Feedback saved successfully",
            "total_feedback_count": len(feedback_list)
        }
    
    except Exception as e:
        print(f"[FEEDBACK] Error: {e}")
        return {
            "status": "error",
            "message": f"Error saving feedback: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Check if port is specified in command line arguments
    port = 3000  # Default port
    if len(sys.argv) > 1 and sys.argv[1].startswith('--port='):
        try:
            port = int(sys.argv[1].split('=')[1])
        except:
            port = 3000
    
    print("\n" + "="*60)
    print("🚀 Starting Screen Time Advisor API Server")
    print("="*60)
    print(f"📍 Server will run at: http://localhost:{port}")
    print(f"📊 API Docs available at: http://localhost:{port}/docs")
    print(f"🔑 API Key loaded: {bool(GEMINI_API_KEY)}")
    print(f"📁 Data loaded: {data_loaded}")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
