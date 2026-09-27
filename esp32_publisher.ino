#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Configuration for WiFi
const char* ssid = "***";
const char* pswd = "***";

// Configuration: MQTT Broker
const char* mqtt_server = "****";
const int mqtt_port = ****;
const char* mqtt_topic = "sensor/dht11"; // Fixed: Added semicolon

#define DHTPIN 22
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);
WiFiClient espClient;          // Added: Required for MQTT
PubSubClient client(espClient); // Added: Required for MQTT

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  // Start the DHT sensor and Serial
  dht.begin();
  Serial.begin(115200); // Fixed: Changed from 1115200 to 115200
  
  WiFi.begin(ssid, pswd);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP()); // Fixed: Added parentheses ()

  // Configure MQTT server
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  // Ensure MQTT connection is maintained
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Wait 2 seconds between measurements (DHT11 has a slow sample rate)
  delay(2000);

  // Read humidity and temperature
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Create JSON document using ArduinoJson Library
  JsonDocument doc;
  doc["Temperature"] = t;
  doc["Humidity"] = h;

  char buffer[256];
  serializeJson(doc, buffer);

  // Publish to MQTT topic
  client.publish(mqtt_topic, buffer);

  // Debug output
  Serial.print("Published JSON: ");
  Serial.println(buffer);
}
