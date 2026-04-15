import time
import random
import pandas as pd
import numpy as np

class ThreatDetectionModel:
    """Mock architecture for CNN+LSTM model used for cyber threat detection."""
    
    def __init__(self):
        self.is_loaded = False
        self.model_name = "Hybrid_CNN_LSTM_v1.0"
        self._load_model()
        
    def _load_model(self):
        """Simulates loading weights into the CNN+LSTM architecture."""
        # Intentionally empty for mock. Real implementation would use:
        # self.model = tf.keras.models.load_model('path/to/weights.h5')
        self.is_loaded = True
        
    def preprocess_packet(self, packet_dict):
        """
        FR-2: Data Preprocessing. 
        Simulates normalizing features into a tensor.
        """
        # Convert dictionary to mock tensor array shape (1, Sequence_length, features)
        # Real version would apply min-max scaling and reshape.
        feature_vector = np.array([
            packet_dict.get('src_bytes', 0),
            packet_dict.get('dst_bytes', 0),
            packet_dict.get('duration', 0),
            packet_dict.get('src_port', 0),
            packet_dict.get('dst_port', 0)
        ])
        return feature_vector
        
    def predict(self, packet_dict):
        """
        FR-3: Threat Detection and Classification.
        Runs inference on the preprocessed packet.
        """
        features = self.preprocess_packet(packet_dict)
        
        # Simulate inference delay
        time.sleep(0.01)
        
        # We rely on the simulator's logic for the demonstration to match the UI.
        # In the real system, model.predict(features) happens here.
        simulated_label = packet_dict.get('label', 'Normal')
        is_anomaly = 1 if simulated_label != 'Normal' else 0
        confidence = packet_dict.get('confidence', 0.95)
        
        return {
            'prediction': simulated_label,
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'timestamp': packet_dict.get('timestamp')
        }
