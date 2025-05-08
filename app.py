from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os
import asyncio
from bleak import BleakScanner, BleakClient
import struct
import threading

app = Flask(__name__)

REPORT_FILE = "latest_report.json"

# BeatXP Scale Service and Characteristic UUIDs
BEATXP_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
BEATXP_CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"

# Global scale data
scale_data = {
    "weight": "--",
    "body_fat": "--",
    "muscle": "--",
    "bmi": "--",
    "water": "--",
    "bone_mass": "--",
    "visceral_fat": "--",
    "protein": "--",
    "bmr": "--",
    "measured_at": "--",
    "name": "--",
    "age": "--",
    "gender": "--",
    "height": "--",
    "is_connected": False,
    "device_name": "--"
}

# Store selected device address
selected_scale_address = {"address": None}

@app.route("/scan-ble-devices")
def scan_ble_devices():
    devices = asyncio.run(BleakScanner.discover(timeout=5.0))
    device_list = [
        {"name": d.name or "Unknown", "address": d.address}
        for d in devices if d.name
    ]
    return jsonify(device_list)

@app.route("/connect-scale-device", methods=["POST"])
def connect_scale_device():
    data = request.get_json()
    address = data.get("address")
    if not address:
        return jsonify({"success": False, "error": "No address provided"}), 400
    selected_scale_address["address"] = address
    threading.Thread(target=run_scale_reader, daemon=True).start()
    return jsonify({"success": True})

def run_scale_reader():
    asyncio.run(connect_to_scale(selected_scale_address["address"]))

async def connect_to_scale(address):
    while True:
        try:
            async with BleakClient(address) as client:
                device_name = address
                try:
                    device_name = (await client.get_services()).services[0].description or address
                except:
                    pass
                print(f"Connected to {device_name}")
                scale_data["is_connected"] = True
                scale_data["device_name"] = device_name
                await client.start_notify(BEATXP_CHARACTERISTIC_UUID, handle_scale_data)
                while True:
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"Error connecting to scale: {e}")
            scale_data["is_connected"] = False
            scale_data["device_name"] = "--"
            await asyncio.sleep(5)

def handle_scale_data(sender, data):
    try:
        # Parse the data from the scale
        if len(data) >= 20:  # Assuming data packet is at least 20 bytes
            weight = struct.unpack('<f', data[0:4])[0]  # Weight in kg
            bmi = struct.unpack('<f', data[4:8])[0]     # BMI
            body_fat = struct.unpack('<f', data[8:12])[0]  # Body fat percentage
            muscle = struct.unpack('<f', data[12:16])[0]  # Muscle mass
            water = struct.unpack('<f', data[16:20])[0]  # Water percentage
            
            scale_data["weight"] = round(weight, 2)
            scale_data["bmi"] = round(bmi, 2)
            scale_data["body_fat"] = round(body_fat, 2)
            scale_data["muscle"] = round(muscle, 2)
            scale_data["water"] = round(water, 2)
            scale_data["measured_at"] = str(datetime.now())
            
            # Save to file
            with open(REPORT_FILE, "w") as f:
                json.dump(scale_data, f)
    except Exception as e:
        print(f"Error parsing scale data: {e}")

@app.route("/")
def index():
    return render_template("index.html", scale_connected=scale_data["is_connected"])

@app.route("/get-data", methods=["POST"])
def get_data():
    # Extract form values
    name = request.form.get("name")
    age = request.form.get("age")
    gender = request.form.get("gender")
    height = request.form.get("height")

    # Update scale data with form values
    scale_data["name"] = name
    scale_data["age"] = age
    scale_data["gender"] = gender
    scale_data["height"] = height

    # Save to file
    with open(REPORT_FILE, "w") as f:
        json.dump(scale_data, f)

    return jsonify(success=True)

@app.route("/report")
def report():
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE) as f:
            data = json.load(f)
        return render_template("report.html", data=data)
    return "No report available."

@app.route("/scale-status")
def scale_status():
    return jsonify({"connected": scale_data["is_connected"]})

@app.route("/get-scale-data")
def get_scale_data():
    return jsonify(scale_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 