from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to maintain compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model path
MODEL_PATH = os.path.join(Path(__file__).parent.parent, "models", "random_forest.pkl")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model: {e}")

class PredictionInput(BaseModel):
    age: int
    sex: int 
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int

@app.post("/predict")
async def predict(input_data: PredictionInput):
    try:
        input_array = np.array([[
            input_data.age, input_data.sex, input_data.cp,
            input_data.trestbps, input_data.chol, input_data.fbs,
            input_data.restecg, input_data.thalach, input_data.exang,
            input_data.oldpeak, input_data.slope, input_data.ca,
            input_data.thal
        ]])

        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(input_array)[0][1]
        else:
            probability = None

        prediction = model.predict(input_array)[0]

        response = {
            "result": int(prediction),
            "probability": float(probability) if probability is not None else None,
            "message": ""
        }

        if prediction == 1:
            response["message"] = "Potential heart disease risk detected" if probability <= 0.6 else "High heart disease risk detected"
        else:
            response["message"] = "Low risk of heart disease" if probability >= 0.4 else "Very low risk of heart disease"

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))