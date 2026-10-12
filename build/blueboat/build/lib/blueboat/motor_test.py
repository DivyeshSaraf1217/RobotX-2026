import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from mavros_msgs.msg import RCOut
from mavros_msgs.srv import CommandBool, SetMode
import threading
import csv
import time
import os

class MotorProfilerNode(Node):
    def __init__(self):
        super().__init__('motor_profiler_node')
        
        # PUBLISHER: Send velocity commands
        self.vel_pub = self.create_publisher(
            Twist, 
            '/mavros/setpoint_velocity/cmd_vel_unstamped', 
            10)
            
        # SUBSCRIBER: Listen to the actual motor outputs (PWM) sent to the ESCs
        self.rc_out_sub = self.create_subscription(
            RCOut, 
            '/mavros/rc/out', 
            self.rc_out_callback, 
            10)
            
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')

        # Profiling State Variables
        self.is_recording = False
        self.move_type = 'linear'
        self.target_vel = 0.0
        self.csv_file = None
        self.csv_writer = None
        self.start_time = 0.0

    def rc_out_callback(self, msg):
        """This triggers every time ArduPilot outputs PWM to the motors."""
        if self.is_recording and self.csv_writer:
            # Calculate elapsed time
            elapsed = time.time() - self.start_time
            
            # BlueBoat default mixer usually outputs Left Motor on Ch1 and Right Motor on Ch3
            # msg.channels is 0-indexed, so Ch1 = index 0, Ch3 = index 2
            # We will log the first 4 channels just to be safe!
            ch1 = msg.channels[0] if len(msg.channels) > 0 else 1500
            ch2 = msg.channels[1] if len(msg.channels) > 1 else 1500
            ch3 = msg.channels[2] if len(msg.channels) > 2 else 1500
            ch4 = msg.channels[3] if len(msg.channels) > 3 else 1500
            
            self.csv_writer.writerow([round(elapsed, 2), self.target_vel, ch1, ch2, ch3, ch4])

    def set_mode_and_arm(self):
        self.get_logger().info("Switching to GUIDED mode and Arming...")
        if self.mode_client.wait_for_service(timeout_sec=2.0):
            req_mode = SetMode.Request()
            req_mode.custom_mode = "GUIDED"
            self.mode_client.call_async(req_mode)
            
        if self.arm_client.wait_for_service(timeout_sec=2.0):
            req_arm = CommandBool.Request()
            req_arm.value = True
            self.arm_client.call_async(req_arm)

    def disarm(self):
        self.get_logger().info("Disarming...")
        if self.arm_client.wait_for_service(timeout_sec=2.0):
            req_arm = CommandBool.Request()
            req_arm.value = False
            self.arm_client.call_async(req_arm)

    def publish_velocity(self):
        """Publishes the target velocity continuously while profiling."""
        msg = Twist()
        if self.move_type == 'linear':
            msg.linear.x = self.target_vel
            msg.angular.z = 0.0
        elif self.move_type == 'angular':
            msg.linear.x = 0.0
            msg.angular.z = self.target_vel
        self.vel_pub.publish(msg)

    def run_profile(self, move_type, speed, duration, filename):
        """Executes the automated test run."""
        self.move_type = move_type
        self.target_vel = float(speed)
        
        # Setup CSV file
        filepath = os.path.join(os.getcwd(), filename)
        self.csv_file = open(filepath, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(['Time(s)', f'Target_{move_type.capitalize()}', 'Ch1_PWM(Left)', 'Ch2_PWM', 'Ch3_PWM(Right)', 'Ch4_PWM'])
        
        self.set_mode_and_arm()
        time.sleep(2) # Give it a moment to arm
        
        self.get_logger().info(f"Starting profile: {move_type} at {speed} for {duration} seconds.")
        self.get_logger().info(f"Saving data to: {filepath}")
        
        self.start_time = time.time()
        self.is_recording = True
        
        # Run the loop for the specified duration
        end_time = self.start_time + float(duration)
        while time.time() < end_time and rclpy.ok():
            self.publish_velocity()
            time.sleep(0.1) # 10Hz command rate
            
        # Test finished, stop the boat
        self.is_recording = False
        self.target_vel = 0.0
        self.publish_velocity()
        
        self.csv_file.close()
        self.get_logger().info("Profile complete! Boat stopped and data saved.")
        self.disarm()

def user_interface(node):
    print("\n--- Motor Profiler Tool ---")
    print("This will drive the boat in a straight line or rotate in place and record motor PWM.")
    print("Ensure you are in a large open space of water!")
    
    while rclpy.ok():
        try:
            cmd = input("\nType 's' to start a test, or 'q' to quit: ").strip().lower()
            if cmd == 'q':
                rclpy.shutdown()
                break
            elif cmd == 's':
                move_input = input("Enter movement type ('l' for linear, 'a' for angular): ").strip().lower()
                
                if move_input == 'a':
                    move_type = 'angular'
                    unit = "rad/s"
                else:
                    if move_input != 'l':
                        print("Invalid movement type! Defaulting to 'l' (linear).")
                    move_type = 'linear'
                    unit = "m/s"
                    
                speed = input(f"Enter target speed (e.g. 1.0 {unit}): ")
                duration = input("Enter test duration in seconds (e.g. 10): ")
                filename = input("Enter save filename (e.g. 'without_guard.csv'): ")
                
                if not filename.endswith('.csv'):
                    filename += '.csv'
                    
                node.run_profile(move_type, speed, duration, filename)
            else:
                print("Invalid command.")
        except Exception as e:
            print(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = MotorProfilerNode()
    
    ui_thread = threading.Thread(target=user_interface, args=(node,))
    ui_thread.daemon = True
    ui_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Failsafe stop
        msg = Twist()
        node.vel_pub.publish(msg)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()