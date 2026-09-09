import time
from pymavlink import mavutil

# --- Connect ---
print("Connecting to SITL...")
master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')
master.wait_heartbeat()
print(f"Heartbeat received! System: {master.target_system}, Component: {master.target_component}")


def set_mode(mode):
    mode_id = master.mode_mapping()[mode]
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id
    )
    # Poll HEARTBEAT until custom_mode actually matches what we asked for
    while True:
        hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if hb is not None and hb.custom_mode == mode_id:
            print(f"Mode confirmed: {mode}")
            break
        print(f" Waiting for mode {mode}...")


def arm():
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )
    # Poll HEARTBEAT until the ARMED bit in base_mode is actually set
    while True:
        hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if hb is not None and (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            print("Armed confirmed.")
            break
        print(" Waiting for arm confirmation...")


def takeoff(altitude):
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, 0, altitude
    )
    # Poll GLOBAL_POSITION_INT until relative_alt is within 95% of target
    while True:
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if msg is not None:
            current_alt = msg.relative_alt / 1000.0  # mm -> m
            print(f" Altitude: {current_alt:.2f} m / target {altitude} m")
            if current_alt >= altitude * 0.95:
                print("Target altitude reached.")
                break


def send_velocity(vx, vy, vz):
    master.mav.set_position_target_local_ned_send(
        0,
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,
        0, 0, 0,
        vx, vy, vz,
        0, 0, 0,
        0, 0
    )


def wait_until_disarmed():
    # Poll HEARTBEAT until the ARMED bit clears (confirms landing finished)
    while True:
        hb = master.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
        if hb is not None and not (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            print("Disarm confirmed. Landing complete.")
            break
        print(" Waiting for disarm (landing in progress)...")


# --- Sequence ---
print("Setting GUIDED mode...")
set_mode("GUIDED")

print("Arming...")
arm()

print("Taking off to 5m...")
takeoff(5)

print("Moving forward at 2 m/s for 5 seconds...")
for _ in range(50):
    send_velocity(2, 0, 0)
    time.sleep(0.1)

print("Holding position (zero velocity)...")
for _ in range(30):
    send_velocity(0, 0, 0)
    time.sleep(0.1)

print("Landing...")
set_mode("LAND")
wait_until_disarmed()

print("Mission complete.")
