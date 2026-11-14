import csv
import socket
import sys
import time
from datetime import datetime

import serial

ESP32_IP = "192.168.1.188"
PORT = 80

ser = None

for attempt in range(5):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ESP32_IP, PORT))
        print("Connected to ESP32")
        break
    except serial.SerialException as e:
        print(f"Attempt {attempt + 1}/5: Cannot connect to ESP32: {e}")
        time.sleep(2)
else:
    print("Failed to open port after 5 attempts. Check if something else is using it.")
    sys.exit(1)

filename = f"moisture_log-{datetime.now().strftime('%Y-%m-%d')}.csv"
with open(filename, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "raw", "percent"])

    print("Logging started... Press Ctrl+C to stop")
    buffer = ""
    try:
        while True:
            chunk = s.recv(1024).decode("utf-8")
            if not chunk:
                print("Connection closed by ESP32")
                break

            buffer += chunk

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue

                parts = line.split(",")
                if len(parts) == 3:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([now, parts[1].strip(), parts[2].strip()])
                    f.flush()
                    print(now, parts[1].strip(), parts[2].strip())

    except KeyboardInterrupt:
        print("\nStopped. Data saved to moisture_log.csv")
    finally:
        s.close()
