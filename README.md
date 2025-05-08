# Medical Monitoring Dashboard

A comprehensive medical monitoring system that integrates various health sensors including ECG, EMG, SpO2, temperature, and BeatXP weight scale measurements.

## Features

- Real-time monitoring of multiple health parameters:
  - ECG (Electrocardiogram)
  - EMG (Electromyography)
  - SpO2 (Blood Oxygen Saturation)
  - Body Temperature
  - Weight Scale Measurements (BeatXP Infinity Body Fat Scale)
    - Weight
    - BMI
    - Body Fat Percentage
    - Muscle Mass
    - Water Percentage
- Modern, responsive web interface
- Real-time data visualization
- Automatic sensor data collection
- Bluetooth integration for weight scale

## Hardware Requirements

- Arduino board (for EMG and temperature)
- HealthyPi v4 (for ECG and SpO2)
- BeatXP Infinity Body Fat Scale (Model: BXPBMI1001)
- Raspberry Pi or similar Linux-based system

## Software Requirements

- Python 3.x
- Flask
- PySerial
- Bleak (for Bluetooth communication)
- Chrome/Chromium browser

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medical-monitoring-dashboard.git
cd medical-monitoring-dashboard
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip bluetooth libbluetooth-dev
```

4. Make the startup script executable:
```bash
chmod +x start_medical_dashboard.sh
```

## Usage

1. Connect all hardware devices:
   - Arduino to USB port
   - HealthyPi to USB port
   - Ensure BeatXP scale is in pairing mode

2. Run the startup script:
```bash
./start_medical_dashboard.sh
```

3. Open your browser and navigate to:
```
http://localhost:5050
```

## Project Structure

```
medical-monitoring-dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── start_medical_dashboard.sh  # Startup script
├── templates/
│   └── index.html        # Web interface
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- BeatXP for their Infinity Body Fat Scale
- HealthyPi for their medical monitoring hardware
- Arduino community for sensor integration support 