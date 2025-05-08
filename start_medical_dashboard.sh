#!/bin/bash

# Install required dependencies
sudo apt-get update
sudo apt-get install -y python3-pip bluetooth libbluetooth-dev
sudo pip3 install bleak

# Wait for network to be available
sleep 10

# Start the web server
cd /home/legion/CH341SER/Test  # Updated to your actual working directory
python3 app.py &

# Wait for the server to start
sleep 5

# Start the on-screen keyboard in the background
matchbox-keyboard &

# Open the webpage in Chromium in kiosk mode
chromium-browser --kiosk --app=http://localhost:5050 --noerrdialogs --disable-translate --no-first-run --fast --fast-start --disable-infobars --disable-features=TranslateUI --disk-cache-dir=/dev/null 