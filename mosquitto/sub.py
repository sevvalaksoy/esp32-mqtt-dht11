from datetime import datetime
import json
import matplotlib.pyplot as plt
paho_mqtt = True
import paho.mqtt.client as mqtt

# Configuration
BROKER = "192.168.1.37"
PORT = 1883
TOPIC = "sensor/dht11"

# Data containers
timestamps = []
temperatures = []
humidities = []

# Setup Matplotlib in interactive mode on the main thread
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))


def on_message(client, userdata, msg):
  try:
    payload = json.loads(msg.payload.decode())
    t = payload.get("Temperature")
    h = payload.get("Humidity")
    now = datetime.now().strftime("%H:%M:%S")

    # Append new data
    timestamps.append(now)
    temperatures.append(t)
    humidities.append(h)

    # Keep only the last 20 points
    if len(timestamps) > 20:
      timestamps.pop(0)
      temperatures.pop(0)
      humidities.pop(0)

    print(f"Received -> Temp: {t}°C | Humidity: {h}%")

  except Exception as e:
    print(f"Error parsing message: {e}")


# MQTT Client Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.subscribe(TOPIC)

print(f"Subscribed to topic '{TOPIC}' on broker {BROKER}. Starting plot...")

# Start the MQTT network loop in a background thread safely
client.loop_start()

try:
  # Main thread is now solely dedicated to updating the Matplotlib UI safely
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

    # Pause allows Matplotlib to process window events without threading crashes
    plt.pause(1.0)

except KeyboardInterrupt:
  print("\nStopping subscriber...")
  client.loop_stop()
  client.disconnect()
  plt.close()
