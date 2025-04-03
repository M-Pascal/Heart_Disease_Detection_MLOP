from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import requests
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
import logging
from datetime import datetime

# Local imports
from .model import train_model
from .preprocess import preprocess_data
from .database import (
    clear_existing_data, 
    save_to_database, 
    load_from_database, 
    ensure_table_exists,
    count_records
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Initialize database table
ensure_table_exists()

# FastAPI endpoint - should be in your environment variables
FASTAPI_URL = os.getenv('FASTAPI_URL', 'https://heart-disease-detection-mlop.onrender.com')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def show_form():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Convert form data with proper error handling
        data = {
            "age": int(float(request.form['age'])),
            "sex": int(float(request.form['sex'])),
            "cp": int(float(request.form['cp'])),
            "trestbps": int(float(request.form['trestbps'])),
            "chol": int(float(request.form['chol'])),
            "fbs": int(float(request.form['fbs'])),
            "restecg": int(float(request.form['restecg'])),
            "thalach": int(float(request.form['thalach'])),
            "exang": int(float(request.form['exang'])),
            "oldpeak": float(request.form['oldpeak']),
            "slope": int(float(request.form['slope'])),
            "ca": int(float(request.form['ca'])),
            "thal": int(float(request.form['thal']))
        }
        
        logger.info(f"Sending prediction request: {data}")
        
        response = requests.post(
            f"{FASTAPI_URL}/predict",
            json=data,
            timeout=10  # 10 seconds timeout
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Received prediction result: {result}")
        return jsonify(result)
        
    except ValueError as e:
        logger.error(f"Invalid input format: {str(e)}")
        return jsonify({
            "error": "Invalid input format",
            "details": "All fields must be numbers",
            "received_data": dict(request.form)
        }), 400
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return jsonify({
            "error": "Prediction service unavailable",
            "details": str(e)
        }), 502
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

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
            file_extension = file.filename.split('.')[-1].lower()
            
            if file_extension == 'csv':
                df = pd.read_csv(file)
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(file)
            elif file_extension == 'json':
                df = pd.read_json(file)
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Unsupported file format. Please upload CSV, Excel, or JSON.'
                })
            
            # Verify required columns exist
            required_columns = [
                'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                'restecg', 'thalach', 'exang', 'oldpeak', 
                'slope', 'ca', 'thal', 'target'
            ]
            
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required columns: {", ".join(missing)}'
                })
            
            # Save data to database
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
            
            # Save to temporary file for preprocessing
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
                    'records_used': record_count,
                    'timestamp': datetime.now().isoformat()
                })
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            logger.error(f"Error during retraining: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Error during retraining: {str(e)}'
            })
    
    # For GET requests, show current dataset info
    record_count = count_records()
    return render_template('retrain.html', record_count=record_count)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "False") == "True")