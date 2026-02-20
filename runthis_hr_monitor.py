#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/Desktop/max30102-master')
from max30102 import MAX30102
import hrcalc
import time
import numpy as np

sensor = MAX30102()
ir_data = []
red_data = []
hr_buffer = []

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
        
        # check finger is on sensor
        if np.mean(ir_data) < 50000 or np.mean(red_data) < 50000:
            hr_buffer.clear()
            if time.time() - last_display >= 3.0:
                print("No finger detected")
                last_display = time.time()
            continue

        if len(ir_data) == 250:
            hr, hr_valid, spo2, spo2_valid = hrcalc.calc_hr_and_spo2(ir_data, red_data)
            
            # only accept physiologically plausible HR
            if hr_valid and 40 < hr < 180:
                hr_buffer.append(hr)
                while len(hr_buffer) > 10:
                    hr_buffer.pop(0)
            
            if len(hr_buffer) >= 5 and time.time() - last_display >= 3.0:
                avg_hr = int(np.median(hr_buffer))  # median is more robust than mean
                
                if spo2_valid:
                    print(f"HR: {avg_hr:3d} bpm | SpO2: {int(spo2):3d}%")
                else:
                    print(f"HR: {avg_hr:3d} bpm | SpO2: --- %")
                
                last_display = time.time()
    
    time.sleep(0.01)
