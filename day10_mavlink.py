import time
from pymavlink import mavutil

print("Connecting directly to ArduPilot SITL via TCP port 5762...")
# Connect to secondary SITL TCP port
master = mavutil.mavlink_connection('tcp:127.0.0.1:5762')

print("Waiting for heartbeat from vehicle...")
master.wait_heartbeat()
print(f"Heartbeat received! Target System ID: {master.target_system}, Component ID: {master.target_component}")

# Request telemetry streams at 4Hz
master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    4, # 4 Hz
    1  # Enable
)

print("\n--- Direct MAVLink Telemetry Stream ---")
try:
    for _ in range(10):
        msg = master.recv_match(type=['GLOBAL_POSITION_INT', 'SYS_STATUS'], blocking=True, timeout=3)
        if msg is not None:
            msg_type = msg.get_type()
            
            if msg_type == 'GLOBAL_POSITION_INT':
                relative_alt_meters = msg.relative_alt / 1000.0
                print(f"[GPS/Pos] Relative Altitude: {relative_alt_meters:.2f} m | Heading: {msg.hdg / 100.0}°")
                
            elif msg_type == 'SYS_STATUS':
                battery_voltage = msg.voltage_battery / 1000.0
                print(f"[System]  Battery Voltage: {battery_voltage:.2f} V")
                
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStream stopped by user.")

print("Telemetry check complete!")
