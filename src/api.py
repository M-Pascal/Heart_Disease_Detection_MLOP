from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
from pathlib import Path
import os

app = FastAPI()

# Correctly load the Random Forest model
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

        # Ensure the input is scaled correctly
        if hasattr(model, "predict_proba"):  
            probabilities = model.predict_proba(input_array)
            probability_of_heart_disease = probabilities[0][1]  # Probability of class 1 (heart disease)
        else:
            probability_of_heart_disease = None  # Some models don't have probabilities

        # Make prediction
        prediction = model.predict(input_array)[0]

        # Generate a more detailed response
        response = {
            "prediction": int(prediction),
            "probability": probability_of_heart_disease if probability_of_heart_disease is not None else "Not available",
            "message": ""
        }

        if prediction == 1:
            if probability_of_heart_disease is not None and probability_of_heart_disease > 0.6:
                response["message"] = "High risk! Urgent medical consultation needed."
            else:
                response["message"] = "You are more likely to get heart disease. Consult a doctor."
        else:
            if probability_of_heart_disease is not None and probability_of_heart_disease < 0.4:
                response["message"] = "You seem very healthy. Keep maintaining your lifestyle!"
            else:
                response["message"] = "Low risk of heart disease, but consider regular checkups."

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
