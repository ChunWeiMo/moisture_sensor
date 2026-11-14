import csv
import socket
import sys
import time
from datetime import datetime

import serial

PORT = "COM8"
BAUD = 115200

ESP32_IP = "192.168.1.188"
PORT = 80

ser = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ESP32_IP, PORT))

for attempt in range(5):
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Connected to {PORT}")
        break
    except serial.SerialException as e:
        print(f"Attempt {attempt + 1}/5: Cannot connect to {PORT}: {e}")
        time.sleep(2)
else:
    print("Failed to open port after 5 attempts. Check if something else is using it.")
    sys.exit(1)


with open("moisture_log.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "raw", "percent"])

    print("Logging started... Press Ctrl+C to stop")
    try:
        while True:
            try:
                line = ser.readline().decode("utf-8").strip()
                if line:
                    parts = line.split(",")
                    if len(parts) == 3:
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        writer.writerow([now, parts[1], parts[2]])
                        f.flush()
                        print(now, parts[1], parts[2])
            except UnicodeDecodeError:
                continue
    except KeyboardInterrupt:
        print("\nStopped. Data saved to moisture_log.csv")
    finally:
        ser.close()
