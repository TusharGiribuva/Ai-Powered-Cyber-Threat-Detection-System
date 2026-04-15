from fastapi import APIRouter, Depends
from core.dependencies import get_current_user
from pydantic import BaseModel
import pandas as pd
from typing import Set, Dict, Any, List, Optional
import time
from datetime import datetime
import json

from services.data_simulator import generate_network_traffic, generate_live_packet
from services.inference import ThreatDetectionModel

router = APIRouter()

# --- In-Memory State ---
class MonitorState:
    def __init__(self):
        self.blocklist: Set[str] = set()
        self.is_running: bool = False
        self.view_mode: str = "Ordinary User View"
        self.threshold: float = 0.85
        # Generate initial history
        self.historical_data = generate_network_traffic(
            num_records=500, historical_minutes=60, blocklist=self.blocklist
        )
        self.model = ThreatDetectionModel()

state = MonitorState()

# Helper to format data for dashboard charts and metrics
def _format_historical_data(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "metrics": {}, "time_grouped": [], "threat_dist": [], 
            "port_dist": [], "recent_alerts": [], "recent_events": [],
            "is_running": state.is_running, "view_mode": state.view_mode, "blocklist": []
        }
        
    df_copy = df.copy()
    
    # Area chart: group by minute
    time_grouped = df_copy.groupby(pd.Grouper(key='timestamp', freq='1min')).agg({'src_bytes':'sum', 'is_anomaly': 'max'}).reset_index()
    time_grouped['time'] = time_grouped['timestamp'].dt.strftime('%H:%M')
    
    # Pie and Bar Chart
    threats = df_copy[df_copy['is_anomaly'] == 1].copy()
    if not threats.empty:
        threat_dist = threats['label'].value_counts().reset_index()
        threat_dist.columns = ['label', 'count']
        
        port_dist = threats['dst_port'].value_counts().reset_index()
        port_dist.columns = ['port', 'count']
        port_dist['port'] = port_dist['port'].astype(str)
        
        recent_threats = threats.sort_values(by='timestamp', ascending=False).head(5)
        recent_threats['timestamp_str'] = recent_threats['timestamp'].dt.strftime('%H:%M:%S')
        recent_threats_list = recent_threats[['timestamp_str', 'src_ip', 'label', 'confidence']].to_dict('records')
    else:
        threat_dist = pd.DataFrame()
        port_dist = pd.DataFrame()
        recent_threats_list = []
    
    # Metrics
    total_packets = len(df_copy)
    anomalies_detected = len(threats)
    
    # Calculate active threats in last 5 minutes
    try:
        five_mins_ago = datetime.now() - pd.Timedelta(minutes=5)
        active_threats = len(df_copy[(df_copy['is_anomaly'] == 1) & (df_copy['timestamp'] >= five_mins_ago)])
    except:
        active_threats = 0
        
    threat_ratio = (anomalies_detected / total_packets * 100) if total_packets > 0 else 0
    avg_confidence = df_copy['confidence'].mean() if not df_copy.empty else 1.0

    # Recent events
    recent_events = df_copy.sort_values(by='timestamp', ascending=False).head(8)
    recent_events_list = []
    for _, row in recent_events.iterrows():
        tstampStr = row['timestamp'].strftime('%H:%M:%S') if hasattr(row['timestamp'], 'strftime') else str(row['timestamp'])
        recent_events_list.append({
            'time': tstampStr,
            'is_anomaly': int(row['is_anomaly']),
            'src_ip': str(row['src_ip']),
            'label': str(row['label']),
            'confidence': float(row['confidence'])
        })

    return {
        "metrics": {
            "total_packets": int(total_packets),
            "threat_ratio": float(threat_ratio),
            "active_threats": int(active_threats),
            "avg_confidence": float(avg_confidence),
            "blocklist_count": len(state.blocklist),
            "anomalies_detected": int(anomalies_detected)
        },
        "time_grouped": time_grouped[['time', 'src_bytes', 'is_anomaly']].to_dict('records') if not time_grouped.empty else [],
        "threat_dist": threat_dist.to_dict('records') if not threat_dist.empty else [],
        "port_dist": port_dist.to_dict('records') if not port_dist.empty else [],
        "recent_alerts": recent_threats_list,
        "recent_events": recent_events_list,
        "is_running": state.is_running,
        "view_mode": state.view_mode,
        "blocklist": list(state.blocklist),
        "threats_total": int(anomalies_detected)
    }

@router.get("/state")
def get_state(user=Depends(get_current_user)):
    """Returns the aggregated data to power the dashboard."""
    return _format_historical_data(state.historical_data)

class ToggleRequest(BaseModel):
    is_running: bool

@router.post("/toggle")
def toggle_monitoring(req: ToggleRequest, user=Depends(get_current_user)):
    state.is_running = req.is_running
    return {"status": "ok", "is_running": state.is_running}

class ModeRequest(BaseModel):
    view_mode: str

@router.post("/mode")
def set_view_mode(req: ModeRequest, user=Depends(get_current_user)):
    state.view_mode = req.view_mode
    return {"status": "ok", "view_mode": state.view_mode}

@router.post("/clear-firewall")
def clear_firewall(user=Depends(get_current_user)):
    state.blocklist.clear()
    return {"status": "ok", "blocklist": list(state.blocklist)}

@router.post("/tick")
def poll_tick(user=Depends(get_current_user)):
    """Simulates one time pass of data ingestion and model inference."""
    if not state.is_running:
        return _format_historical_data(state.historical_data)
    
    # Ingestion
    new_packet = generate_live_packet(blocklist=state.blocklist)
    
    # Inference
    prediction = state.model.predict(new_packet)
    
    # Update state
    if prediction['is_anomaly'] == 1 and prediction['confidence'] >= state.threshold:
        state.blocklist.add(new_packet['src_ip'])
        
    new_row_df = pd.DataFrame([new_packet])
    state.historical_data = pd.concat([state.historical_data, new_row_df], ignore_index=True)
    
    if len(state.historical_data) > 2000:
        state.historical_data = state.historical_data.iloc[-2000:]
        
    return _format_historical_data(state.historical_data)
