from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import UserInput, AnalysisResponse
from recommendation_system import ScreenTimeRecommendationSystem
import os

app = FastAPI(title="Screen Time Recommendation API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommendation system
csv_path = os.path.join(os.path.dirname(__file__), "data", "Indian_Kids_Screen_Time_Processed.csv")
rec_system = ScreenTimeRecommendationSystem(csv_path=csv_path)

@app.get("/")
def health_check():
    return {"message": "Screen Time Recommendation API is running", "status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_screen_time(user_input: UserInput):
    """
    Analyze user screen time and provide recommendations
    """
    try:
        # Calculate total screen time
        screen_time = user_input.educational_hours + user_input.recreational_hours
        
        # Calculate edu/rec ratio
        if user_input.recreational_hours > 0:
            edu_rec_ratio = user_input.educational_hours / user_input.recreational_hours
        else:
            edu_rec_ratio = user_input.educational_hours
        
        # Analyze using recommendation system
        analysis = rec_system.analyze_user_input(
            age=user_input.age,
            gender=user_input.gender,
            device=user_input.device,
            location=user_input.location,
            screen_time=screen_time
        )
        
        # Add additional fields
        analysis['educational_hours'] = user_input.educational_hours
        analysis['recreational_hours'] = user_input.recreational_hours
        analysis['edu_rec_ratio'] = edu_rec_ratio
        analysis['health_impacts'] = user_input.health_impacts
        
        # Generate recommendations
        recommendations = rec_system.generate_recommendations(analysis)
        analysis['recommendations'] = recommendations
        
        # Generate charts (NEW)
        analysis['comparison_chart'] = rec_system.generate_comparison_chart(analysis)
        analysis['dashboard_chart'] = rec_system.generate_dashboard_chart(analysis)
        
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
def get_statistics():
    """Get overall statistics from the dataset"""
    return rec_system.get_statistics()
