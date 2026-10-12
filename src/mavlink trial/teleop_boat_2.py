import time
import threading
from pymavlink import mavutil
from pynput import keyboard

# --- 1. GLOBAL STATE VARIABLES ---
current_x = 0    
current_y = 0     # Yaw/Turn (A/D)
# BUG FIX: 32767 is the MAVLink standard for "Ignore this axis". 
# This prevents ArduRover from interpreting Z as a reverse throttle command.
current_z = 0  # Forward/Back (W/S)
current_r = 0     

# --- 2. THE 10 HZ SENDER FUNCTION ---
def send_telemetry(master):
    """This function runs in a continuous background loop at 10 Hz."""
    while True:
        # DEBUG LINE: Dynamically print the current values being sent
        print(f"[MAVLink 10Hz] Sending -> X(Forward): {current_x:5} | R(Turn): {current_r:5} | Z: {current_z}", end="\r")
        master.mav.manual_control_send(
            master.target_system,
            current_x,
            current_y,
            current_z,
            current_r,
            0 # Buttons bitmask
        )
        time.sleep(0.1)

# --- 3. THE KEYBOARD LISTENER FUNCTIONS ---
def on_press(key):
    global current_z, current_y
    try:
        if key.char == 'w':
            if current_z != 1000: # Prevent spamming the terminal if key is held down
                current_z = 1000
                print("\n[KEYBOARD] 'W' Pressed  -> Max Forward")
        elif key.char == 's':
            if current_z != -1000:
                current_z = -1000
                print("\n[KEYBOARD] 'S' Pressed  -> Max Reverse")
        elif key.char == 'd':
            if current_y != 1000:
                current_y = 1000
                print("\n[KEYBOARD] 'D' Pressed  -> Hard Right")
        elif key.char == 'a':
            if current_y != -1000:
                current_y = -1000
                print("\n[KEYBOARD] 'A' Pressed  -> Hard Left")
        elif key.char == 'q':
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 0, 0, 0, 0, 0, 0, 0)
            print("\nBoat is DISARMED")
        elif key.char == 'e':
            master.mav.command_long_send(
                master.target_system,
                master.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                0, 1, 0, 0, 0, 0, 0, 0)
            print("\nBoat is ARMED")
    except AttributeError:
        pass # Ignore special keys

def on_release(key):
    global current_x, current_r
    try:
        if key.char in ['w', 's']:
            current_z = 0
            print(f"\n[KEYBOARD] '{key.char.upper()}' Released -> Forward/Back Neutral")
        elif key.char in ['a', 'd']:
            current_y = 0
            print(f"\n[KEYBOARD] '{key.char.upper()}' Released -> Steering Neutral")
                
    except AttributeError:
        pass
        
    if key == keyboard.Key.esc:
        print("\n[KEYBOARD] 'ESC' Pressed -> Initiating Shutdown...")
        return False 

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    print("Connecting to BlueBoat...")
    master = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
    master.wait_heartbeat()    

    # Start the 10 Hz sender
    sender_thread = threading.Thread(target=send_telemetry, args=(master,), daemon=True)
    sender_thread.start()

    print("\n=== TELEOP ACTIVE ===")
    print("Use WASD to drive. Press ESC to quit and disarm.\n")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        # FIX: Instead of listener.join(), we use a loop. 
        # This allows Python to catch the Ctrl+C signal!
        while listener.running:
            time.sleep(0.1)
                
        
        print("Teleop Ended Safely.")
