import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
import threading
import math
import csv
import os

# ==========================================
# EXPERIMENT CONFIGURATION VARIABLES
# ==========================================
RECORD_DENSITY_METERS = 0.5    # Drop a waypoint every 0.5 meters of 3D movement
RECORD_YAW_DEG = 20.0          # Also drop a waypoint if heading changes by 20 degrees
ARRIVAL_RADIUS_METERS = 0.5    # Waypoint arrival threshold (3D Euclidean sphere)
MIN_ENDPOINT_METERS = 0.05     # Capture final point on stop if moved at least 5cm

# Set to True for differential/rudder boats that must face forward when reversing (B to A).
# Set to False for holonomic subs/ROVs that should keep the exact recorded orientation.
REVERSE_FLIPS_HEADING = False

# Anchor the CSV file to the exact directory where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_FILENAME = os.path.join(SCRIPT_DIR, "saved_path.csv")

# Fallback mode when toggling out of GUIDED ("MANUAL" for Rover/Boat/Sub, "LOITER" for Copter)
MANUAL_FALLBACK_MODE = "MANUAL"
# ==========================================


def quaternion_to_yaw(q) -> float:
    """Convert a geometry_msgs Quaternion into a yaw angle in radians (-pi to pi)."""
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def yaw_to_quaternion(yaw: float):
    """Convert a yaw angle in radians into a pure-yaw quaternion (x, y, z, w)."""
    half_yaw = yaw * 0.5
    return (0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw))


def shortest_angular_distance(from_angle: float, to_angle: float) -> float:
    """Return the shortest signed angle (in radians) between two headings, handling -pi/pi wrap."""
    return math.atan2(math.sin(to_angle - from_angle), math.cos(to_angle - from_angle))


class RecordReplayNode(Node):
    def __init__(self):
        super().__init__('record_replay_node')

        # Thread lock to prevent race conditions between CLI and 10Hz control loop
        self.lock = threading.Lock()

        # Best Effort QoS profile to match MAVROS position topics
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        # Subscribers and Publishers
        self.local_pos_sub = self.create_subscription(
            PoseStamped, '/blueboat/mavros/local_position/pose', self.pose_callback, qos_profile
        )
        self.state_sub = self.create_subscription(
            State, '/blueboat/mavros/state', self.state_callback, 10
        )
        self.local_pos_pub = self.create_publisher(
            PoseStamped, '/blueboat/mavros/setpoint_position/local', 10
        )

        # Vehicle Position, Heading & Telemetry State
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.current_yaw = 0.0
        self.pose_received = False

        self.current_mode = "UNKNOWN"
        self.is_armed = False

        # Navigation and Recording Arrays — stored as 4-tuples: (x, y, z, yaw_rad)
        self.waypoints = []
        self.recorded_path = []
        self.current_target = None

        # State Machine: IDLE, RECORDING, NAVIGATING
        self.state = 'IDLE'

        # MAVROS Service Clients
        self.arm_client = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.mode_client = self.create_client(SetMode, '/mavros/setpoint_mode' if False else '/mavros/set_mode')

        # 10Hz Control Loop
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info(f"Node initialized. CSV path anchored to: {PATH_FILENAME}")

    # ------------------------------------------
    # MAVROS CALLBACKS & COMMANDS
    # ------------------------------------------
    def state_callback(self, msg: State):
        with self.lock:
            self.current_mode = msg.mode
            self.is_armed = msg.armed

    def pose_callback(self, msg: PoseStamped):
        with self.lock:
            self.current_x = msg.pose.position.x
            self.current_y = msg.pose.position.y
            self.current_z = msg.pose.position.z
            self.current_yaw = quaternion_to_yaw(msg.pose.orientation)
            self.pose_received = True

    def arm_vehicle(self, arm_state: bool):
        if not self.arm_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Arming service not available.")
            return
        req = CommandBool.Request()
        req.value = arm_state
        self.arm_client.call_async(req)
        action = "ARMED" if arm_state else "DISARMED"
        self.get_logger().info(f"Requested vehicle to be {action}")

    def toggle_mode(self):
        if not self.mode_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("SetMode service not available.")
            return

        with self.lock:
            active_mode = self.current_mode

        req = SetMode.Request()
        if active_mode == "GUIDED":
            req.custom_mode = MANUAL_FALLBACK_MODE
        else:
            req.custom_mode = "GUIDED"

        self.mode_client.call_async(req)
        self.get_logger().info(
            f"Current mode is {active_mode}. Requested switch to {req.custom_mode}"
        )

    def publish_setpoint(self, x: float, y: float, z: float, yaw: float):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.pose.position.x = float(x)
        msg.pose.position.y = float(y)
        msg.pose.position.z = float(z)

        qx, qy, qz, qw = yaw_to_quaternion(float(yaw))
        msg.pose.orientation.x = qx
        msg.pose.orientation.y = qy
        msg.pose.orientation.z = qz
        msg.pose.orientation.w = qw

        self.local_pos_pub.publish(msg)

    # ------------------------------------------
    # FILE I/O OPERATIONS
    # ------------------------------------------
    def save_path_to_file(self, path_data):
        if not path_data:
            self.get_logger().warn(
                "Recorded path is empty (0 waypoints). Skipping save to protect existing CSV."
            )
            return False

        try:
            os.makedirs(os.path.dirname(PATH_FILENAME), exist_ok=True)
            with open(PATH_FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                for pt in path_data:
                    # Saves 4 columns: x, y, z, yaw (radians)
                    writer.writerow([pt[0], pt[1], pt[2], pt[3]])
                file.flush()
                os.fsync(file.fileno())

            self.get_logger().info(
                f"Saved {len(path_data)} waypoints (with heading) to {PATH_FILENAME}"
            )
            return True
        except Exception as e:
            self.get_logger().error(f"Failed to save path to {PATH_FILENAME}: {e}")
            return False

    def load_path_from_file(self):
        loaded_path = []
        if not os.path.exists(PATH_FILENAME):
            self.get_logger().error(
                f"File not found at {PATH_FILENAME}. Record a path first."
            )
            return loaded_path

        try:
            raw_rows = []
            with open(PATH_FILENAME, mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    clean_row = [val.strip() for val in row if val.strip()]
                    if len(clean_row) >= 2:
                        raw_rows.append([float(val) for val in clean_row])

            for i, vals in enumerate(raw_rows):
                if len(vals) >= 4:
                    # 4-column CSV: (x, y, z, yaw_rad)
                    loaded_path.append((vals[0], vals[1], vals[2], vals[3]))
                else:
                    # Fallback for legacy 2-column or 3-column CSVs without recorded yaw:
                    # Automatically compute line-of-sight heading toward the next waypoint
                    x = vals[0]
                    y = vals[1]
                    z = vals[2] if len(vals) == 3 else 0.0
                    if i + 1 < len(raw_rows):
                        dx = raw_rows[i + 1][0] - x
                        dy = raw_rows[i + 1][1] - y
                        auto_yaw = math.atan2(dy, dx)
                    elif len(loaded_path) > 0:
                        auto_yaw = loaded_path[-1][3]
                    else:
                        auto_yaw = 0.0
                    loaded_path.append((x, y, z, auto_yaw))

            self.get_logger().info(
                f"Loaded {len(loaded_path)} waypoints from {PATH_FILENAME}"
            )
            return loaded_path
        except Exception as e:
            self.get_logger().error(f"Failed to load path from {PATH_FILENAME}: {e}")
            return []

    # ------------------------------------------
    # THREAD-SAFE STATE TRANSITIONS
    # ------------------------------------------
    def start_recording(self):
        with self.lock:
            if not self.pose_received:
                self.get_logger().error(
                    "Cannot start recording: No position data received from MAVROS yet!"
                )
                return

            self.waypoints.clear()
            self.current_target = None
            self.recorded_path.clear()

            # Drop the first waypoint with current 3D position + yaw
            self.recorded_path.append(
                (self.current_x, self.current_y, self.current_z, self.current_yaw)
            )
            self.state = 'RECORDING'
            self.get_logger().info(
                f"Recording started! Waypoint #1 dropped at "
                f"X={self.current_x:.2f}, Y={self.current_y:.2f}, Z={self.current_z:.2f}, "
                f"Yaw={math.degrees(self.current_yaw):.1f} deg"
            )

    def _append_final_endpoint_locked(self):
        """Helper to capture the final pose on stop (must be called while holding self.lock)."""
        if len(self.recorded_path) > 0:
            last_x, last_y, last_z, last_yaw = self.recorded_path[-1]
            dist = math.sqrt(
                (self.current_x - last_x) ** 2 +
                (self.current_y - last_y) ** 2 +
                (self.current_z - last_z) ** 2
            )
            yaw_diff = abs(shortest_angular_distance(last_yaw, self.current_yaw))

            if dist >= MIN_ENDPOINT_METERS or yaw_diff >= math.radians(5.0):
                self.recorded_path.append(
                    (self.current_x, self.current_y, self.current_z, self.current_yaw)
                )
                self.get_logger().info(
                    f"Final endpoint captured. Total waypoints: {len(self.recorded_path)}"
                )

    def stop_recording(self):
        path_copy = []
        with self.lock:
            if self.state != 'RECORDING':
                self.get_logger().warn("Node is not currently in RECORDING state.")
                return

            self._append_final_endpoint_locked()
            self.state = 'IDLE'
            path_copy = list(self.recorded_path)

        self.save_path_to_file(path_copy)

    def halt_all(self):
        should_save = False
        path_copy = []

        with self.lock:
            prev_state = self.state
            self.state = 'IDLE'
            self.current_target = None
            self.waypoints.clear()

            if prev_state == 'RECORDING':
                self._append_final_endpoint_locked()
                path_copy = list(self.recorded_path)
                should_save = True

            elif prev_state == 'NAVIGATING' and self.pose_received:
                # Command the vehicle to hold its current 3D position AND current heading
                self.publish_setpoint(
                    self.current_x, self.current_y, self.current_z, self.current_yaw
                )
                self.get_logger().info(
                    f"Navigation halted! Holding at X={self.current_x:.2f}, "
                    f"Y={self.current_y:.2f}, Z={self.current_z:.2f}, "
                    f"Yaw={math.degrees(self.current_yaw):.1f} deg"
                )
            else:
                self.get_logger().info("Halted operations. State is now IDLE.")

        if should_save:
            self.get_logger().info("Stopping recording and auto-saving path to disk...")
            self.save_path_to_file(path_copy)

    def start_replay(self, reverse: bool = False):
        with self.lock:
            if not self.pose_received:
                self.get_logger().error(
                    "Cannot start replay: No position data received from MAVROS yet!"
                )
                return

        path = self.load_path_from_file()
        if not path:
            return

        if reverse:
            path.reverse()
            if REVERSE_FLIPS_HEADING:
                # Rotate recorded headings by 180 degrees (pi rad), normalized to [-pi, pi]
                path = [
                    (pt[0], pt[1], pt[2], math.atan2(math.sin(pt[3] + math.pi), math.cos(pt[3] + math.pi)))
                    for pt in path
                ]
            direction_str = "REVERSE"
        else:
            direction_str = "FORWARD"

        with self.lock:
            self.waypoints = path
            self.current_target = self.waypoints.pop(0)
            self.state = 'NAVIGATING'
            target = self.current_target
            mode = self.current_mode
            armed = self.is_armed

        self.get_logger().info(
            f"Starting {direction_str} replay ({len(path) + 1} total waypoints)."
        )
        if not armed or mode != "GUIDED":
            self.get_logger().warn(
                f"Vehicle is currently {'ARMED' if armed else 'DISARMED'} in {mode} mode. "
                f"Ensure it is ARMED and in GUIDED mode to move!"
            )
        self.get_logger().info(
            f"Heading to first coordinate: X={target[0]:.2f}, Y={target[1]:.2f}, "
            f"Z={target[2]:.2f}, Yaw={math.degrees(target[3]):.1f} deg"
        )

    # ------------------------------------------
    # 10Hz CONTROL LOOP
    # ------------------------------------------
    def control_loop(self):
        with self.lock:
            if self.state == 'IDLE' or not self.pose_received:
                return

            # --- RECORDING LOGIC ---
            if self.state == 'RECORDING':
                if len(self.recorded_path) == 0:
                    self.recorded_path.append(
                        (self.current_x, self.current_y, self.current_z, self.current_yaw)
                    )
                    self.get_logger().info("First waypoint dropped.")
                else:
                    last_x, last_y, last_z, last_yaw = self.recorded_path[-1]
                    dist = math.sqrt(
                        (self.current_x - last_x) ** 2 +
                        (self.current_y - last_y) ** 2 +
                        (self.current_z - last_z) ** 2
                    )
                    yaw_diff = abs(shortest_angular_distance(last_yaw, self.current_yaw))

                    # Drop a waypoint if moved 0.5m OR rotated by at least RECORD_YAW_DEG
                    if dist >= RECORD_DENSITY_METERS or yaw_diff >= math.radians(RECORD_YAW_DEG):
                        self.recorded_path.append(
                            (self.current_x, self.current_y, self.current_z, self.current_yaw)
                        )
                        self.get_logger().info(
                            f"Waypoint #{len(self.recorded_path)} dropped at "
                            f"X={self.current_x:.2f}, Y={self.current_y:.2f}, Z={self.current_z:.2f}, "
                            f"Yaw={math.degrees(self.current_yaw):.1f} deg"
                        )
                return

            # --- NAVIGATING LOGIC ---
            if self.state == 'NAVIGATING' and self.current_target is not None:
                target_x, target_y, target_z, target_yaw = self.current_target

                # 1. Broadcast the current 3D target coordinate + target heading
                self.publish_setpoint(target_x, target_y, target_z, target_yaw)

                # 2. Check 3D distance to waypoint
                dist = math.sqrt(
                    (target_x - self.current_x) ** 2 +
                    (target_y - self.current_y) ** 2 +
                    (target_z - self.current_z) ** 2
                )

                # 3. Smooth Glide Transition
                if dist <= ARRIVAL_RADIUS_METERS:
                    if len(self.waypoints) > 0:
                        self.current_target = self.waypoints.pop(0)
                        nxt = self.current_target
                        self.get_logger().info(
                            f"Gliding to next waypoint ({len(self.waypoints)} remaining): "
                            f"X={nxt[0]:.2f}, Y={nxt[1]:.2f}, Z={nxt[2]:.2f}, "
                            f"Yaw={math.degrees(nxt[3]):.1f} deg"
                        )
                    else:
                        self.state = 'IDLE'
                        self.current_target = None
                        self.get_logger().info(
                            "Route Complete! Vehicle is holding at final coordinate and heading."
                        )


def user_input_thread(node: RecordReplayNode):
    print("\n--- Record & Replay Navigator (4-DOF: X, Y, Z, Yaw) ---")
    print(f"CSV Storage Location: {PATH_FILENAME}")
    print("Commands:")
    print("  rec start   : Begin recording path and heading")
    print("  rec stop    : Stop recording and save to file")
    print("  rep fwd     : Replay path Forward (A to B)")
    print("  rep rev     : Replay path Reverse (B to A)")
    print("  stop        : Halt navigation (brakes vehicle) or stop & save recording")
    print("  q           : Arm")
    print("  e           : Disarm")
    print("  t           : Toggle Mode (MANUAL to/from GUIDED)")
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
                node.halt_all()
                rclpy.shutdown()
                break
            elif cmd == 'q':
                node.arm_vehicle(True)
            elif cmd == 'e':
                node.arm_vehicle(False)
            elif cmd == 't':
                node.toggle_mode()
            elif cmd == 'stop':
                node.halt_all()
            elif cmd == 'rec start':
                node.start_recording()
            elif cmd == 'rec stop':
                node.stop_recording()
            elif cmd == 'rep fwd':
                node.start_replay(reverse=False)
            elif cmd == 'rep rev':
                node.start_replay(reverse=True)
            else:
                print("Invalid command. Type 'rec start', 'rec stop', 'rep fwd', 'rep rev', or 'stop'.")

        except EOFError:
            break
        except Exception as e:
            print(f"Error processing command: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = RecordReplayNode()

    ui_thread = threading.Thread(target=user_input_thread, args=(node,), daemon=True)
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
