import csv
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt

# Configuration
BROKER = "****"
PORT = 1883
TOPIC = "sensor/dht11"
CSV_FILENAME = "sensor_log.csv"

# Data containers for plotting
timestamps = []
temperatures = []
humidities = []

# Setup Matplotlib in interactive mode on the main thread
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))


def log_to_csv(timestamp, temp, hum):
  """Appends a new reading to the CSV file safely."""
  file_exists = os.path.exists(CSV_FILENAME)
  with open(CSV_FILENAME, mode="a", newline="") as f:
    writer = csv.writer(f)
    # Write header if file is newly created
    if not file_exists:
      writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)"])
    writer.writerow([timestamp, temp, hum])


def on_message(client, userdata, msg):
  try:
    payload = json.loads(msg.payload.decode())
    t = payload.get("Temperature")
    h = payload.get("Humidity")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time_only = datetime.now().strftime("%H:%M:%S")

    # 1. Save data immediately to CSV file
    log_to_csv(now, t, h)

    # 2. Append new data for live plotting
    timestamps.append(time_only)
    temperatures.append(t)
    humidities.append(h)

    # Keep only the last 20 points on the graph
    if len(timestamps) > 20:
      timestamps.pop(0)
      temperatures.pop(0)
      humidities.pop(0)

    print(f"Logged & Received -> Time: {now} | Temp: {t}°C | Humidity: {h}%")

  except Exception as g:
    print(f"Error parsing message: {g}")


# MQTT Client Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)

print(f"Subscribed to topic '{TOPIC}' on broker {BROKER}. Logging & Plotting...")

# Start the MQTT network loop in a background thread
client.loop_start()

try:
  while True:
    if timestamps:
      # Update Temperature Plot
      ax1.clear()
      ax1.plot(timestamps, temperatures, color="tab:red", marker="o")
      ax1.set_ylabel("Temperature (°C)")
      ax1.set_title("Live DHT11 Sensor Data (Real-Time)")
      ax1.grid(True)
      ax1.tick_params(axis="x", rotation=45)

      # Update Humidity Plot
      ax2.clear()
      ax2.plot(timestamps, humidities, color="tab:blue", marker="o")
      ax2.set_ylabel("Humidity (%)")
      ax2.set_xlabel("Time")
      ax2.grid(True)
      ax2.tick_params(axis="x", rotation=45)

      plt.tight_layout()
      plt.draw()

    plt.pause(1.0)

except KeyboardInterrupt:
  print("\nStopping subscriber and saving logs...")
  client.loop_stop()
  client.disconnect()
  plt.close()
