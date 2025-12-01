from fastapi import FastAPI
from pydantic import BaseModel
from backend.Codefiles.datavalidation import Validator
from backend.recommendationengine.enginefile import recommendation


app=FastAPI()

@app.get('/')
def Hello():
    return {'message':'Welcome to the Recommendation System'}

@app.post('/Recommendations')
def recommender(payload:Validator):
    data=payload.model_dump()       # Changing payload into a dictionary
    age = data["age"]
    gender = data["gender"]
    device = data["device"]
    edu_time = data["edu_time"]
    rec_time = data["rec_time"]
    
    result=recommendation(age,gender,device,edu_time,rec_time)
    
    return {'Result':result}

    