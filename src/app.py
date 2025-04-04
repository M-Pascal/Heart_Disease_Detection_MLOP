from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import os
import pandas as pd
import requests
import joblib
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from dotenv import load_dotenv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Flask app with correct template and static folders
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
            static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'))
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# CORS configuration
CORS(app)

# Import database functions after app creation
from .database import (
    save_to_database,
    ensure_table_exists,
    get_db_connection,
    count_records
)

# Import model functions
from .model import train_model
from .preprocess import preprocess_data

# Initialize database table
ensure_table_exists()

# FastAPI endpoint
FASTAPI_URL = os.getenv('FASTAPI_URL', 'http://127.0.0.1:8000')

@app.route('/')
def index():
    """Home page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index: {str(e)}")
        return str(e), 500

@app.route('/form')
def show_form():
    """Prediction form page"""
    return render_template('form.html')

@app.route('/visualize')
def visualize():
    """Data visualization page"""
    try:
        record_count = count_records()
        return render_template('visualization.html', record_count=record_count)
    except Exception as e:
        logger.error(f"Visualization error: {str(e)}")
        flash("Error loading visualization data", "error")
        return redirect(url_for('index'))

@app.route('/retrain-page')
def retrain_page():
    """Retrain model page"""
    return render_template('retrain.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests"""
    try:
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

        response = requests.post(
            f"{FASTAPI_URL}/predict",
            json=data,
            timeout=10
        )
        response.raise_for_status()

        result = response.json()
        flash(result.get('message', 'Prediction completed'), 'success')
        return jsonify(result)

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/retrain', methods=['GET', 'POST', 'OPTIONS'])
def retrain():
    """Handle model retraining requests"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'success'}), 200
        
    if request.method == 'GET':
        return render_template('retrain.html')
        
    try:
        if 'dataset' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['dataset']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Create temp directory
        temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True, parents=True)
        file_path = temp_dir / file.filename
        
        try:
            file.save(str(file_path))
            
            # Process dataset
            df = pd.read_csv(str(file_path)) if file.filename.lower().endswith('.csv') else \
                 pd.read_excel(str(file_path)) if file.filename.lower().endswith(('.xlsx', '.xls')) else \
                 pd.read_json(str(file_path))
            
            required_columns = [
                'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
                'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
            ]
            
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                return jsonify({
                    'error': f'Missing required columns: {", ".join(missing)}'
                }), 400
            
            # Save and retrain
            save_to_database(df)
            model, metrics = train_model(str(file_path))
            
            return jsonify({
                'status': 'success',
                'message': 'Model retrained successfully',
                'metrics': {
                    'accuracy': f"{metrics['accuracy']:.2%}",
                    'precision': f"{metrics['precision']:.2%}",
                    'recall': f"{metrics['recall']:.2%}",
                    'f1_score': f"{metrics['f1_score']:.2%}"
                },
                'records_used': len(df)
            })
            
        finally:
            if file_path.exists():
                file_path.unlink()
                
    except Exception as e:
        logger.error(f"Retrain failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return jsonify({'status': 'healthy'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)