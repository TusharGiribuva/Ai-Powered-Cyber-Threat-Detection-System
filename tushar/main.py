import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import sys
import os

# Add root project path to sys to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_simulator import generate_network_traffic, generate_live_packet
from inference import ThreatDetectionModel

st.set_page_config(
    page_title="AI Cyber Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'custom.css')
with open(css_file_path) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Initialize Session State & Models
# -----------------------------------------------------------------------------
if 'blocklist' not in st.session_state:
    st.session_state.blocklist = set()

if 'historical_data' not in st.session_state:
    st.session_state.historical_data = generate_network_traffic(num_records=500, historical_minutes=60, blocklist=st.session_state.blocklist)
    
if 'model' not in st.session_state:
    st.session_state.model = ThreatDetectionModel()

if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    
    # Toggle real-time monitoring
    if st.button("▶️ Start Monitoring" if not st.session_state.is_running else "⏸️ Pause Monitoring", use_container_width=True):
        st.session_state.is_running = not st.session_state.is_running
        st.rerun()

    st.markdown("---")
    st.markdown("### View Mode")
    view_mode = st.radio("Interface Level", ["Ordinary User View", "Technician View"])

    st.markdown("---")
    st.markdown("### Model Configuration")
    architecture = st.selectbox("AI Architecture", ["Hybrid CNN + LSTM", "LSTM Only", "CNN Only"])
    threshold = st.slider("Anomaly Confidence Threshold", 0.5, 0.99, 0.85, 0.01)
    
    st.markdown("---")
    st.info("System Health: **OPTIMAL**")
    st.success("Model status: **Loaded**")

# -----------------------------------------------------------------------------
# Main Dashboard UI
# -----------------------------------------------------------------------------
st.markdown("<h1><span class='pulse-ring'></span> Sentinel-X: AI Network Monitor</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -15px; margin-bottom: 30px;'>Real-time intrusion detection and autonomous firewall defense.</p>", unsafe_allow_html=True)

df = st.session_state.historical_data
total_packets = len(df)
anomalies_detected = len(df[df['is_anomaly'] == 1])
threat_ratio = (anomalies_detected / total_packets * 100) if total_packets > 0 else 0
active_threats = len(df[(df['is_anomaly'] == 1) & (df['timestamp'] >= (datetime.now() - pd.Timedelta(minutes=5)))])

# -----------------------------------------------------------------------------
# ORDINARY USER VIEW
# -----------------------------------------------------------------------------
if view_mode == "Ordinary User View":
    if active_threats == 0:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10b981; padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem;">
            <h2 style="color: #10b981; margin:0;"><span style="font-size: 2rem;">🟢</span> Your Network is Safe and Secure</h2>
            <p style="color: #cbd5e1; font-size: 1.1rem; margin-top: 10px;">The AI is actively monitoring all web traffic. No hackers detected recently.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.15); border: 2px solid #ef4444; padding: 2rem; border-radius: 12px; text-align: center; margin-bottom: 2rem; box-shadow: 0 0 20px rgba(239, 68, 68, 0.4);">
            <h2 style="color: #ef4444; margin:0; text-shadow: 0 0 10px rgba(239,68,68,0.8);"><span style="font-size: 2rem;">🔴</span> Alert! We blocked {active_threats} hacking attempt(s)</h2>
            <p style="color: #ffb7b7; font-size: 1.1rem; margin-top: 10px;">The AI detected abnormal behavior and has isolated the threats instantly.</p>
        </div>
        """, unsafe_allow_html=True)

    # Simplified Metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #94a3b8; font-size: 1.1rem; font-weight: 500;">Connection Monitored</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: white;">{total_packets:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="border-color: {'rgba(239, 68, 68, 0.5)' if active_threats > 0 else 'rgba(255,255,255,0.05)'}">
            <div style="color: #94a3b8; font-size: 1.1rem; font-weight: 500;">Hackers Blocked Today</div>
            <div class="{'critical-text' if active_threats > 0 else 'safe-text'}" style="font-size: 2.5rem;">{len(st.session_state.blocklist)} Unique</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #94a3b8; font-size: 1.1rem; font-weight: 500;">AI Certainty</div>
            <div style="font-size: 2.5rem; font-weight: 700; color: #a78bfa;">{round(df['confidence'].mean() * 100, 1) if not df.empty else 100}%</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Active FireWall State
    st.markdown("### 🛡️ Active Countermeasures")
    if len(st.session_state.blocklist) > 0:
        st.warning(f"**Action Taken:** The AI has automatically blocked **{len(st.session_state.blocklist)}** malicious IP Addresses from accessing the network.")
        if st.button("Reset Firewall (Allow All)"):
            st.session_state.blocklist.clear()
            st.rerun()
    else:
        st.info("The firewall is standing by. All connected computers are trusted.")

    # Conversational Explainer History
    st.markdown("### 💬 AI Activity Log")
    st.markdown("<p style='color: #94a3b8;'>A plain-English explanation of recent network events.</p>", unsafe_allow_html=True)
    
    recent_events = df.sort_values(by='timestamp', ascending=False).head(8)
    
    for idx, row in recent_events.iterrows():
        t_stamp = row['timestamp'].strftime('%H:%M:%S')
        if row['is_anomaly'] == 0:
            st.markdown(f"<div style='border-left: 3px solid #10b981; padding-left: 15px; margin-bottom: 10px;'><span style='color: #64748b;'>{t_stamp}</span> - Normal connection from computer `...{row['src_ip'][-6:]}` was permitted.</div>", unsafe_allow_html=True)
        else:
            attack_term = row['label']
            if attack_term == "DDoS":
                attack_term = "Website Overload Attack (Trying to crash the site)"
            elif attack_term == "Brute Force":
                attack_term = "Password Guessing Attack"
            elif attack_term == "Port Scan":
                attack_term = "Network Probing (Looking for vulnerabilities)"
            elif attack_term == "SQL Injection":
                attack_term = "Database Hacking Attempt"
                
            st.markdown(f"<div style='border-left: 3px solid #ef4444; padding-left: 15px; margin-bottom: 10px; background-color: rgba(239, 68, 68, 0.05); padding: 10px; border-radius: 4px;'><span style='color: #ef4444; font-weight:bold;'>{t_stamp} ⚠️ Threat Prevented:</span> Someone tried a <b>{attack_term}</b>. The AI permanently blocked their IP Address with {round(row['confidence']*100, 1)}% certainty.</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# TECHNICIAN VIEW
# -----------------------------------------------------------------------------
else:
    # Layout setup
    top_row = st.columns(4)

    # Metrics UI using HTML/CSS classes from custom.css for premium look
    with top_row[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 500;">TOTAL PACKETS (1H)</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: white;">{total_packets:,}</div>
        </div>
        """, unsafe_allow_html=True)

    with top_row[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 500;">THREAT LEVEL</div>
            <div class="{'critical-text' if threat_ratio > 10 else 'warning-text' if threat_ratio > 5 else 'safe-text'}" style="font-size: 2.2rem;">{str(round(threat_ratio, 1))}%</div>
        </div>
        """, unsafe_allow_html=True)

    with top_row[2]:
        st.markdown(f"""
        <div class="metric-card" style="border-color: {'rgba(239, 68, 68, 0.5)' if active_threats > 0 else 'rgba(255,255,255,0.05)'}">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 500;">ACTIVE THREATS</div>
            <div class="critical-text" style="font-size: 2.2rem;">{active_threats}</div>
        </div>
        """, unsafe_allow_html=True)

    with top_row[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #94a3b8; font-size: 0.9rem; font-weight: 500;">ML CONFIDENCE</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #a78bfa;">{round(df['confidence'].mean() * 100, 1)}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Firewall Controls
    st.markdown("### 🔥 Simulated iptables Blocklist")
    fw_col1, fw_col2 = st.columns([8, 2])
    with fw_col1:
        if len(st.session_state.blocklist) > 0:
            st.code("\n".join([f"iptables -A INPUT -s {ip} -j DROP" for ip in list(st.session_state.blocklist)]), language="bash")
        else:
            st.success("No active layer 3 blocking rules.")
    with fw_col2:
        if st.button("Flush Rules", use_container_width=True):
            st.session_state.blocklist.clear()
            st.rerun()

    st.markdown("---")

    # -----------------------------------------------------------------------------
    # Real-Time Charts & Tables Layout
    # -----------------------------------------------------------------------------
    chart_col, table_col = st.columns([6, 4])

    # Plotting
    with chart_col:
        st.markdown("### Traffic Distribution & Anomaly Mapping")
        # Live Traffic Flow Chart
        time_grouped = df.groupby(pd.Grouper(key='timestamp', freq='1min')).agg({'src_bytes':'sum', 'is_anomaly': 'max'}).reset_index()
        
        fig = px.area(time_grouped, x='timestamp', y='src_bytes', 
                      color_discrete_sequence=['#818cf8'],
                      template="plotly_dark",
                      labels={'src_bytes': 'Bandwidth (Bytes)', 'timestamp': 'Time'})
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            height=300
        )
        
        # Overlay anomalies
        anomalies = df[df['is_anomaly'] == 1]
        if not anomalies.empty:
            fig.add_trace(go.Scatter(
                x=anomalies['timestamp'], y=anomalies['src_bytes'],
                mode='markers', marker=dict(color='#ef4444', size=8, symbol='star', line=dict(width=1, color='white')),
                name='Detected Threat', hoverinfo='text',
                text=anomalies['label'] + "<br>" + anomalies['src_ip']
            ))
            
        st.plotly_chart(fig, use_container_width=True)

    with table_col:
        st.markdown("### Recent Alerts & Classifications")
        # Show only recent threats
        recent_threats = df[df['is_anomaly'] == 1].sort_values(by='timestamp', ascending=False).head(5)
        
        if not recent_threats.empty:
            display_df = recent_threats[['timestamp', 'src_ip', 'label', 'confidence']].copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%H:%M:%S')
            display_df['confidence'] = (display_df['confidence'] * 100).round(1).astype(str) + '%'
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.success("No anomalies detected recently.")

    st.markdown("---")
    st.markdown("### Attack Type Vectors")
    pie_col, bar_col = st.columns([4, 6])

    with pie_col:
        threat_df = df[df['is_anomaly'] == 1]
        if not threat_df.empty:
            pie_fig = px.pie(threat_df, names='label', hole=0.7, 
                             color_discrete_sequence=['#ef4444', '#f59e0b', '#8b5cf6', '#ec4899', '#10b981'],
                             template="plotly_dark")
            pie_fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                height=200,
                showlegend=False
            )
            # Adding center text
            pie_fig.add_annotation(text=f"<b>{len(threat_df)}</b><br>Threats", x=0.5, y=0.5, showarrow=False, font=dict(size=14))
            st.plotly_chart(pie_fig, use_container_width=True)
        else:
            st.info("Not enough threat data to generate distribution.")

    with bar_col:
        if not threat_df.empty:
            port_dist = threat_df['dst_port'].value_counts().reset_index()
            port_dist.columns = ['Port', 'Count']
            port_dist['Port'] = port_dist['Port'].astype(str)
            
            bar_fig = px.bar(port_dist.head(5), x='Port', y='Count', 
                             color_discrete_sequence=['#6366f1'],
                             template="plotly_dark")
            bar_fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0),
                height=200,
                xaxis=dict(showgrid=False, title='Targeted Ports'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title='Attacks')
            )
            st.plotly_chart(bar_fig, use_container_width=True)


# -----------------------------------------------------------------------------
# Streaming Loop
# -----------------------------------------------------------------------------
metric_placeholder = st.empty()

if st.session_state.is_running:
    # Simulate data streaming
    time.sleep(1.5) # Throttle refresh rate
    
    # Pass our global blocklist to the live generator
    new_packet = generate_live_packet(blocklist=st.session_state.blocklist)
    
    # Run Inference
    prediction = st.session_state.model.predict(new_packet)
    
    # AUTO BLOCKING LOGIC
    if prediction['is_anomaly'] == 1 and prediction['confidence'] >= threshold:
        st.session_state.blocklist.add(new_packet['src_ip'])
    
    # Append to dataframe
    new_row_df = pd.DataFrame([new_packet])
    st.session_state.historical_data = pd.concat([st.session_state.historical_data, new_row_df], ignore_index=True)
    
    # Keep dataframe size manageable
    if len(st.session_state.historical_data) > 2000:
        st.session_state.historical_data = st.session_state.historical_data.iloc[-2000:]
        
    st.rerun()
