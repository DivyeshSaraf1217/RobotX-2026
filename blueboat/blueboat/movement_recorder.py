import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.srv import CommandBool, SetMode
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import threading
import time
import math
import csv
import os

# ==========================================
# EXPERIMENT CONFIGURATION VARIABLES
# ==========================================
RECORD_DENSITY_METERS = 0.5  # Drop a new waypoint every 0.5 meters (3D Euclidean distance)
ARRIVAL_RADIUS_METERS = 0.5  # Waypoint arrival threshold (3D Euclidean sphere)
PATH_FILENAME = "saved_path.csv" # Hardcoded file to overwrite and load from
# ==========================================

class RecordReplayNode(Node):
    def __init__(self):
        super().__init__('record_replay_node')
        
        # Define a Best Effort QoS profile to match MAVROS
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # Subscribers and Publishers
        self.local_pos_sub = self.create_subscription(
            PoseStamped, '/mavros/local_position/pose', self.pose_callback, qos_profile)
            
        self.local_pos_pub = self.create_publisher(
            PoseStamped, '/mavros/setpoint_position/local', 10)
            
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        
        # Navigation and Recording Arrays
        self.waypoints = []        
        self.recorded_path = []
        self.current_target = None 
        
        # State Machine: IDLE, RECORDING, NAVIGATING
        self.state = 'IDLE' 
        
        # MAVROS Service Clients
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/set_mode')
        self.is_guided = False
        
        # 10Hz Control Loop
        self.timer = self.create_timer(0.1, self.control_loop)

    def arm_vehicle(self, arm_state):
        if self.arm_client.wait_for_service(timeout_sec=1.0):
            req = CommandBool.Request()
            req.value = arm_state
            self.arm_client.call_async(req)
            action = "ARMED" if arm_state else "DISARMED"
            self.get_logger().info(f"Requested vehicle to be {action}")

    def toggle_mode(self):
        if self.mode_client.wait_for_service(timeout_sec=1.0):
            req = SetMode.Request()
            if self.is_guided:
                req.custom_mode = "MANUAL"
                self.is_guided = False
            else:
                req.custom_mode = "GUIDED"
                self.is_guided = True
            self.mode_client.call_async(req)
            self.get_logger().info(f"Requested mode switch to {req.custom_mode}")

    def pose_callback(self, msg):
        self.current_x = msg.pose.position.x
        self.current_y = msg.pose.position.y
        self.current_z = msg.pose.position.z

    def save_path_to_file(self):
        try:
            with open(PATH_FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                for pt in self.recorded_path:
                    # pt is always stored internally as (x, y, z)
                    writer.writerow([pt[0], pt[1], pt[2]])
            self.get_logger().info(f"Successfully saved {len(self.recorded_path)} waypoints (3D) to {PATH_FILENAME}")
        except Exception as e:
            self.get_logger().error(f"Failed to save path: {e}")

    def load_path_from_file(self):
        loaded_path = []
        if not os.path.exists(PATH_FILENAME):
            self.get_logger().error(f"File {PATH_FILENAME} does not exist. Record a path first.")
            return loaded_path
            
        try:
            with open(PATH_FILENAME, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    # Strip empty values or whitespace
                    clean_row = [val.strip() for val in row if val.strip()]
                    if len(clean_row) == 2:
                        # 2-axis input fallback: automatically default z to 0.0
                        loaded_path.append((float(clean_row[0]), float(clean_row[1]), 0.0))
                    elif len(clean_row) >= 3:
                        # 3-axis input: x, y, z
                        loaded_path.append((float(clean_row[0]), float(clean_row[1]), float(clean_row[2])))
            return loaded_path
        except Exception as e:
            self.get_logger().error(f"Failed to load path: {e}")
            return []

    def control_loop(self):
        if self.state == 'IDLE':
            return
            
        # --- RECORDING LOGIC ---
        if self.state == 'RECORDING':
            if len(self.recorded_path) == 0:
                self.recorded_path.append((self.current_x, self.current_y, self.current_z))
                self.get_logger().info("First waypoint dropped.")
            else:
                last_x, last_y, last_z = self.recorded_path[-1]
                # 3D Euclidean distance
                dist = math.sqrt(
                    (self.current_x - last_x)**2 + 
                    (self.current_y - last_y)**2 + 
                    (self.current_z - last_z)**2
                )
                
                if dist >= RECORD_DENSITY_METERS:
                    self.recorded_path.append((self.current_x, self.current_y, self.current_z))
                    self.get_logger().info(f"Waypoint dropped. Total: {len(self.recorded_path)}")
            return
            
        # --- NAVIGATING LOGIC ---
        if self.state == 'NAVIGATING' and self.current_target is not None:
            # 1. Broadcast the current 3D target coordinate
            msg = PoseStamped()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = "map"
            msg.pose.position.x = self.current_target[0]
            msg.pose.position.y = self.current_target[1]
            msg.pose.position.z = self.current_target[2]
            self.local_pos_pub.publish(msg)
            
            # 2. Check 3D distance to waypoint
            dist = math.sqrt(
                (self.current_target[0] - self.current_x)**2 + 
                (self.current_target[1] - self.current_y)**2 + 
                (self.current_target[2] - self.current_z)**2
            )
                             
            # 3. Smooth Glide Transition
            if dist <= ARRIVAL_RADIUS_METERS:
                if len(self.waypoints) > 0:
                    self.current_target = self.waypoints.pop(0)
                    self.get_logger().info(
                        f"Gliding to next waypoint: X={self.current_target[0]:.2f}, "
                        f"Y={self.current_target[1]:.2f}, Z={self.current_target[2]:.2f}"
                    )
                else:
                    self.state = 'IDLE'
                    self.get_logger().info("Route Complete! Vehicle is holding at final coordinate.")

def user_input_thread(node):
    print("\n--- Record & Replay Navigator ---")
    print("Commands:")
    print("  rec start   : Begin recording path")
    print("  rec stop    : Stop recording and save to file")
    print("  rep fwd     : Replay path Forward (A->B)")
    print("  rep rev     : Replay path Reverse (B->A)")
    print("  stop        : Halt navigation/recording immediately")
    print("  q           : Arm")
    print("  e           : Disarm")
    print("  t           : Toggle Mode (MANUAL <-> GUIDED)")
    print("  x           : Exit program")
    
    while rclpy.ok():
        try:
            cmd_input = input("\nCommand> ").strip().lower()
            parts = cmd_input.split()
            
            if not parts:
                continue
                
            cmd = " ".join(parts)
            
            if cmd == 'x':
                print("Shutting down...")
                rclpy.shutdown()
                break
            elif cmd == 'q':
                node.arm_vehicle(True)
            elif cmd == 'e':
                node.arm_vehicle(False)
            elif cmd == 't':
                node.toggle_mode()
                
            elif cmd == 'stop':
                node.state = 'IDLE'
                node.current_target = None
                node.waypoints.clear()
                print("Halted all operations. State is now IDLE.")
                
            elif cmd == 'rec start':
                node.recorded_path.clear()
                node.state = 'RECORDING'
                print("Recording started! Drive the vehicle manually to drop waypoints.")
                
            elif cmd == 'rec stop':
                node.state = 'IDLE'
                node.save_path_to_file()
                print("Recording stopped and path saved.")
                
            elif cmd == 'rep fwd' or cmd == 'rep rev':
                path = node.load_path_from_file()
                if not path:
                    continue
                    
                if cmd == 'rep rev':
                    path.reverse()
                    print(f"Loaded {len(path)} waypoints in REVERSE order.")
                else:
                    print(f"Loaded {len(path)} waypoints in FORWARD order.")
                    
                node.waypoints = path
                node.current_target = node.waypoints.pop(0)
                node.state = 'NAVIGATING'
                print("Ensure vehicle is ARMED and in GUIDED mode!")
                print(
                    f"Heading to starting coordinate: X={node.current_target[0]:.2f}, "
                    f"Y={node.current_target[1]:.2f}, Z={node.current_target[2]:.2f}"
                )
                
            else:
                print("Invalid command.")
                
        except Exception as e:
            print(f"Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = RecordReplayNode()
    
    ui_thread = threading.Thread(target=user_input_thread, args=(node,))
    ui_thread.daemon = True
    ui_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()