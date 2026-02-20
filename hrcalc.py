#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/Desktop/max30102-master')
from max30102 import MAX30102
import time
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

def bandpass_filter(data, lowcut=0.7, highcut=3.5, fs=25):
    nyq = fs / 2
    b, a = butter(2, [lowcut/nyq, highcut/nyq], btype='band')
    return filtfilt(b, a, data)

def calc_spo2(ir_data, red_data):
    ir = np.array(ir_data, dtype=float)
    red = np.array(red_data, dtype=float)
    
    ir_ac = np.std(ir)
    ir_dc = np.mean(ir)
    red_ac = np.std(red)
    red_dc = np.mean(red)
    
    if ir_dc == 0 or red_dc == 0 or ir_ac == 0:
        return None
    
    r = (red_ac / red_dc) / (ir_ac / ir_dc)
    spo2 = 110 - 25 * r
    
    if 80 <= spo2 <= 100:
        return round(spo2, 1)
    return None

sensor = MAX30102()
ir_data = []
red_data = []
hr_buffer = []
spo2_buffer = []

print("Place finger on sensor...")
print("HR: Heart Rate | SpO2: Blood Oxygen")
print("-" * 40)

last_display = 0

while True:
    num_bytes = sensor.get_data_present()

    if num_bytes > 0:
        while num_bytes > 0:
            red, ir = sensor.read_fifo()
            num_bytes -= 1
            ir_data.append(ir)
            red_data.append(red)

        while len(ir_data) > 250:
            ir_data.pop(0)
            red_data.pop(0)

        if len(ir_data) < 250:
            continue

        ir_array = np.array(ir_data, dtype=float)

        if np.mean(ir_array) < 50000:
            hr_buffer.clear()
            spo2_buffer.clear()
            if time.time() - last_display >= 3.0:
                print("No finger detected")
                last_display = time.time()
            continue

        # HR calculation
        filtered = bandpass_filter(ir_array)
        peaks, _ = find_peaks(filtered, distance=15, prominence=20)

        if len(peaks) >= 2:
            intervals = np.diff(peaks)
            avg_interval = np.median(intervals)
            hr = int(60 / (avg_interval / 25))

            if 40 < hr < 150:
                if len(hr_buffer) < 3 or abs(hr - np.median(hr_buffer)) <= 20:
                    hr_buffer.append(hr)
                    while len(hr_buffer) > 8:
                        hr_buffer.pop(0)

        # SpO2 calculation
        spo2 = calc_spo2(ir_data, red_data)
        if spo2 is not None:
            spo2_buffer.append(spo2)
            while len(spo2_buffer) > 8:
                spo2_buffer.pop(0)

        if len(hr_buffer) >= 4 and time.time() - last_display >= 3.0:
            avg_hr = int(np.median(hr_buffer))
            if len(spo2_buffer) >= 3:
                avg_spo2 = round(np.median(spo2_buffer), 1)
                print(f"HR: {avg_hr:3d} bpm | SpO2: {avg_spo2}%")
            else:
                print(f"HR: {avg_hr:3d} bpm | SpO2: --- %")
            last_display = time.time()

    time.sleep(0.01)
