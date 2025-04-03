import tensorflow as tf
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
import numpy as np
import joblib
import os
import logging
from datetime import datetime
from .preprocess import preprocess_data
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_model(input_shape):
    """Create the neural network model architecture"""
    model = Sequential([
        Dense(64, activation='relu', input_shape=(input_shape,)),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    
    return model

def train_model(file_path):
    """
    Trains a neural network model and returns the model with test accuracy
    """
    try:
        logger.info(f"Starting model training with file: {file_path}")
        
        # Preprocess the data
        X, y = preprocess_data(file_path)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)
        
        # Convert sparse matrices if needed
        if hasattr(X_train, 'toarray'):
            X_train = X_train.toarray()
            X_test = X_test.toarray()
        
        # Create and train model
        model = create_model(X_train.shape[1])
        
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        history = model.fit(
            X_train, y_train,
            epochs=100,
            batch_size=32,
            validation_data=(X_test, y_test),
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Evaluate model
        y_pred = (model.predict(X_test) > 0.5).astype(int)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'training_time': datetime.now().isoformat()
        }
        
        # Save model and metrics
        os.makedirs('models', exist_ok=True)
        save_model(model, 'models/heart_disease_model.keras')
        joblib.dump(metrics, 'models/model_metrics.pkl')
        joblib.dump(history.history, 'models/training_history.pkl')
        
        logger.info(f"Model training completed with accuracy: {accuracy:.2%}")
        return model, accuracy
        
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise