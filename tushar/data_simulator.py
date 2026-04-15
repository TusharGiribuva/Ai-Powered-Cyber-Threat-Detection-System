import pandas as pd
import numpy as np
import random
import time
from datetime import datetime, timedelta

PROTOCOLS = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'DNS']
THREAT_TYPES = ['Normal', 'DDoS', 'Port Scan', 'Brute Force', 'SQL Injection']
THREAT_PROBABILITIES = [0.85, 0.05, 0.05, 0.03, 0.02]

def generate_network_traffic(num_records=50, historical_minutes=10, blocklist=None):
    """Generates mock network traffic dataframe."""
    if blocklist is None:
        blocklist = set()
    data = []
    
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=historical_minutes)
    
    # Generate random timestamps between start and end
    time_diff = (end_time - start_time).total_seconds()
    
    for _ in range(num_records):
        timestamp = start_time + timedelta(seconds=random.uniform(0, time_diff))
        protocol = random.choice(PROTOCOLS)
        
        # Inject anomalies based on probabilities
        label = np.random.choice(THREAT_TYPES, p=THREAT_PROBABILITIES)
        
        if label == 'Normal':
            src_bytes = int(np.random.normal(500, 100))
            dst_bytes = int(np.random.normal(1000, 300))
            duration = round(random.uniform(0.01, 2.0), 3)
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([80, 443, 53, 22])
            is_anomaly = 0
            confidence = random.uniform(0.90, 0.99)
        else:
            is_anomaly = 1
            confidence = random.uniform(0.85, 0.99)
            if label == 'DDoS':
                src_bytes = int(np.random.normal(5000, 2000))
                dst_bytes = int(np.random.normal(100, 50))
                duration = round(random.uniform(0.001, 0.1), 3)
                src_port = random.randint(1024, 65535)
                dst_port = 80
            elif label == 'Port Scan':
                src_bytes = int(random.uniform(40, 100))
                dst_bytes = 0
                duration = round(random.uniform(0.001, 0.5), 3)
                src_port = random.randint(1024, 65535)
                dst_port = random.randint(1, 1024)
            else:
                src_bytes = int(np.random.normal(2000, 500))
                dst_bytes = int(np.random.normal(5000, 1000))
                duration = round(random.uniform(1.0, 5.0), 3)
                src_port = random.randint(1024, 65535)
                dst_port = random.choice([22, 80, 443])

        # Determine IPs: src = external/client, dst = internal server
        if label == 'Normal':
            src_ip = f"10.0.{random.randint(1, 5)}.{random.randint(10, 250)}"
        else:
            # Use a slightly restricted pool of attacker IPs so the blocklist has a visible effect
            src_ip = f"45.{random.randint(100, 105)}.40.10"
            
        dst_ip = f"192.168.1.{random.randint(10, 50)}"
        
        # Firewall Enforcement
        if src_ip in blocklist:
            label = 'Normal'
            is_anomaly = 0
            src_ip = f"10.0.{random.randint(1, 5)}.{random.randint(10, 250)}"
            src_bytes = int(np.random.normal(500, 100))
            dst_bytes = int(np.random.normal(1000, 300))
            confidence = random.uniform(0.90, 0.99)
        
        data.append({
            'timestamp': timestamp,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': protocol,
            'src_bytes': max(10, src_bytes),
            'dst_bytes': max(0, dst_bytes),
            'duration': max(0.001, duration),
            'label': label,
            'is_anomaly': is_anomaly,
            'confidence': round(confidence, 2)
        })
        
    df = pd.DataFrame(data)
    df = df.sort_values(by='timestamp').reset_index(drop=True)
    return df

def generate_live_packet(blocklist=None):
    """Generates a single live packet for real-time streaming simulation."""
    return generate_network_traffic(num_records=1, historical_minutes=0, blocklist=blocklist).iloc[0].to_dict()
