import time
import threading
from pymavlink import mavutil
from pynput import keyboard
print("Connecting to BlueBoat...")
master = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
master.wait_heartbeat()
print("Connection Established")
while True:
    print(f"[MAVLink 10Hz end=")
    msg=master.mav.manual_control_send(
        master.target_system,
        0,
        0,
        100,
        0,
        0 # Buttons bitmask
    )
    time.sleep(0.043)
