import time
import collections
import sys

# Crucial compatibility fix for Python 3.10+ environments
if sys.version_info >= (3, 10):
    from collections import abc
    collections.MutableMapping = abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative

# 1. Establish data link connection to the running SITL simulation instance
print("Connecting to virtual drone chassis on port 5760...")
vehicle = connect('udpin:127.0.0.1:14551', wait_ready=True)

def arm_and_takeoff(target_altitude):
    print("Initializing pre-flight health diagnostics...")
    
    # Wait until the Extended Kalman Filter (EKF) achieves stable localization lock
    while not vehicle.is_armable:
        print(" Waiting for structural sensor calibration and GPS lock...")
        time.sleep(1)

    print("Sensor telemetry verified. Armable status: OK.")
    
    # Transition the autopilot hardware state into GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != 'GUIDED':
        print(" Transitioning flight profile to GUIDED mode...")
        time.sleep(1)

    print("Flight profile lock: GUIDED.")
    
    # Spin up vehicle actuator arrays
    vehicle.armed = True
    while not vehicle.armed:
        print(" Transmitting arm signal to electronic speed controllers...")
        time.sleep(1)

    print("Motors status: ARMED. Clear takeoff zone.")
    
    # Execute autonomous ascent sequence
    print(f"Executing vertical ascent to: {target_altitude} meters.")
    vehicle.simple_takeoff(target_altitude)

    # Monitor current telemetry until altitude threshold matches target bounds
    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        print(f" Telemetry Feedback -> Target: {target_altitude}m | Current Altitude: {current_alt:.2f}m")
        
        # Break loop once drone reaches 95% of targeted target height
        if current_alt >= target_altitude * 0.95:
            print("Target altitude baseline achieved.")
            break
        time.sleep(1)

# Run the takeoff sequence to 5 meters
arm_and_takeoff(5)

print("Holding altitude stabilization routine for 5 seconds...")
time.sleep(5)

# Initiate ground return phase
print("Initiating automated recovery descent...")
vehicle.mode = VehicleMode("LAND")

# Terminate pipeline links cleanly
print("Closing ground system software sockets...")
vehicle.close()
print("Mission loop successfully concluded.")
