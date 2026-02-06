import max30102
import hrcalc
import time

# Initialize the MAX30102 sensor
m = max30102.MAX30102()

def read_sensor():
        while True:
            # Read data from the sensor
            red, ir = m.read_sequential()
            # Calculate heart rate and SpO2
            hr, hr_valid, spo2, spo2_valid = hrcalc.calc_hr_and_spo2(ir, red)

            # Check if valid readings are obtained
            if hr_valid and spo2_valid:
                print("Heart Rate: ", hr, "BPM")
                print("SpO2 Level: ", spo2, "%")
            else:
                print("Invalid readings. Please try again.")

            # Wait for a short time before reading again
            time.sleep(1)

if __name__ == "__main__":
    read_sensor()