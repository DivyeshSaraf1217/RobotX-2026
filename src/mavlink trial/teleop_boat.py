import time
import threading
from pymavlink import mavutil
from pynput import keyboard

# --- 1. GLOBAL STATE VARIABLES ---
# These hold the current joystick intent. 
# Z is 500 (neutral throttle), everything else is 0 (neutral).
current_x = 0    # Forward/Back (W/S)
current_y = 0    # Strafe (Q/E) - BlueBoat usually doesn't strafe, but kept for completeness
current_z = 500  # Up/Down (Throttle)
current_r = 0    # Yaw/Turn (A/D)

# --- 2. THE 10 HZ SENDER FUNCTION ---
def send_telemetry(master):
    """This function runs in a continuous background loop at 10 Hz."""
    while True:
        # Send the current state of the global variables
        master.mav.manual_control_send(
            master.target_system,
            current_x,
            current_y,
            current_z,
            current_r,
            0 # Buttons bitmask (0 means no buttons pressed)
        )
        # Sleep for 0.1 seconds to achieve exactly 10 Hz
        time.sleep(0.1)

# --- 3. THE KEYBOARD LISTENER FUNCTIONS ---
def on_press(key):
    global current_x, current_r
    
    try:
        if key.char == 'w':
            current_x = 1000  # Max forward
        elif key.char == 's':
            current_x = -1000 # Max reverse
        elif key.char == 'd':
            current_r = 1000  # Max turn right
        elif key.char == 'a':
            current_r = -1000 # Max turn left
    except AttributeError:
        pass # Ignore special keys like Shift or Ctrl

def on_release(key):
    global current_x, current_r
    
    try:
        # When you let go of the key, return that specific axis to neutral
        if key.char in ['w', 's']:
            current_x = 0
        elif key.char in ['a', 'd']:
            current_r = 0
    except AttributeError:
        pass
        
    # Press ESC to stop the script safely
    if key == keyboard.Key.esc:
        return False 

# --- 4. MAIN EXECUTION ---
if __name__ == "__main__":
    # Initialize your MAVLink connection
    print("Connecting to BlueBoat...")
    master = mavutil.mavlink_connection('udpin:0.0.0.0:14551')
    master.wait_heartbeat()
    print("Connected! Ready to drive.")
    master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    1, 0, 0, 0, 0, 0, 0)

    # Start the 10 Hz sender in a background Thread
    sender_thread = threading.Thread(target=send_telemetry, args=(master,), daemon=True)
    sender_thread.start()

    # Start the Keyboard Listener in the main thread
    # This will block and listen until you press ESC
    print("Use WASD to drive. Press ESC to quit.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
    0,
    0, 0, 0, 0, 0, 0, 0)

        
    print("Teleop Ended.")
