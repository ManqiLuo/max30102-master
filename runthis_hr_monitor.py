#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/Desktop/max30102-master')

from max30102 import MAX30102
import hrcalc
import time
import numpy as np
from datetime import datetime

sensor = MAX30102()
ir_data = []
red_data = []
hr_buffer = []

# Create filename with timestamp
filename = f"hr_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

print("Place finger on sensor...")
print("HR: Heart Rate | SpO2: Blood Oxygen")
print(f"Saving data to: {filename}")
print("-" * 40)

# Write header to file
with open(filename, 'w') as f:
    f.write("Timestamp, HR (bpm), SpO2 (%)\n")

last_display = 0

while True:
    num_bytes = sensor.get_data_present()
    
    if num_bytes > 0:
        while num_bytes > 0:
            red, ir = sensor.read_fifo()
            num_bytes -= 1
            ir_data.append(ir)
            red_data.append(red)
        
        while len(ir_data) > 100:
            ir_data.pop(0)
            red_data.pop(0)
        
        if len(ir_data) == 100:
            hr, hr_valid, spo2, spo2_valid = hrcalc.calc_hr_and_spo2(ir_data, red_data)
            
            if hr_valid:
                hr_buffer.append(hr)
                while len(hr_buffer) > 5:
                    hr_buffer.pop(0)
                
                if time.time() - last_display >= 3.0:
                    avg_hr = int(np.mean(hr_buffer))
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if spo2_valid:
                        print(f"HR: {avg_hr:3d} bpm | SpO2: {int(spo2):3d}%")
                        # Save to file
                        with open(filename, 'a') as f:
                            f.write(f"{timestamp}, {avg_hr}, {int(spo2)}\n")
                    else:
                        print(f"HR: {avg_hr:3d} bpm | SpO2: --- %")
                        with open(filename, 'a') as f:
                            f.write(f"{timestamp}, {avg_hr}, N/A\n")
                    
                    last_display = time.time()
    
    time.sleep(0.01)
