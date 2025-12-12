from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from myenv.Codefiles.datavalidation import Validator
from myenv.recommendationengine.enginefile import recommendation  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def Hello():
    return {"message": "Welcome to the Recommendation System"}

@app.post("/Recommendations")
def recommender(payload: Validator):
    data = payload.model_dump()
    result = recommendation(
        data["age"],
        data["gender"],
        data["device"],
        data["edu_time"],
        data["rec_time"],
    )
    return {"Result": result}