import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import logging
from pathlib import Path
from typing import Union, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeartDiseasePredictor:
    def __init__(self, model_type: str = "keras"):
        """
        Initialize the predictor with the model and encoders.
        
        Args:
            model_type: The type of model to load ("keras" or "pkl").
        """
        try:
            self.model_type = model_type.lower()
            self.models_dir = Path('models')
            
            # Validate model type
            if self.model_type not in ['keras', 'pkl']:
                raise ValueError("Invalid model type. Choose 'keras' or 'pkl'.")
            
            # Load label encoders
            label_encoders_path = self.models_dir / 'label_encoders.pkl'
            if not label_encoders_path.exists():
                raise FileNotFoundError(f"Label encoders not found at {label_encoders_path}")
            self.label_encoders = joblib.load(label_encoders_path)
            
            # Load model
            model_path = self.models_dir / f'heart_disease_model.{self.model_type}'
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at {model_path}")
            
            if self.model_type == "keras":
                self.model = load_model(model_path)
            else:
                self.model = joblib.load(model_path)
            
            logger.info("Predictor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing predictor: {str(e)}")
            raise

    def preprocess_input(self, input_data: Union[Dict, pd.DataFrame]) -> np.ndarray:
        """
        Preprocess the input data using the saved encoders.
        
        Args:
            input_data: Dictionary or DataFrame of input features.
            
        Returns:
            Preprocessed features as numpy array.
        """
        try:
            if isinstance(input_data, dict):
                input_df = pd.DataFrame([input_data])
            else:
                input_df = input_data.copy()
            
            # Apply label encoding to categorical features
            for col, le in self.label_encoders.items():
                if col in input_df.columns:
                    input_df[col] = le.transform(input_df[col])
            
            # Ensure all required columns are present
            required_cols = list(self.label_encoders.keys()) + [
                'age', 'trestbps', 'chol', 'thalach', 'oldpeak'
            ]
            
            if not all(col in input_df.columns for col in required_cols):
                missing = [col for col in required_cols if col not in input_df.columns]
                raise ValueError(f"Missing required columns: {', '.join(missing)}")
            
            return input_df[required_cols].values
            
        except Exception as e:
            logger.error(f"Error preprocessing input: {str(e)}")
            raise

    def predict(self, input_data: Union[Dict, pd.DataFrame]) -> Dict:
        """
        Make a prediction on the input data.
        
        Args:
            input_data: Dictionary or DataFrame of input features.
            
        Returns:
            Dictionary with prediction results.
        """
        try:
            processed_data = self.preprocess_input(input_data)
            
            # Get prediction and probability
            if hasattr(self.model, "predict_proba"):
                probability = float(self.model.predict_proba(processed_data)[0][1])
            else:
                probability = float(self.model.predict(processed_data)[0][0])
            
            prediction = int(probability > 0.5)
            
            # Generate appropriate message
            if prediction == 1:
                if probability > 0.7:
                    message = "High risk! Urgent medical consultation recommended."
                elif probability > 0.5:
                    message = "Moderate risk of heart disease. Consult a doctor."
                else:
                    message = "Slight risk of heart disease. Consider lifestyle changes."
            else:
                if probability < 0.3:
                    message = "Low risk. Maintain your healthy lifestyle!"
                else:
                    message = "Very low risk, but regular checkups are still important."
            
            result = {
                'prediction': prediction,
                'probability': probability,
                'message': message,
                'status': 'success'
            }
            
            logger.info(f"Prediction result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

if __name__ == '__main__':
    try:
        predictor = HeartDiseasePredictor(model_type="keras")
        sample_input = {
            'age': 58, 'sex': 1, 'cp': 0,
            'trestbps': 140, 'chol': 289, 'fbs': 0,
            'restecg': 0, 'thalach': 172, 'exang': 0,
            'oldpeak': 0.0, 'slope': 1, 'ca': 0, 'thal': 1
        }
        print(predictor.predict(sample_input))
    except Exception as e:
        print(f"Error: {str(e)}")