#!/usr/bin/env python3
"""YOLO on /image_raw/compressed -> /<env>/cv/objects: class, score, box, LED state, distance."""
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
from sensor_msgs.msg import CameraInfo, CompressedImage
from ultralytics import YOLO

from robotx_cv.dock import parts as dock_parts
from robotx_cv.light import HUES, LightTracker, colour
from robotx_cv.msg import Object, ObjectArray
from robotx_cv.ranging import Ranger

NAN = float('nan')


def px_size(box, dim):
    """Side of an upright box (px) that `dim` measures."""
    w, h = box[2], box[3]
    return {'w': w, 'h': h, 'max': max(w, h), 'min': min(w, h)}[dim]


class Detector(Node):
    def __init__(self):
        super().__init__('detector')
        param = lambda name, default: self.declare_parameter(name, default).value
        share = get_package_share_directory('robotx_cv')
        # Environment = one model + its objects: config/<env>.yaml, or a path to such a file.
        env = param('env', 'coco')
        with open(env if env.endswith('.yaml') else os.path.join(share, 'config', f'{env}.yaml')) as f:
            cfg = yaml.safe_load(f)
        name = os.path.splitext(os.path.basename(env))[0]
        model = param('model', '') or cfg['model']
        task = cfg.get('task', 'detect')  # detect (upright boxes) | obb (rotated boxes)
        self.conf = param('conf', -1.0)  # < 0: the env's `conf`, else 0.25
        if self.conf < 0:
            self.conf = float(cfg.get('conf', 0.25))
        self.imgsz = cfg.get('imgsz', [384, 640])  # [h, w], must equal the engine's export imgsz
        # Only these classes are published; other model classes (e.g. pipe supports) are dropped.
        self.objects = {n: s or {} for n, s in (cfg.get('objects') or {}).items()}
        # LED colours to look for per class: `light: true` = all, `light: {colours: [RED, GREEN]}`.
        self.colours = {}
        for n, s in self.objects.items():
            light = s.get('light')
            if light:
                cs = tuple(c.upper() for c in light.get('colours', HUES)) if isinstance(light, dict) else tuple(HUES)
                if not cs or set(cs) - set(HUES):
                    raise ValueError(f'{n}: light colours must be among {list(HUES)}, got {list(cs)}')
                self.colours[n] = cs
        # Dock faces split into windows + indicator (dock.py): `parts: true` or `parts: {split: 0.75}`.
        # The windows are published as `window` (its entry: size, LED colours), the indicator as
        # `dock_indicator` (painted, red / green).
        self.parts = {}
        for n, s in self.objects.items():
            p = s.get('parts')
            if p:
                self.parts[n] = {'split': p.get('split', 0.75)} if isinstance(p, dict) else {}
        if self.parts and 'window' not in self.objects:
            raise ValueError(f'{sorted(self.parts)} have parts: list `window` in objects too')
        # Calibration file until the first valid /camera_info.
        self.ranger = Ranger.from_yaml(
            param('camera_info', '') or os.path.join(share, 'config', 'camera', 'bull_camera.yaml'))
        self.info = None
        self.lights = LightTracker()
        self.latest = None

        if not os.path.isfile(model):
            raise FileNotFoundError(f'Model {model} (env {env}) not found: train/export it or pass model:=...')
        self.model = YOLO(model, task=task)
        self.model.predict(np.zeros((*self.imgsz, 3), np.uint8), imgsz=self.imgsz, verbose=False)  # warm up
        missing = set(self.objects) - set(self.model.names.values()) - ({'window'} if self.parts else set())
        if missing:
            self.get_logger().warn(f'Not in the model: {sorted(missing)}')

        # One model per environment, so the outputs are named after it: /uuv/cv/objects, ...
        self.pub = self.create_publisher(ObjectArray, f'/{name}/cv/objects', 10)
        self.debug_pub = (self.create_publisher(CompressedImage, f'/{name}/cv/debug_image/compressed', 1)
                          if param('debug_image', False) else None)
        qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        topic = param('image_topic', '/image_raw/compressed')
        self.create_subscription(CompressedImage, topic, self.on_image, qos)
        self.create_subscription(CameraInfo, param('camera_info_topic', '/camera_info'), self.on_info, qos)
        # Only the newest frame is processed, so a slow model never builds up lag.
        rate = param('rate', 15.0)
        self.create_timer(1.0 / rate, self.on_timer)
        self.get_logger().info(f'{env}: {model} ({task}) <- {topic} @ {rate} Hz -> /{name}/cv/objects')

    def on_info(self, msg):
        info = (tuple(msg.k), tuple(msg.d), msg.width, msg.height)
        if msg.k[0] <= 0 or info == self.info:  # all zeros = the publisher has no calibration
            return
        self.info = info
        self.ranger = Ranger(msg.k, msg.d or [0.0] * 5, msg.width, msg.height)
        self.get_logger().info(f'camera_info: {msg.width}x{msg.height} fx={msg.k[0]:.1f}')

    def on_image(self, msg):
        self.latest = msg

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
        # boxes: (cx, cy, w, h, rotation rad), pixels of the original image; rotation 0 for upright boxes
        b = r.obb if r.obb is not None else r.boxes
        xywhr = b.xywhr.tolist() if r.obb is not None else [[*x, 0.0] for x in b.xywh.tolist()]
        dets = [(r.names[c], score, box) for c, score, box in zip(b.cls.int().tolist(), b.conf.tolist(), xywhr)
                if r.names[c] in self.objects]
        # Dock faces: their parts (dock.py) join the detections after all model boxes.
        # parent: index of the dock face, -1 for model boxes. painted: indicator colour of this frame.
        n_yolo = len(dets)
        parent, part, found, painted = [-1] * n_yolo, [''] * n_yolo, [True] * n_yolo, {}
        for i, (n, score, box) in enumerate(dets[:n_yolo]):
            if n not in self.parts:
                continue
            for name, pbox, seen, c in dock_parts(frame, box, **self.parts[n]):
                if name == 'indicator':
                    painted[len(dets)] = c
                dets.append(('dock_indicator' if name == 'indicator' else 'window', score, list(pbox)))
                parent.append(i)
                part.append(name)
                found.append(seen)
        names, scores, boxes = (list(x) for x in zip(*dets)) if dets else ([], [], [])
        specs = [self.objects.get(n, {}) for n in names]
        out = ObjectArray(header=header)
        for i, (name, score, (cx, cy, w, h, rot)) in enumerate(zip(names, scores, boxes)):
            o = Object(class_name=name, score=score, parent=parent[i], part=part[i], found=found[i],
                       light_id=-1, distance=NAN, position=Point(x=NAN, y=NAN, z=NAN))
            o.bbox.center.position.x, o.bbox.center.position.y, o.bbox.center.theta = cx, cy, rot
            o.bbox.size_x, o.bbox.size_y = w, h
            out.objects.append(o)

        # LED: colour in this frame, then the pattern over time. The image time keeps bags right;
        # some sources leave the stamp at 0. The indicator is tracked the same way (steady red / green).
        t = (header.stamp.sec + header.stamp.nanosec * 1e-9) or self.get_clock().now().nanoseconds * 1e-9
        lit = [i for i, n in enumerate(names) if n in self.colours or i in painted]
        seen_colour = [painted[i] if i in painted else colour(frame, boxes[i], self.colours[names[i]]) for i in lit]
        states = self.lights.update(t, [(names[i], *boxes[i][:4], c) for i, c in zip(lit, seen_colour)])
        for i, c, (lid, state) in zip(lit, seen_colour, states):
            o = out.objects[i]
            o.light_id, o.light, o.colour = lid, state, '' if c is None else c.lower()

        # Distance from the real size. A dock face and its parts are on one panel, so they share one
        # depth: the size estimates of the face and of its windows seen, weighted by their size in px
        # (error ~ 1 px / size; close up the face leaves the image and the windows remain).
        # Parts placed from the layout get that depth too.
        ranger = self.ranger.fit(frame.shape[1], frame.shape[0])
        own = [ranger(box, s['size'], s.get('dim', 'max')) if s.get('size') and found[i] else None
               for i, (s, box) in enumerate(zip(specs, boxes))]
        groups = {i: [i] for i, n in enumerate(names[:n_yolo]) if n in self.parts}
        for k, p in enumerate(parent):
            if p >= 0:
                groups[p].append(k)
        depth = {}
        for members in groups.values():
            est = [(own[k][3], px_size(boxes[k], specs[k].get('dim', 'max')) ** 2) for k in members if own[k]]
            if est:
                z = sum(z * w for z, w in est) / sum(w for _, w in est)
                depth.update((k, z) for k in members)
        for i, o in enumerate(out.objects):
            rng = ranger.at_depth(boxes[i][0], boxes[i][1], depth[i]) if i in depth else own[i]
            if rng:
                o.distance, o.position = rng[0], Point(x=rng[1], y=rng[2], z=rng[3])
        self.pub.publish(out)

        labels = [' '.join(p for p in (o.class_name, o.light, '' if isnan(o.distance) else f'{o.distance:.1f}m')
                           if p) + f' ({o.score:.2f})' for o in out.objects]
        if self.debug_pub and self.debug_pub.get_subscription_count():
            img = r.plot(labels=False)
            # Dock parts: windows green if seen, yellow if from the layout; indicator blue.
            for i, (cx, cy, w, h, _) in enumerate(boxes[n_yolo:], n_yolo):
                cv2.rectangle(img, (int(cx - w / 2), int(cy - h / 2)), (int(cx + w / 2), int(cy + h / 2)),
                              (255, 0, 0) if i in painted else (0, 255, 0) if found[i] else (0, 255, 255), 2)
            for box, text in zip(boxes, labels):
                x, y = cv2.boxPoints(((box[0], box[1]), (box[2], box[3]), np.degrees(box[4]))).min(0)
                cv2.putText(img, text, (int(x), max(int(y) - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            jpg = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])[1]
            self.debug_pub.publish(CompressedImage(header=header, format='jpeg', data=jpg.tobytes()))
        self.get_logger().info(f'{len(labels)} obj: {", ".join(labels) or "-"} | {sum(r.speed.values()):.1f} ms',
                               throttle_duration_sec=5.0)


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = Detector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
