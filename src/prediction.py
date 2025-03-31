import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import os

class HeartDiseasePredictor:
    def __init__(self, model_type="keras"):
        """
        Initialize the predictor with the model and encoders.
        
        Args:
            model_type (str): The type of model to load ("keras" or "pkl").
        """
        self.model_type = model_type
        self.model_path = f"models/heart_disease_model.{model_type}"
        self.label_encoders = joblib.load("models/label_encoders.pkl")

        if model_type == "keras":
            self.model = load_model(self.model_path)
        elif model_type == "pkl":
            self.model = joblib.load(self.model_path)
        else:
            raise ValueError("Invalid model type. Choose 'keras' or 'pkl'.")

    def preprocess_input(self, input_data):
        """
        Preprocess the input data using the saved encoders.
        
        Args:
            input_data: Dictionary or DataFrame of input features.
            
        Returns:
            numpy.ndarray: Preprocessed features.
        """
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data])
        else:
            input_df = input_data.copy()
        
        # Apply label encoding to categorical features
        for col, le in self.label_encoders.items():
            if col in input_df.columns:
                input_df[col] = le.transform(input_df[col])
        
        return input_df.values

    def predict(self, input_data):
        """
        Make a prediction on the input data.
        
        Args:
            input_data: Dictionary or DataFrame of input features.
            
        Returns:
            dict: Prediction result with probability.
        """
        processed_data = self.preprocess_input(input_data)
        probability = float(self.model.predict(processed_data)[0][0])
        prediction = int(probability > 0.5)
        
        return {
            'prediction': prediction,
            'probability': probability,
            'message': 'High risk of heart disease' if prediction == 1 
                      else 'Low risk of heart disease'
        }

if __name__ == '__main__':
    predictor = HeartDiseasePredictor(model_type="keras")
    sample_input = {'age': 58, 'sex': 'male', 'chest_pain_type': 'atypical angina',
                    'resting_blood_pressure': 140, 'cholesterol': 289,
                    'fasting_blood_sugar': 'lower than 120mg/ml',
                    'resting_electrocardiogram': 'normal', 'max_heart_rate_achieved': 172, 
                    'exercise_induced_angina': 'no', 'st_depression': 0.0, 'st_slope': 'upsloping',
                    'num_major_vessels': 0, 'thalassemia': 'normal'}
    print(predictor.predict(sample_input))
