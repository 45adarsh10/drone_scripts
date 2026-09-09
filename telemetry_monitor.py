import time
import collections
import sys

# Python 3.10+ Compatibility Patch
if sys.version_info >= (3, 10):
    from collections import abc
    collections.MutableMapping = abc.MutableMapping

from dronekit import connect

print("Connecting to drone telemetry stream on port 14550...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

print("\n--- LIVE DRONE TELEMETRY MONITOR ---")
try:
    for i in range(15):
        # Read GPS, EKF, and attitude telemetry
        lat = vehicle.location.global_frame.lat
        lon = vehicle.location.global_frame.lon
        alt = vehicle.location.global_relative_frame.alt
        heading = vehicle.heading
        groundspeed = vehicle.groundspeed
        mode = vehicle.mode.name
        armed = vehicle.armed
        ekf_ok = vehicle.ekf_ok

        print(f"[{i+1:02d}/15] Mode: {mode} | Armed: {armed} | EKF OK: {ekf_ok}")
        print(f"       Lat: {lat:.6f} | Lon: {lon:.6f} | Alt: {alt:.2f}m")
        print(f"       Heading: {heading}° | Speed: {groundspeed:.2f} m/s")
        print("-" * 55)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nTelemetry polling stopped.")

vehicle.close()
print("Telemetry link closed.")
import time
import collections
import sys

# Python 3.10+ Compatibility Patch
if sys.version_info >= (3, 10):
    from collections import abc
    collections.MutableMapping = abc.MutableMapping

from dronekit import connect

print("Connecting to drone telemetry stream on port 14550...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

print("\n--- LIVE DRONE TELEMETRY MONITOR ---")
try:
    for i in range(15):
        # Read GPS, EKF, and attitude telemetry
        lat = vehicle.location.global_frame.lat
        lon = vehicle.location.global_frame.lon
        alt = vehicle.location.global_relative_frame.alt
        heading = vehicle.heading
        groundspeed = vehicle.groundspeed
        mode = vehicle.mode.name
        armed = vehicle.armed
        ekf_ok = vehicle.ekf_ok

        print(f"[{i+1:02d}/15] Mode: {mode} | Armed: {armed} | EKF OK: {ekf_ok}")
        print(f"       Lat: {lat:.6f} | Lon: {lon:.6f} | Alt: {alt:.2f}m")
        print(f"       Heading: {heading}° | Speed: {groundspeed:.2f} m/s")
        print("-" * 55)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nTelemetry polling stopped.")

vehicle.close()
print("Telemetry link closed.")
