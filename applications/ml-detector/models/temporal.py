"""
Temporal anomaly detection using Variational Autoencoders.

This module implements VAE-based sequential analysis for detecting
anomalies in time-series patterns.
"""
import logging
import numpy as np
from collections import deque
from typing import Deque, Optional
# Lazy import for faster startup
tf = None
keras = None

def _ensure_tensorflow():
    """Load TensorFlow only when needed for faster startup."""
    global tf, keras
    if tf is None:
        import tensorflow as _tf
        from tensorflow import keras as _keras
        tf = _tf
        keras = _keras

from .base import BaseDetectionModel
from constants import VAE_CONFIG, WINDOW_SIZES

logger = logging.getLogger(__name__)


class TemporalAnomalyDetector(BaseDetectionModel):
    """VAE-based temporal anomaly detection (Rakuten Symphony approach)."""
    
    def __init__(self):
        self.sequence_length = VAE_CONFIG["sequence_length"]
        self.vae: Optional[keras.Model] = None
        self._is_trained = False
        
        # Sequence management
        self.current_sequence: Deque[np.ndarray] = deque(maxlen=self.sequence_length)
        self.time_series_window: Deque[np.ndarray] = deque(maxlen=WINDOW_SIZES["time_series"])
    
    def add_sample(self, features: np.ndarray) -> None:
        """Add a new sample to the current sequence."""
        self.current_sequence.append(features[0])
        
        # When sequence is complete, add to time series window
        if len(self.current_sequence) == self.sequence_length:
            self.time_series_window.append(np.array(list(self.current_sequence)))
    
    def fit(self, data: np.ndarray) -> None:
        """Train VAE on sequential data."""
        try:
            if len(self.time_series_window) < 50:
                logger.warning("Insufficient sequences for VAE training")
                return
            
            # Load TensorFlow only when actually needed
            _ensure_tensorflow()
            
            # Build VAE if not exists
            if self.vae is None:
                input_dim = len(data[0])
                self.vae = self._build_vae(input_dim)
            
            # Prepare training sequences
            sequences = list(self.time_series_window)[-200:]
            X_train = np.array(sequences)
            
            # Validate shapes before training
            if len(X_train.shape) != 3:
                logger.error(f"Invalid X_train shape: {X_train.shape}, expected 3D")
                return
                
            logger.info(f"Training VAE with shape: {X_train.shape}")
            
            # Train VAE with smaller batch size to avoid memory issues
            batch_size = min(VAE_CONFIG["batch_size"], len(X_train) // 4)
            self.vae.fit(X_train, X_train, 
                        epochs=VAE_CONFIG["epochs"], 
                        batch_size=max(1, batch_size), 
                        verbose=0)
            self._is_trained = True
            
            logger.info(f"VAE trained on {len(sequences)} sequences")
            
        except Exception as e:
            logger.error(f"VAE training error: {e}")
    
    def predict(self, features: np.ndarray) -> float:
        """Predict anomaly score using VAE reconstruction error."""
        if not self._is_trained or self.vae is None:
            return 0.0
        
        try:
            _ensure_tensorflow()
            # Need full sequence for prediction
            if len(self.current_sequence) < self.sequence_length:
                return 0.0
            
            # Prepare sequence for VAE
            sequence = np.array([list(self.current_sequence)])
            
            # Get reconstruction
            reconstruction = self.vae.predict(sequence, verbose=0)
            
            # Calculate reconstruction error (MSE)
            mse = np.mean(np.square(sequence - reconstruction))
            
            # Normalize to 0-1 range
            anomaly_score = min(mse / 0.1, 1.0)
            
            return float(anomaly_score)
            
        except Exception as e:
            logger.warning(f"VAE prediction error: {e}")
            return 0.0
    
    def is_trained(self) -> bool:
        """Check if VAE is trained and ready."""
        return self._is_trained
    
    def save(self, path: str) -> None:
        """Save VAE model."""
        try:
            if self.vae is not None:
                self.vae.save(f"{path}/vae_model")
                logger.info("Temporal VAE model saved successfully")
        except Exception as e:
            logger.error(f"Error saving VAE model: {e}")
    
    def load(self, path: str) -> bool:
        """Load VAE model."""
        try:
            import os
            if not os.path.exists(f"{path}/vae_model"):
                return False
            
            _ensure_tensorflow()
            self.vae = keras.models.load_model(f"{path}/vae_model")
            self._is_trained = True
            
            logger.info("Temporal VAE model loaded successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Could not load VAE model: {e}")
            return False
    
    def _build_vae(self, input_dim: int):
        """Build Variational Autoencoder architecture."""
        _ensure_tensorflow()
        # Encoder
        encoder_inputs = keras.Input(shape=(self.sequence_length, input_dim))
        x = keras.layers.LSTM(VAE_CONFIG["lstm_units"][0], return_sequences=True)(encoder_inputs)
        x = keras.layers.LSTM(VAE_CONFIG["lstm_units"][1], return_sequences=False)(x)
        z_mean = keras.layers.Dense(VAE_CONFIG["latent_dim"])(x)
        z_log_var = keras.layers.Dense(VAE_CONFIG["latent_dim"])(x)
        
        # Sampling layer
        def sampling(args):
            z_mean, z_log_var = args
            batch = tf.shape(z_mean)[0]
            dim = tf.shape(z_mean)[1]
            epsilon = tf.random.normal(shape=(batch, dim))
            return z_mean + tf.exp(0.5 * z_log_var) * epsilon
        
        z = keras.layers.Lambda(sampling, output_shape=(VAE_CONFIG["latent_dim"],))([z_mean, z_log_var])
        
        # Decoder
        decoder_input = keras.layers.RepeatVector(self.sequence_length)(z)
        x = keras.layers.LSTM(VAE_CONFIG["lstm_units"][1], return_sequences=True)(decoder_input)
        x = keras.layers.LSTM(VAE_CONFIG["lstm_units"][0], return_sequences=True)(x)
        decoder_outputs = keras.layers.TimeDistributed(
            keras.layers.Dense(input_dim, activation='linear')
        )(x)
        
        # VAE model
        vae = keras.Model(encoder_inputs, decoder_outputs, name='vae')
        
        # VAE loss - fix dimension compatibility
        reconstruction_loss = tf.reduce_mean(keras.losses.mse(encoder_inputs, decoder_outputs))
        reconstruction_loss *= input_dim * self.sequence_length
        
        kl_loss = 1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
        kl_loss = tf.reduce_mean(kl_loss, axis=-1)
        kl_loss *= -0.5
        kl_loss = tf.reduce_mean(kl_loss)  # Fix: ensure scalar loss
        
        vae_loss = reconstruction_loss + kl_loss
        vae.add_loss(vae_loss)
        vae.compile(optimizer='adam')
        
        return vae