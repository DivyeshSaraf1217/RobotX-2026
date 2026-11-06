#!/usr/bin/env python3
"""Task 1: YOLO buoys, the light beacon above each -> /<vehicle>/task1/detections (state, distance).

The LED colour is read in the beacon box on top of the buoy if the model has `beacon_class`, else
(none found) in `roi` above the buoy box. Beacons are tracked by their buoy (bigger, steadier box).
"""
import os
from math import isnan

import cv2
import numpy as np
import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import CameraInfo, CompressedImage, Image
from ultralytics import YOLO

from robotx_cv.beacon import BeaconTracker, beacon_on, led_colour, roi
from robotx_cv.msg import Detection, DetectionArray
from robotx_cv.ranging import Ranger

NAN = float('nan')
STATE_BGR = {'flashing_red': (0, 0, 255), 'flashing_green': (0, 255, 0), 'flashing_blue': (255, 128, 0),
             'solid_blue': (255, 0, 0), 'off': (80, 80, 80), 'unknown': (255, 255, 255)}


def namespace(config):
    """usv_task1.yaml -> /usv/task1"""
    return '/' + os.path.splitext(os.path.basename(config))[0].replace('_', '/', 1)


class Task1(Node):
    def __init__(self):
        super().__init__('task1_cv')
        param = lambda name, default: self.declare_parameter(name, default).value
        share = get_package_share_directory('robotx_cv')
        config = param('config', 'usv_task1')
        path = config if config.endswith('.yaml') else os.path.join(share, 'config', f'{config}.yaml')
        with open(path) as f:
            cfg = yaml.safe_load(f)
        ns = namespace(path)
        model = param('model', '') or cfg['model']
        self.conf = param('conf', -1.0)
        if self.conf < 0:
            self.conf = float(cfg.get('conf', 0.25))
        self.imgsz = cfg['imgsz']
        self.cls = cfg.get('buoy_class', 'robobuoy')
        self.roi = cfg.get('roi', [0.1, -0.5, 0.9, 0.0])
        self.led = cfg.get('led') or {}
        self.beacon_cls = cfg.get('beacon_class', '')
        self.beacon_led = {**self.led, **(cfg.get('beacon_led') or {})}
        self.tracker = BeaconTracker(**(cfg.get('state') or {}))
        self.ranger = Ranger.from_yaml(
            param('camera_info', '') or os.path.join(share, 'config', 'camera', 'bull_camera.yaml'))
        self.ros_frame = param('ros_frame', True)
        self.info = None
        self.latest = None
        self.depth = None

        if not os.path.isfile(model):
            raise FileNotFoundError(f'Model {model} not found: train/export it or pass model:=...')
        self.model = YOLO(model, task=cfg.get('task', 'detect'))
        self.model.predict(np.zeros((*self.imgsz, 3), np.uint8), imgsz=self.imgsz, verbose=False)  # warm up
        if self.cls not in self.model.names.values():
            raise ValueError(f'{model} has no class {self.cls!r}: {sorted(self.model.names.values())}')
        if self.beacon_cls and self.beacon_cls not in self.model.names.values():
            self.get_logger().warn(f'{model} has no class {self.beacon_cls!r}: colour above the buoys only')
            self.beacon_cls = ''

        self.pub = self.create_publisher(DetectionArray, f'{ns}/detections', 10)
        self.debug_pub = (self.create_publisher(CompressedImage, f'{ns}/debug_image/compressed', 1)
                          if param('debug_image', False) else None)
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        topic = param('image_topic', '/image_raw/compressed')
        self.create_subscription(CompressedImage, topic, self.on_image, qos)
        self.create_subscription(CameraInfo, param('camera_info_topic', '/camera_info'), self.on_info, qos)
        self.depth_topic = param('depth_topic', '/depth/image_raw')
        self.create_subscription(Image, self.depth_topic, self.on_depth, qos)
        # Only the newest frame is processed, so a slow model never builds up lag.
        rate = param('rate', 15.0)
        self.create_timer(1.0 / rate, self.on_timer)
        self.get_logger().info(
            f'{model} ({self.cls}) <- {topic} @ {rate} Hz -> {ns}/detections | position: depth image '
            f'{self.depth_topic} + camera_info, {"ROS frame (x fwd, y left, z up)" if self.ros_frame else "optical frame"}')

    def on_info(self, msg):
        info = (tuple(msg.k), tuple(msg.d), msg.width, msg.height)
        if msg.k[0] <= 0 or info == self.info:  # all zeros = the publisher has no calibration
            return
        self.info = info
        self.ranger = Ranger(msg.k, msg.d or [0.0] * 5, msg.width, msg.height)
        self.get_logger().info(f'camera_info: {msg.width}x{msg.height} fx={msg.k[0]:.1f}')

    def on_image(self, msg):
        self.latest = msg

    def on_depth(self, msg):
        """Depth image (16UC1 mm or 32FC1 m) -> float32 metres, NaN where invalid."""
        if msg.encoding in ('16UC1', 'mono16'):
            dt, scale = np.uint16, 0.001
        elif msg.encoding == '32FC1':
            dt, scale = np.float32, 1.0
        else:
            self.get_logger().error(f'depth encoding {msg.encoding!r} not supported', throttle_duration_sec=5.0)
            return
        raw = np.frombuffer(msg.data, dt).reshape(msg.height, msg.step // np.dtype(dt).itemsize)[:, :msg.width]
        depth = raw.astype(np.float32) * scale
        depth[~np.isfinite(depth) | (depth <= 0)] = np.nan
        self.depth = depth

    def depth_at(self, box, width, height):
        """Depth (m, along the optical axis) at the box centroid: median of a small patch (a quarter of
        the box, at least 5 px) so a hole or a noisy pixel does not matter. None without valid depth.
        The depth image must be aligned to the colour image (any resolution, same field of view)."""
        if self.depth is None:
            return None
        dh, dw = self.depth.shape
        cx, cy = box[0] * dw / width, box[1] * dh / height
        hw, hh = max(box[2] * dw / width / 8, 2.5), max(box[3] * dh / height / 8, 2.5)
        patch = self.depth[max(int(cy - hh), 0):int(cy + hh) + 1, max(int(cx - hw), 0):int(cx + hw) + 1]
        patch = patch[np.isfinite(patch)]
        return float(np.median(patch)) if patch.size else None

    def on_timer(self):
        msg, self.latest = self.latest, None
        if msg is None:
            return
        frame = cv2.imdecode(np.frombuffer(msg.data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            self.get_logger().error('JPEG decode failed', throttle_duration_sec=5.0)
            return
        self.detect(frame, msg.header)

    def detect(self, frame, header):
        r = self.model.predict(frame, conf=self.conf, imgsz=self.imgsz, verbose=False)[0]
        names = [r.names[c] for c in r.boxes.cls.int().tolist()]
        boxes = [(*b, 0.0) for b in r.boxes.xywh.tolist()]
        dets = [(s, b) for n, s, b in zip(names, r.boxes.conf.tolist(), boxes) if n == self.cls]
        beacons = [b for n, b in zip(names, boxes) if n == self.beacon_cls]
        leds = [self.read_led(frame, box, beacons) for _, box in dets]
        # The image time keeps bags right; some sources leave the stamp at 0.
        t = (header.stamp.sec + header.stamp.nanosec * 1e-9) or self.get_clock().now().nanoseconds * 1e-9
        states = self.tracker.update(t, [(*box[:4], led[0]) for (_, box), led in zip(dets, leds)])
        ranger = self.ranger.fit(frame.shape[1], frame.shape[0])

        out = DetectionArray(header=header)
        for (score, box), (bid, state) in zip(dets, states):
            d = Detection(class_name=self.cls, score=score, id=bid, state=state,
                          distance=NAN, position=Point(x=NAN, y=NAN, z=NAN))
            d.bbox.center.position.x, d.bbox.center.position.y = box[0], box[1]
            d.bbox.size_x, d.bbox.size_y = box[2], box[3]
            z = self.depth_at(box, frame.shape[1], frame.shape[0])
            if z:
                # centroid pixel + measured depth + camera_info intrinsics -> 3D point
                p = ranger.deproject(box[0], box[1], z, self.ros_frame)
                d.position = Point(x=p[0], y=p[1], z=p[2])
                d.distance = float(np.linalg.norm(p))
            out.detections.append(d)
        self.pub.publish(out)

        labels = [f'{d.id} {d.state}' + ('' if isnan(d.distance) else
                  f' x{d.position.x:.2f} y{d.position.y:.2f} z{d.position.z:.2f}m') + f' ({d.score:.2f})'
                  for d in out.detections]
        if self.depth is None:
            self.get_logger().warn(f'no depth image on {self.depth_topic} yet: position is NaN',
                                   throttle_duration_sec=5.0)
        if self.debug_pub and self.debug_pub.get_subscription_count():
            self.publish_debug(frame, header, out.detections, dets, leds, labels)
        self.get_logger().info(f'{len(labels)} buoys: {", ".join(labels) or "-"} | {sum(r.speed.values()):.1f} ms',
                               throttle_duration_sec=5.0)

    def read_led(self, frame, buoy, beacons):
        """-> (colour, lit ratio, area read, in the beacon box)"""
        k = beacon_on(buoy, beacons, self.roi)
        if k is None:
            return (*led_colour(frame, buoy, self.roi, **self.led), False)
        return (*led_colour(frame, beacons[k], (0.0, 0.0, 1.0, 1.0), **self.beacon_led), True)

    def publish_debug(self, frame, header, detections, dets, leds, labels):
        """State-coloured buoy boxes; magenta: the area the colour was read in; yellow: the search area
        above the buoy when there is no beacon box."""
        img = frame.copy()
        for d, (_, box), (c, ratio, win, in_box), text in zip(detections, dets, leds, labels):
            draw_box(img, box, STATE_BGR[d.state], 2)
            if not in_box:
                draw_box(img, roi(box, self.roi), (0, 255, 255), 1)
            draw_box(img, win, (255, 0, 255), 2)
            cv2.putText(img, f'{text} [{c or "?"} {ratio:.0%}]', (int(box[0] - box[2] / 2), max(int(box[1] - box[3] / 2) - 6, 14)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        jpg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])[1]
        self.debug_pub.publish(CompressedImage(header=header, format='jpeg', data=jpg.tobytes()))


def draw_box(img, box, bgr, thickness):
    cx, cy, w, h = box[:4]
    cv2.rectangle(img, (int(cx - w / 2), int(cy - h / 2)), (int(cx + w / 2), int(cy + h / 2)), bgr, thickness)


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = Task1()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
