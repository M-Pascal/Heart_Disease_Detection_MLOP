from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import joblib
from pathlib import Path
from model import train_model
from preprocess import preprocess_data
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# FastAPI endpoint
FASTAPI_URL = "http://localhost:8000"  # Update if different

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form')
def show_form():
    return render_template('form.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = {  # Prepare data for FastAPI
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
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['dataset']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                X, y = preprocess_data(filepath)  # Preprocess data
                model, accuracy = train_model(filepath)  # Train the model
                
                categorical_cols = ['sex', 'chest_pain_type', 'fasting_blood_sugar',
                                  'resting_electrocardiogram', 'exercise_induced_angina',
                                  'st_slope', 'thalassemia']
                
                label_encoders = {}
                df = pd.read_csv(filepath)  # Load dataset
                for col in categorical_cols:
                    if col in df.columns:
                        le = LabelEncoder()
                        le.fit(df[col])
                        label_encoders[col] = le
                
                os.makedirs('models', exist_ok=True)
                joblib.dump(label_encoders, 'models/label_encoders.pkl')
                
                flash(f'Model retrained successfully! Accuracy: {accuracy:.2%}', 'success')
                return redirect(url_for('retrain'))
                
            except Exception as e:
                flash(f'Error during retraining: {str(e)}', 'error')
                return redirect(request.url)
    
    return render_template('retrain.html')

if __name__ == '__main__':
    app.run(debug=True)
