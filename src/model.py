import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
import numpy as np
import joblib
import os
from preprocess import preprocess_data
from sklearn.metrics import accuracy_score

def train_model(file_path):
    """
    Trains a neural network model and returns the model with test accuracy
    """
    # Preprocess the data
    X, y = preprocess_data(file_path)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    
    # Convert sparse matrices if needed
    if hasattr(X_train, 'toarray'):
        X_train = X_train.toarray()
        X_test = X_test.toarray()
    
    # Model architecture
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam',
                 loss='binary_crossentropy',
                 metrics=['accuracy'])
    
    # Train model
    history = model.fit(X_train, y_train,
              epochs=50,
              batch_size=32,
              validation_data=(X_test, y_test),
              verbose=0)
    
    # Calculate accuracy
    y_pred = (model.predict(X_test) > 0.5).astype(int)
    accuracy = accuracy_score(y_test, y_pred)
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model.save('models/heart_disease_model.keras')
    
    # Save training history for visualization
    joblib.dump(history.history, 'models/training_history.pkl')
    
    return model, accuracy
