# HRV Monitor

A Python-based Heart Rate Variability (HRV) monitoring tool that connects to XOSS heart rate straps via Bluetooth Low Energy (BLE) to collect and analyze heart rate data.

## Features

- BLE device scanning and connection
- Real-time heart rate monitoring
- RR interval collection
- HRV calculation using RMSSD (Root Mean Square of Successive Differences)
- Support for XOSS heart rate straps
- Configurable data collection duration

## Requirements

- Python 3.9 or higher
- Bluetooth Low Energy (BLE) capable device
- XOSS heart rate strap
- Required Python packages:
  - bleak
  - numpy

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd hrv
```

2. Install required packages:
```bash
pip install bleak numpy
```

## Usage

1. Turn on your XOSS heart rate strap and ensure it's in pairing mode
2. Run the script:
```bash
# Run with default 20-second collection duration
python hrv.py

# Run with custom duration (in seconds)
python hrv.py -d 30
```

The script will:
1. Scan for available BLE devices
2. Connect to the XOSS device
3. Collect heart rate and RR interval data for the specified duration (default: 20 seconds)
4. Calculate and display HRV metrics

## Command Line Arguments

- `-d, --duration`: Duration of data collection in seconds (default: 20)
  ```bash
  python hrv.py -d 30  # Collect data for 30 seconds
  ```

## Output

The script provides real-time feedback including:
- Device connection status
- Available services and characteristics
- Heart rate measurements
- RR intervals
- Final HRV analysis including:
  - Total number of RR intervals collected
  - RMSSD value
  - HRV Score

## Notes

- The script collects data for 20 seconds by default
- You can specify a custom duration using the `-d` or `--duration` flag
- HRV calculation requires at least 2 RR intervals
- Make sure your XOSS strap is properly positioned and has good contact with your skin for accurate readings

## License

[Add your preferred license here]
