'''
import time
from pymavlink import mavutil

print("Connecting to BlueBoat...")
# Explicitly setting our Source System to 255 (Standard for GCS/Scripts)
#master = mavutil.mavlink_connection('udpout:192.168.2.2:14551', source_system=255)
master = mavutil.mavlink_connection('udpout:192.168.2.2:14551', source_system=255)
print("Priming Windows socket...")
master.mav.heartbeat_send(
    mavutil.mavlink.MAV_TYPE_GCS,          
    mavutil.mavlink.MAV_AUTOPILOT_INVALID, 
    0, 0, 0
)
print(f"Connection Established! Target System is: {master.target_system}")

# Keep track of time so we only send heartbeats once a second
last_heartbeat_time = 0

while True:
    current_time = time.time()
    
    # --- 1. THE HEARTBEAT SENDER (Runs at 1 Hz) ---
    if current_time - last_heartbeat_time >= 1.0:
        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,          # Identify as a Ground Station
            mavutil.mavlink.MAV_AUTOPILOT_INVALID, # We are not a flight controller
            0, 0, 0
        )
        last_heartbeat_time = current_time
        # Print on a new line so you can see it working
        print("\n[HEARTBEAT] Sent to keep connection alive.")

    # --- 2. THE MANUAL CONTROL SENDER (Runs at ~23 Hz) ---
    master.mav.manual_control_send(
        1,
        0,      # X (Forward/Back)
        0,      # Y (Strafe)
        32767,  # Z (Throttle/Depth - 32767 means IGNORE)
        0,      # R (Yaw)
        0       # Buttons
    )
    
    # Print status on a single updating line
    print("[MANUAL_CONTROL] Packet sent.", end="\r")
    
    # Sleep to achieve ~23 Hz
    time.sleep(0.043)
'''
import time
from pymavlink import mavutil

print("Listening for BlueBoat on port 14551...")
# udpin:0.0.0.0 means "Listen on all network adapters for incoming data"
master = mavutil.mavlink_connection('udpin:0.0.0.0:14551', source_system=255)

print("Waiting for boat heartbeat...")
# Because BlueOS is throwing data at us, this should clear almost instantly.
master.wait_heartbeat()
print(f"Connection Established! Target System is: {master.target_system}")

last_heartbeat_time = 0
packet_count = 0

while True:
    current_time = time.time()
    
    # --- 1. THE HEARTBEAT SENDER ---
    if current_time - last_heartbeat_time >= 1.0:
        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,          
            mavutil.mavlink.MAV_AUTOPILOT_INVALID, 
            0, 0, 0
        )
        last_heartbeat_time = current_time
        print("\n[HEARTBEAT] Sent System 255 Heartbeat.")

    # --- 2. THE MANUAL CONTROL SENDER ---
    master.mav.manual_control_send(
        1,      # Target System (Hardcoded to 1 to reach the Autopilot)
        0,      # X 
        0,      # Y 
        32767,  # Z (Ignore)
        0,      # R 
        0       # Buttons
    )
    
    packet_count += 1
    if packet_count % 23 == 0:
        # Print only once a second so we don't flood your IDE console
        print(f"[MANUAL_CONTROL] 23 packets sent successfully...")
        
    time.sleep(0.043)
