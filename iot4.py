import streamlit as st
import paho.mqtt.client as mqtt
import time
from threading import Thread

# ----------------------------
# MQTT CONFIGURATION
# ----------------------------
BROKER = "broker.hivemq.com"      # You can use "test.mosquitto.org" or your local broker IP
PORT = 1883
PUBLISH_TOPIC = "home/controls"
SUBSCRIBE_TOPIC = "home/sensors"

# ----------------------------
# STREAMLIT SETUP
# ----------------------------
st.set_page_config(page_title="IoT MQTT Dashboard", layout="wide")
st.title("📡 IoT MQTT Communication with Node-RED")
st.markdown("""
This Streamlit app communicates with **Node-RED** using MQTT.  
- It **publishes** commands (e.g., turn ON light).  
- It **subscribes** to sensor data from Node-RED or ESP devices.
""")

# ----------------------------
# GLOBALS
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------
# MQTT CALLBACKS
# ----------------------------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.mqtt_status = "✅ Connected to MQTT Broker!"
        client.subscribe(SUBSCRIBE_TOPIC)
    else:
        st.session_state.mqtt_status = f"❌ Connection failed (Code {rc})"

def on_message(client, userdata, msg):
    message = f"[{time.strftime('%H:%M:%S')}] {msg.topic}: {msg.payload.decode()}"
    st.session_state.messages.append(message)

# ----------------------------
# MQTT CLIENT SETUP
# ----------------------------
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Run MQTT client in background thread
def mqtt_loop():
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

thread = Thread(target=mqtt_loop)
thread.daemon = True
thread.start()

# ----------------------------
# STREAMLIT UI
# ----------------------------
st.sidebar.header("🔘 MQTT Controls")

command = st.sidebar.selectbox(
    "Select Command to Send to Node-RED",
    ["Turn ON Light", "Turn OFF Light", "Turn ON Fan", "Turn OFF Fan", "Request Sensor Data"]
)

if st.sidebar.button("🚀 Publish Command"):
    client.publish(PUBLISH_TOPIC, command)
    st.sidebar.success(f"Command '{command}' sent to Node-RED!")

# ----------------------------
# MQTT STATUS + MESSAGES
# ----------------------------
st.subheader("📡 MQTT Connection Status")
st.info(st.session_state.get("mqtt_status", "⏳ Connecting..."))

st.subheader("📥 Incoming Messages (from Node-RED)")
messages_box = st.empty()

# Live message feed
while True:
    with messages_box.container():
        if len(st.session_state.messages) == 0:
            st.write("No messages received yet...")
        else:
            for msg in st.session_state.messages[-10:]:
                st.success(msg)
    time.sleep(1)
