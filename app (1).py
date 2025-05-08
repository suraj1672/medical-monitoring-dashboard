from flask import Flask, render_template, jsonify, request
import serial
import threading
import time
import asyncio
from bleak import BleakScanner, BleakClient
import struct

app = Flask(__name__)
# Serial Ports (update if needed)
arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
healthypi = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Global Sensor Data
sensor_data = {
    "temp": "--",
    "emg": "--",
    "spo2": "--",
    "ecg": "--",
    "emgGraph": [],
    "ecgGraph": [],
    "weight": "--",
    "bmi": "--",
    "body_fat": "--",
    "muscle_mass": "--",
    "water_percentage": "--"
}

# BeatXP Scale Service and Characteristic UUIDs
BEATXP_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
BEATXP_CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"

async def connect_to_scale():
    while True:
        try:
            # Scan for the BeatXP scale
            devices = await BleakScanner.discover()
            for device in devices:
                if "BeatXP" in device.name:
                    async with BleakClient(device.address) as client:
                        print(f"Connected to {device.name}")
                        # Subscribe to notifications
                        await client.start_notify(BEATXP_CHARACTERISTIC_UUID, handle_scale_data)
                        while True:
                            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error connecting to scale: {e}")
            await asyncio.sleep(5)

def handle_scale_data(sender, data):
    try:
        # Parse the data from the scale
        # Note: The actual data format may need to be adjusted based on the scale's protocol
        if len(data) >= 20:  # Assuming data packet is at least 20 bytes
            weight = struct.unpack('<f', data[0:4])[0]  # Weight in kg
            bmi = struct.unpack('<f', data[4:8])[0]     # BMI
            body_fat = struct.unpack('<f', data[8:12])[0]  # Body fat percentage
            muscle_mass = struct.unpack('<f', data[12:16])[0]  # Muscle mass
            water_percentage = struct.unpack('<f', data[16:20])[0]  # Water percentage
            
            sensor_data["weight"] = round(weight, 2)
            sensor_data["bmi"] = round(bmi, 2)
            sensor_data["body_fat"] = round(body_fat, 2)
            sensor_data["muscle_mass"] = round(muscle_mass, 2)
            sensor_data["water_percentage"] = round(water_percentage, 2)
    except Exception as e:
        print(f"Error parsing scale data: {e}")

def read_arduino():
    while True:
        try:
            line = arduino.readline().decode('utf-8').strip()
            if line.startswith("EMG"):
                emg_val = int(line.split(':')[1].split('|')[0])
                temp_val = float(line.split("Temp:")[1].replace("\u00b0C", ""))
                sensor_data["emg"] = emg_val
                sensor_data["temp"] = temp_val
                sensor_data["emgGraph"].append(emg_val)
                if len(sensor_data["emgGraph"]) > 200:
                    sensor_data["emgGraph"].pop(0)
        except:
            continue
def read_healthypi():
    while True:
        try:
            b = healthypi.read(1)
            if not b or b[0] != 0x0A: continue
            if healthypi.read(1)[0] != 0xFA: continue
            hdr = healthypi.read(3)
            length = hdr[0] | (hdr[1] << 8)
            payload = healthypi.read(length)
            footer  = healthypi.read(2)
            if len(payload) == length:
                ecg = int.from_bytes(payload[0:4], byteorder='little', signed=True)
                spo2 = payload[19]
                sensor_data["ecg"] = ecg
                sensor_data["spo2"] = spo2
                sensor_data["ecgGraph"].append(ecg)
                if len(sensor_data["ecgGraph"]) > 200:
                    sensor_data["ecgGraph"].pop(0)
        except:
            continue
@app.route('/')
def index():
    return render_template("index.html")
@app.route('/get_data')
def get_data():
    # Ensure numeric values for frontend logic
    safe_data = sensor_data.copy()
    for k in ['temp', 'emg', 'ecg', 'spo2']:
        try:
            safe_data[k] = float(sensor_data[k])
        except:
            safe_data[k] = 0
    return jsonify(safe_data)
@app.route('/start_emg', methods=['POST'])
def start_emg():
    threading.Thread(target=read_arduino, daemon=True).start()
    return '', 200
@app.route('/start_ecg', methods=['POST'])
def start_ecg():
    threading.Thread(target=read_healthypi, daemon=True).start()
    return '', 200
@app.route('/start_spo2', methods=['POST'])
def start_spo2():
    # SpO2 already handled in ECG reader
    return '', 200
@app.route('/start_scale', methods=['POST'])
def start_scale():
    def run_scale_reader():
        asyncio.run(connect_to_scale())
    
    threading.Thread(target=run_scale_reader, daemon=True).start()
    return '', 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)