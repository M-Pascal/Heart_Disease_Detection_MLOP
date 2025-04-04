import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import joblib
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data(file_path):
    """Load data from different file formats"""
    try:
        # Convert Path object to string if needed
        file_path_str = str(file_path)
        
        if file_path_str.endswith('.csv'):
            df = pd.read_csv(file_path_str)
        elif file_path_str.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path_str)
        elif file_path_str.endswith('.json'):
            df = pd.read_json(file_path_str)
        else:
            raise ValueError("Unsupported file format. Please upload CSV, Excel, or JSON.")
        
        logger.info(f"Successfully loaded data with shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def validate_data(df):
    """Validate the dataset structure"""
    required_columns = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
        'restecg', 'thalach', 'exang', 'oldpeak', 
        'slope', 'ca', 'thal', 'target'
    ]
    
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    
    return True

def preprocess_data(file_path):
    """
    Preprocesses the heart disease dataset
    """
    try:
        # Load the data
        df = load_data(file_path)
        validate_data(df)
        
        # Separate features and target
        X = df.drop('target', axis=1)
        y = df['target']
        
        # Define numeric and categorical features
        numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
        categorical_features = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        
        # Numeric preprocessing pipeline
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Apply numeric preprocessing
        X[numeric_features] = numeric_transformer.fit_transform(X[numeric_features])
        
        # Handle label encoders
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        label_encoders_path = models_dir / 'label_encoders.pkl'
        
        if label_encoders_path.exists():
            label_encoders = joblib.load(label_encoders_path)
        else:
            label_encoders = {}
        
        # Apply categorical encoding
        for col in categorical_features:
            if col in X.columns:
                if col not in label_encoders:
                    label_encoders[col] = LabelEncoder().fit(X[col])
                X[col] = label_encoders[col].transform(X[col])
        
        # Save label encoders if they were updated
        joblib.dump(label_encoders, label_encoders_path)
        
        logger.info("Data preprocessing completed successfully")
        return X, y
        
    except Exception as e:
        logger.error(f"Error during preprocessing: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        X, y = preprocess_data('sample_heart_data.csv')
        print("Preprocessing completed successfully!")
        print(f"Processed features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")