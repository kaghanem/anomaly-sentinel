import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Simulate normal activity: 1000 entires of network traffic, bytes sent per session
normal_data = np.random.normal(loc=500, scale=100, size=1000)

# Simulate 10 anomalous sessions (e.g., large data exfiltration or strange behavior)
anomalies = np.random.normal(loc=1200, scale=100, size=10)

#Combine and create a DataFrame
traffic_data = np.concatenate([normal_data, anomalies])
df = pd.DataFrame(traffic_data, columns=['bytes_sent'])

# Shuffle the rows
df = df.sample(frac=1).reset_index(drop=True)

# Preview the first few rows
print(df.head()) 

# Calculate Z-scores
mean = df['bytes_sent'].mean()
std = df['bytes_sent'].std()
df['z_score'] = (df['bytes_sent'] - mean) / std

# Flag anomalies: Z-score > 3 or < -3
df['anomaly'] = df['z_score'].apply(lambda x: abs(x) > 3)

# Create timestamps: one entry every 10 seconds
from datetime import datetime, timedelta

start_time = datetime.now()
timestamps = [start_time + timedelta(seconds=10 * i) for i in range(len(df))]
df['timestamp'] = timestamps

# Sort by time just to keep it realistic
df = df.sort_values('timestamp').reset_index(drop=True)

# Print out the anomalies
print("\nAnomalies detected:")
print(df[df['anomaly'] == True])

import matplotlib.pyplot as plt

# Plotting network traffic over time
plt.figure(figsize=(15, 6))
plt.plot(df['timestamp'], df['bytes_sent'], label='Normal Traffic', color='blue')

# Overlay anomalies in red
anomalies = df[df['anomaly'] == True]
plt.scatter(anomalies['timestamp'], anomalies['bytes_sent'], color='red', label='Anomaly')

# Add labels and legend
plt.title('Network Traffic Over Time with Anomalies Highlighted')
plt.xlabel('Timestamp')
plt.ylabel('Bytes Sent')
plt.legend()
plt.tight_layout()
plt.grid(True)

# Show the plot
plt.show()

# Save detected anomalies to a CSV file
anomalies[['timestamp', 'bytes_sent', 'z_score']].to_csv('anomaly_log.csv', index=False)

print("\nAnomalies have been saved to 'anomaly_log.csv'")

import matplotlib.pyplot as plt

# Plot all data
plt.figure(figsize=(15, 6))
plt.plot(df['timestamp'], df['bytes_sent'], label='Normal Traffic', color='blue')

# Overlay anomalies
anomaly_points = df[df['anomaly'] == True]
plt.scatter(anomaly_points['timestamp'], anomaly_points['bytes_sent'],
            color='red', label='Anomalies', zorder=5)

# Add labels and formatting
plt.xlabel('Time')
plt.ylabel('Bytes Sent')
plt.title('Network Traffic with Anomaly Detection')
plt.legend()
plt.tight_layout()
plt.xticks(rotation=45)
plt.grid(True)

# Show the plot
plt.show()

# Create a log file for anomalies
with open("anomaly_log.txt", "w") as log_file:
    for index, row in anomaly_points.iterrows():
        alert_message = f"[ALERT] {row['timestamp']} - High bytes sent: {row['bytes_sent']:.2f}\n"
        log_file.write(alert_message)


print("\nAlerts written to anomaly_log.txt")
