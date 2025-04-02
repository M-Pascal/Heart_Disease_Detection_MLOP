from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import pandas as pd
import requests
import joblib
from pathlib import Path
from model import train_model
from preprocess import preprocess_data
from sklearn.preprocessing import LabelEncoder
from database import (
    clear_existing_data, 
    save_to_database, 
    load_from_database, 
    ensure_table_exists,
    count_records
)
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Initialize database table
ensure_table_exists()

# FastAPI endpoint
FASTAPI_URL = "http://localhost:8000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def show_form():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = {
            "age": int(request.form['age']),
            "sex": int(request.form['sex']),
            "cp": int(request.form['cp']),
            "trestbps": int(request.form['trestbps']),
            "chol": int(request.form['chol']),
            "fbs": int(request.form['fbs']),
            "restecg": int(request.form['restecg']),
            "thalach": int(request.form['thalach']),
            "exang": int(request.form['exang']),
            "oldpeak": float(request.form['oldpeak']),
            "slope": int(request.form['slope']),
            "ca": int(request.form['ca']),
            "thal": int(request.form['thal'])
        }
        response = requests.post(f"{FASTAPI_URL}/predict", json=data)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/visualize')
def visualize():
    return render_template('visualization.html')

@app.route('/retrain', methods=['GET', 'POST'])
def retrain():
    if request.method == 'POST':
        if 'dataset' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})
        
        file = request.files['dataset']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})
        
        try:
            # Read the uploaded file
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.filename.endswith('.json'):
                df = pd.read_json(file)
            else:
                return jsonify({'status': 'error', 'message': 'Unsupported file format'})
            
            # Verify required columns exist
            required_columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                              'restecg', 'thalach', 'exang', 'oldpeak', 
                              'slope', 'ca', 'thal', 'target']
            
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required columns: {", ".join(missing)}'
                })
            
            # Save data to database (this will clear existing data first)
            save_to_database(df)
            
            # Verify data was saved
            record_count = count_records()
            if record_count == 0:
                return jsonify({
                    'status': 'error',
                    'message': 'No data was saved to database'
                })
            
            # Load data from database and train model
            df = load_from_database()
            
            # Save to temporary CSV for preprocessing
            temp_path = 'temp_dataset.csv'
            df.to_csv(temp_path, index=False)
            
            try:
                # Preprocess and train
                X, y = preprocess_data(temp_path)
                model, accuracy = train_model(temp_path)
                
                # Save label encoders
                categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
                label_encoders = {}
                for col in categorical_cols:
                    le = LabelEncoder()
                    le.fit(df[col])
                    label_encoders[col] = le
                
                os.makedirs('models', exist_ok=True)
                joblib.dump(label_encoders, 'models/label_encoders.pkl')
                
                accuracy_percent = f"{accuracy:.2%}"
                return jsonify({
                    'status': 'success',
                    'message': 'Model retrained successfully!',
                    'accuracy': accuracy_percent,
                    'records_used': record_count
                })
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error during retraining: {str(e)}'
            })
    
    # For GET requests, show current dataset info
    record_count = count_records()
    return render_template('retrain.html', record_count=record_count)

if __name__ == '__main__':
    app.run(debug=True)