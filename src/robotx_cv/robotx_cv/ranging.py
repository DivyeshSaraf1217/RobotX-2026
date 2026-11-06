"""Distance from the known real size of an object and the camera calibration."""
from math import hypot

import cv2
import numpy as np
import yaml


class Ranger:
    """Pinhole + distortion: Z = real size / size in normalised (undistorted) image units."""

    def __init__(self, K, D, width, height, edge=2, min_px=12):
        self.K, self.D = np.asarray(K, np.float64).reshape(3, 3), np.asarray(D, np.float64)
        self.width, self.height, self.edge, self.min_px = width, height, edge, min_px

    @classmethod
    def from_yaml(cls, path, **kw):
        """camera_info YAML as written by `camera_calibration` (ost.yaml)."""
        with open(path) as f:
            c = yaml.safe_load(f)
        return cls(c['camera_matrix']['data'], c['distortion_coefficients']['data'],
                   c['image_width'], c['image_height'], **kw)

    def fit(self, width, height):
        """Same camera at another resolution (aspect must match)."""
        if (width, height) == (self.width, self.height):
            return self
        s = np.diag([width / self.width, height / self.height, 1.0])
        return Ranger(s @ self.K, self.D, width, height, self.edge, self.min_px)

    def __call__(self, box, size, dim='max'):
        """box (cx, cy, w, h, rotation rad) px, size m, dim w|h|max|min -> (distance, x, y, z) or None.

        w / h: the side closer to horizontal / vertical in the image (an OBB model may return an
        upright box as w vertical). None when the box is too small or cut off by the image edge;
        for dim min (thickness of long objects) only the thickness has to be in the image.
        """
        cx, cy, w, h, r = box
        if max(w, h) < self.min_px:
            return None
        c = np.array([cx, cy])
        u, v = np.array([np.cos(r), np.sin(r)]) * w / 2, np.array([-np.sin(r), np.cos(r)]) * h / 2
        pts = np.array([c - u, c + u, c - v, c + v, c])
        n = cv2.undistortPoints(pts.reshape(-1, 1, 2), self.K, self.D).reshape(-1, 2)
        sides = [(np.linalg.norm(n[1] - n[0]), pts[:2]), (np.linalg.norm(n[3] - n[2]), pts[2:4])]
        if abs(np.sin(r)) > abs(np.cos(r)):  # the h side is the more horizontal one
            sides.reverse()
        s, ends = {'w': sides[0], 'h': sides[1], 'max': max(sides, key=lambda x: x[0]),
                   'min': min(sides, key=lambda x: x[0])}[dim]
        must_see = ends if dim == 'min' else np.array([c - u - v, c - u + v, c + u - v, c + u + v])
        if ((must_see <= self.edge).any() or (must_see[:, 0] >= self.width - self.edge).any()
                or (must_see[:, 1] >= self.height - self.edge).any()):
            return None
        z = size / s
        x, y = n[4] * z
        return hypot(x, y, z), float(x), float(y), float(z)

    def deproject(self, u, v, z, ros_frame=True):
        """Pixel (u, v) at depth z (m, along the optical axis) -> (x, y, z) m, lens distortion removed.

        X = (undistorted normalised ray) * z, so the point lies exactly on the pixel's ray.
        ros_frame: x forward, y left, z up (camera body axes); else optical: x right, y down, z forward.
        """
        xn, yn = cv2.undistortPoints(np.array([[[u, v]]], np.float64), self.K, self.D).reshape(2)
        x, y = float(xn * z), float(yn * z)
        return (float(z), -x, -y) if ros_frame else (x, y, float(z))

    def at_depth(self, cx, cy, z):
        """Pixel (cx, cy) at depth z (m, along the optical axis) -> (distance, x, y, z)."""
        x, y = cv2.undistortPoints(np.array([[[cx, cy]]], np.float64), self.K, self.D).reshape(2) * z
        return hypot(x, y, z), float(x), float(y), float(z)
