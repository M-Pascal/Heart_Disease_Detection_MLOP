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

# Model path - updated to match your structure
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

        # Prediction logic
        if hasattr(model, "predict_proba"):  
            probabilities = model.predict_proba(input_array)
            probability = probabilities[0][1]
        else:
            probability = None

        prediction = model.predict(input_array)[0]

        # Response format (matches what Flask app expects)
        response = {
            "prediction": int(prediction),
            "probability": probability if probability is not None else "Not available",
            "message": ""
        }

        if prediction == 1:
            if probability is not None and probability > 0.6:
                response["message"] = "High risk! Urgent medical consultation needed."
            else:
                response["message"] = "You are more likely to get heart disease. Consult a doctor."
        else:
            if probability is not None and probability < 0.4:
                response["message"] = "You seem very healthy. Keep maintaining your lifestyle!"
            else:
                response["message"] = "Low risk of heart disease, but consider regular checkups."

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))