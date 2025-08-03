import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Anomaly Sentinel", layout="wide")
st.title("🔒 Anomaly Sentinel – Real-Time Threat Detection Dashboard")

# Generate or load the data
np.random.seed(42)
normal_data = np.random.normal(loc=500, scale=100, size=1000)
anomalies = np.random.normal(loc=1200, scale=100, size=10)
traffic_data = np.concatenate([normal_data, anomalies])
df = pd.DataFrame(traffic_data, columns=['bytes_sent'])
df = df.sample(frac=1).reset_index(drop=True)

# Calculate Z-scores and flag anomalies
mean = df['bytes_sent'].mean()
std = df['bytes_sent'].std()
df['z_score'] = (df['bytes_sent'] - mean) / std
df['anomaly'] = df['z_score'].apply(lambda x: abs(x) > 3)

# Timestamps
start_time = datetime.now()
df['timestamp'] = [start_time + timedelta(seconds=10 * i) for i in range(len(df))]
df = df.sort_values('timestamp').reset_index(drop=True)

# Simulate real-time stream
placeholder = st.empty()
log_placeholder = st.container()
chunk_size = 50  # Number of entries shown at a time

# Track previously displayed rows
seen = set()

# User controls
st.sidebar.title("⚙️ Controls")
z_threshold = st.sidebar.slider("Z-score Threshold", min_value=1.0, max_value=5.0, value=3.0, step=0.1)
chunk_size = st.sidebar.number_input("Number of data points per refresh", min_value=10, max_value=200, value=50, step=10)
refresh_rate = st.sidebar.slider("Refresh every (seconds)", min_value=0.5, max_value=5.0, value=1.0, step=0.5)

# Button to pause/resume
run_button = st.sidebar.button("Pause / Resume Stream")
st.session_state['paused'] = st.session_state.get('paused', False)

if run_button:
    st.session_state['paused'] = not st.session_state['paused']

# Initialize variables if not set
if 'index' not in st.session_state:
    st.session_state['index'] = 0
if 'seen' not in st.session_state:
    st.session_state['seen'] = set()

# Stream loop (run once per rerun)
if not st.session_state['paused']:
    current_index = st.session_state['index']
    chunk = df.iloc[:current_index + chunk_size].copy()

    # Recalculate Z-scores with dynamic threshold
    mean = chunk['bytes_sent'].mean()
    std = chunk['bytes_sent'].std()
    chunk['z_score'] = (chunk['bytes_sent'] - mean) / std
    chunk['anomaly'] = chunk['z_score'].apply(lambda x: abs(x) > z_threshold)

    with placeholder.container():
        st.line_chart(chunk.set_index('timestamp')['bytes_sent'])

    with log_placeholder:
        current_anomalies = chunk[chunk['anomaly'] == True]
        unseen = current_anomalies[~current_anomalies.index.isin(st.session_state['seen'])]
        if not unseen.empty:
            st.subheader("🚨 Detected Anomalies")
            for _, row in unseen.iterrows():
                st.markdown(f"**[ALERT]** {row['timestamp']} – High bytes sent: {row['bytes_sent']:.2f}")
            st.session_state['seen'].update(unseen.index)

    st.session_state['index'] += chunk_size
    time.sleep(refresh_rate)
