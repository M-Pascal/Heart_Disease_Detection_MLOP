# preprocess.py
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
import joblib
import os

def preprocess_data(file_path):
    """
    Preprocesses the heart disease dataset with the original column names
    """
    # Load the data
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload CSV, Excel, or JSON.")
    
    # Ensure we have the target column
    if 'target' not in df.columns:
        raise ValueError("Dataset must contain a 'target' column")
    
    # Separate features and target
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Define numeric features (using original column names)
    numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
    
    # Imputation and Scaling for numeric data
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Apply numeric preprocessing
    X[numeric_features] = numeric_transformer.fit_transform(X[numeric_features])

    # Load or create label encoders
    label_encoders_path = "models/label_encoders.pkl"
    if os.path.exists(label_encoders_path):
        label_encoders = joblib.load(label_encoders_path)
    else:
        label_encoders = {}
        categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
        for col in categorical_cols:
            if col in X.columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col])
                label_encoders[col] = le
        os.makedirs('models', exist_ok=True)
        joblib.dump(label_encoders, label_encoders_path)
    
    # Apply categorical encoding
    for col, le in label_encoders.items():
        if col in X.columns:
            X[col] = le.transform(X[col])
    
    return X, y

if __name__ == '__main__':
    try:
        X, y = preprocess_data('sample_heart_data.csv')
        print("Preprocessing completed successfully!")
        print(f"Processed features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
    except Exception as e:
        print(f"Error during preprocessing: {str(e)}")
