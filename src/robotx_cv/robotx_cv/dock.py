"""Parts of a detected dock face (front panel of a docking bay structure): two black-framed
windows and the colour indicator, from the official layout.

Build guide "Docking Bay Structure" (RobotX 2026), front panel 1000 x 1000 mm:

    +----------------------------+
    |  +-----+                   |   window_left: black frame 280 x 360 (opening 210 x 290),
    |  |     |                   |                x 140-420, y 70-430 from the top-left
    |  |     |        +-----+    |
    |  +-----+        |     |    |   window_right: x 580-860, y 320-680
    |                 |     |    |   (16x16 RGB LED matrix behind each opening)
    |                 +-----+    |
    |                            |
    |           +----+           |   indicator: 160 x 160 opening, x 420-580, y 840-1000;
    +-----------+----+-----------+   the red / green colour indicator stands in it

The dock face box is upright (cx, cy, w, h, rotation 0) around the panel; part boxes the same.
"""
import cv2
import numpy as np

from robotx_cv.light import colour

# Fractions of the panel: (x0, y0, x1, y1), x from the left, y from the top.
LAYOUT = {
    'window_left': (0.14, 0.07, 0.42, 0.43),
    'window_right': (0.58, 0.32, 0.86, 0.68),
    'indicator': (0.42, 0.84, 0.58, 1.00),
}
SIDES = ('window_left', 'window_right')


def expected(box, part):
    """Where `part` is in the image for a dock face box, as (x0, y0, x1, y1) px."""
    cx, cy, w, h, _ = box
    fx0, fy0, fx1, fy1 = LAYOUT[part]
    x0, y0 = cx - w / 2, cy - h / 2
    return x0 + fx0 * w, y0 + fy0 * h, x0 + fx1 * w, y0 + fy1 * h


def to_box(x0, y0, x1, y1):
    return ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0.0)


def is_quad(c, eps=0.08, min_ratio=0.6):
    """Contour ~ a convex 4-gon with opposite sides of similar length: a rectangle seen from any
    angle is a parallelogram-ish quad. eps: polygon fit tolerance, fraction of the perimeter."""
    q = cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
    if len(q) != 4 or not cv2.isContourConvex(q):
        return False
    p = q.reshape(4, 2).astype(float)
    side = [np.hypot(*(p[i] - p[(i + 1) % 4])) for i in range(4)]
    return all(min(side[i], side[i + 2]) >= min_ratio * max(side[i], side[i + 2]) for i in (0, 1))


def find_windows(frame, roi, block=51, C=8, dark=0.9, work_px=240, min_area=0.02, max_area=0.45,
                 min_fill=0.55, min_solidity=0.75, max_aspect=1.8):
    """Black frames inside roi (x0, y0, x1, y1) -> [(x0, y0, x1, y1)] px, largest first.

    The crop is scaled to work_px on its long side (far boards: frames 1-2 px thick). Dark = C under
    the local mean (block px, so a board shaded to one side does not merge with its frames) and under
    `dark` x the board's white (80th percentile). Outer contours of the dark pixels; kept: a quad,
    solid, not touching the roi edge (that is background past the board). The inside of a frame
    may be dark, lit or see-through: only the outline counts.
    """
    H, W = frame.shape[:2]
    x0, y0 = max(int(roi[0]), 0), max(int(roi[1]), 0)
    x1, y1 = min(int(np.ceil(roi[2])), W), min(int(np.ceil(roi[3])), H)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return []
    k = work_px / max(x1 - x0, y1 - y0)
    gray = cv2.cvtColor(cv2.resize(frame[y0:y1, x0:x1], None, fx=k, fy=k, interpolation=cv2.INTER_CUBIC),
                        cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    mask = cv2.adaptiveThreshold(gray, 1, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, block, C)
    mask &= (gray < dark * np.percentile(gray, 80)).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = mask.shape
    found = []
    for c in contours:
        bx, by, bw, bh = cv2.boundingRect(c)
        if bx <= 0 or by <= 0 or bx + bw >= w or by + bh >= h:
            continue
        area = cv2.contourArea(c)
        if (not min_area * w * h <= area <= max_area * w * h or max(bw, bh) > max_aspect * min(bw, bh)
                or area < min_fill * bw * bh or area < min_solidity * cv2.contourArea(cv2.convexHull(c))
                or not is_quad(c)):
            continue
        found.append((area, (x0 + bx / k, y0 + by / k, x0 + (bx + bw) / k, y0 + (by + bh) / k)))
    return [f for _, f in sorted(found, reverse=True)]


def parts(frame, box, split=0.75, max_shift=0.2):
    """Dock face box -> [(part, box, found, colour)] for window_left, window_right, indicator.

    Frames are searched over the top `split` of the box; each side takes the frame nearest to where
    the layout puts it, if within max_shift x the box height (a tilted or yawed panel moves them a bit).
    found False: no frame there (far, blurred, glare), the box is the layout position: the LED can
    still be read in it. colour: the indicator's ('RED', 'GREEN', OFF, None = can't tell); None for
    the windows (their LED colours are read by the detector, with the LED thresholds).
    """
    cx, cy, w, h, _ = box
    top = (cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + split * h)
    frames = find_windows(frame, top)
    out = []
    for side in SIDES:
        e = to_box(*expected(box, side))
        near = sorted((np.hypot(f[0] + f[2] - 2 * e[0], f[1] + f[3] - 2 * e[1]) / 2, i) for i, f in enumerate(frames))
        if near and near[0][0] <= max_shift * h:
            out.append((side, to_box(*frames.pop(near[0][1])), True, None))
        else:
            out.append((side, e, False, None))
    ind = to_box(*expected(box, 'indicator'))
    out.append(('indicator', ind, True, colour(frame, ind, ('RED', 'GREEN'), s_min=80, v_min=60, min_ratio=0.1)))
    return out
