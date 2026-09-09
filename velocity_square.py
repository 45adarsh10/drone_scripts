import time
import collections
import sys

# Python 3.10+ Compatibility Patch
if sys.version_info >= (3, 10):
    from collections import abc
    collections.MutableMapping = abc.MutableMapping

from dronekit import connect, VehicleMode
from pymavlink import mavutil

print("Connecting to virtual drone...")
vehicle = connect('127.0.0.1:14550', wait_ready=True)

def arm_and_takeoff(target_alt):
    while not vehicle.is_armable:
        print(" Waiting for GPS and EKF lock...")
        time.sleep(1)
    
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    while not vehicle.armed:
        time.sleep(0.5)
        
    print("Takeoff initiated...")
    vehicle.simple_takeoff(target_alt)
    
    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        if current_alt >= target_alt * 0.95:
            print("Target altitude reached.")
            break
        time.sleep(1)

def send_local_velocity(vx, vy, vz, duration):
    """
    Sends a direct velocity vector command to the drone.
    vx: Speed North (m/s) | vy: Speed East (m/s) | vz: Speed Down (m/s)
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # Coordinate frame
        0b0000111111000111, # Bitmask: Tells autopilot to only listen to vx, vy, vz
        0, 0, 0, # x, y, z positions (ignored)
        vx, vy, vz, # x, y, z velocities in m/s
        0, 0, 0, # x, y, z acceleration (ignored)
        0, 0)    # yaw, yaw_rate (ignored)
    
    # Send the command repeatedly over the specified duration
    for _ in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

# Execute Mission
arm_and_takeoff(5)
print("Hovering for stabilization...")
time.sleep(2)

print("Leg 1: Flying NORTH at 2 m/s for 4 seconds")
send_local_velocity(2, 0, 0, 4)

print("Leg 2: Flying EAST at 2 m/s for 4 seconds")
send_local_velocity(0, 2, 0, 4)

print("Leg 3: Flying SOUTH at 2 m/s for 4 seconds")
send_local_velocity(-2, 0, 0, 4)

print("Leg 4: Flying WEST at 2 m/s for 4 seconds")
send_local_velocity(0, -2, 0, 4)

print("Breaking and stabilizing flight...")
send_local_velocity(0, 0, 0, 2)

print("Returning to launch pad...")
vehicle.mode = VehicleMode("RTL")

vehicle.close()
