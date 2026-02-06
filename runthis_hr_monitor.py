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
print("-" * 40)

last_update = 0 

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
                
                # update display every 3 seconds
                if time.time() - last_update >= 3.0:
                    avg_hr = int(np.mean(hr_buffer))
                    
                    if spo2_valid:
                        print(f"\rHR: {avg_hr:3d} bpm | SpO2: {int(spo2):3d}%", end='', flush=True)
                    else:
                        print(f"\rHR: {avg_hr:3d} bpm | SpO2: --- %", end='', flush=True)
                    
                    last_update = time.time()
    
    time.sleep(0.01)
