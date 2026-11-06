import rclpy
from rclpy.node import Node
from mavros_msgs.srv import CommandLong
import threading
import sys

class BlueboatHardwareController(Node):
    def __init__(self):
        super().__init__('blueboat_interactive_hardware_controller')
        self.cmd_client = self.create_client(CommandLong, '/mavros/cmd/command')
        
        # Wait for MAVROS to come online
        while not self.cmd_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for MAVROS command service...')
            
        self.get_logger().info('MAVROS connected. Ready for commands.')

    def set_servo(self, channel, pwm_value):
        req = CommandLong.Request()
        req.broadcast = False
        req.command = 183  # MAV_CMD_DO_SET_SERVO
        req.param1 = float(channel)
        req.param2 = float(pwm_value)
        
        self.get_logger().info(f'Sending Command: Servo {channel} -> {pwm_value}us')
        self.cmd_client.call_async(req)

    def set_relay(self, relay_instance, state):
        req = CommandLong.Request()
        req.broadcast = False
        req.command = 181  # MAV_CMD_DO_SET_RELAY
        req.param1 = float(relay_instance)
        req.param2 = float(state)
        
        state_str = "ON" if state else "OFF"
        self.get_logger().info(f'Sending Command: Relay {relay_instance} -> {state_str}')
        self.cmd_client.call_async(req)


def user_menu(node):
    """
    This function runs in a separate thread. It provides the UI and 
    sends commands to the node without blocking the ROS 2 executor.
    """
    while rclpy.ok():
        print("\n=== BlueBoat Hardware Control ===")
        print("1. Set Servo 1 (Channel 6)")
        print("2. Set Servo 2 (Channel 7)")
        print("3. Toggle Relay (Instance 8)")
        print("4. Exit")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1' or choice == '2':
            channel = 6 if choice == '1' else 7
            try:
                pwm = float(input(f"Enter PWM for Channel {channel} (1000-2000): "))
                ##if 1000 <= pwm <= 2000:
                node.set_servo(channel, pwm)
                ##else:
                    ##print("Error: PWM must be between 1000 and 2000.")
            except ValueError:
                print("Error: Invalid number entered.")
                
        elif choice == '3':
            try:
                state_input = input("Enter Relay state (1 for ON, 0 for OFF): ").strip()
                if state_input in ['0', '1']:
                    state = int(state_input)
                    node.set_relay(0, state)
                else:
                    print("Error: Please enter exactly 1 or 0.")
            except ValueError:
                print("Error: Invalid number entered.")
                
        elif choice == '4':
            print("Exiting...")
            # Trigger ROS shutdown to cleanly exit the main thread
            rclpy.shutdown()
            sys.exit(0)
            
        else:
            print("Invalid choice, please try again.")


def main(args=None):
    rclpy.init(args=args)
    node = BlueboatHardwareController()
    
    # Start the interactive menu in a daemon thread. 
    # A daemon thread automatically dies when the main program exits.
    menu_thread = threading.Thread(target=user_menu, args=(node,), daemon=True)
    menu_thread.start()
    
    try:
        # spin() keeps the node alive, processing MAVROS responses in the background.
        # It blocks the main thread, which is why the menu runs in a separate thread.
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nNode interrupted by user (Ctrl+C)")
    finally:
        # Cleanup
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()