"""LED state of detected objects: colour in each frame, same light across frames, pattern over time.

States (RobotX 2026 timing): '<colour>' steady, '<colour>_flash' 1 s on / 1 s off,
'seq_<c1>_<c2>' c1 1 s, off 1 s, c2 1 s, off 2 s, 'off', 'unknown' (not enough history yet).
"""
from collections import deque
from itertools import count
from math import hypot

import cv2
import numpy as np

OFF = 'OFF'
HUES = {'RED': ((0, 10), (170, 179)), 'GREEN': ((45, 85),), 'BLUE': ((100, 130),)}  # OpenCV hue 0-179


def colour(frame, box, colours=tuple(HUES), s_min=120, v_min=180, min_ratio=0.05, dominance=2.0, min_px=12):
    """Colour of the LED in a (cx, cy, w, h, rotation rad) box: one of `colours`, OFF, or None (can't tell).

    Only bright AND saturated pixels count: glare and LED cores blown out to white are ignored,
    the coloured halo around them is what gets counted. The most frequent colour wins if it covers
    min_ratio of the box (else OFF) and has `dominance` times the pixels of the runner-up (else None).
    None also for boxes under min_px: a few JPEG-smeared pixels say nothing.
    """
    cx, cy, w, h, r = box
    if max(w, h) < min_px:
        return None
    H, W = frame.shape[:2]
    pts = cv2.boxPoints(((cx, cy), (w, h), np.degrees(r)))
    # Clip both ends: a negative index would wrap around in numpy.
    x0, y0 = np.clip(np.floor(pts.min(0)), 0, (W, H)).astype(int)
    x1, y1 = np.clip(np.ceil(pts.max(0)) + 1, 0, (W, H)).astype(int)
    patch = frame[y0:y1, x0:x1]
    if patch.size == 0:
        return None
    inside = np.zeros(patch.shape[:2], np.uint8)
    cv2.fillPoly(inside, [np.round(pts - (x0, y0)).astype(np.int32)], 1)
    if not inside.any():
        return None
    hue, s, v = cv2.split(cv2.cvtColor(patch, cv2.COLOR_BGR2HSV))
    hist = np.bincount(hue[(s >= s_min) & (v >= v_min) & (inside > 0)], minlength=180)
    counts = sorted(((sum(int(hist[a:b + 1].sum()) for a, b in HUES[c]), c) for c in colours), reverse=True)
    (n1, best), n2 = counts[0], counts[1][0] if len(counts) > 1 else 0
    if n1 < min_ratio * np.count_nonzero(inside):
        return OFF
    return best if n1 >= dominance * n2 else None


def runs(samples, min_seg=0.3):
    """[(t, colour)] -> [[colour, start, duration]]; runs shorter than min_seg are merged away."""
    starts = []
    for t, c in samples:
        if not starts or starts[-1][0] != c:
            starts.append((c, t))
    dt = (samples[-1][0] - samples[0][0]) / max(len(samples) - 1, 1)
    ends = [s for _, s in starts[1:]] + [samples[-1][0] + dt]
    out = []
    for (c, s), e in zip(starts, ends):
        if out and (e - s < min_seg or out[-1][0] == c):
            out[-1][2] += e - s
        else:
            out.append([c, s, e - s])
    return out


def decode(segs, tol=0.4, steady=2.5, off=4.0):
    """Pattern of the newest runs. The first and last runs are partial (window edge, ongoing)."""
    last_c, _, last_d = segs[-1]
    if last_c != OFF and last_d >= steady:
        return last_c.lower()
    if last_c == OFF and last_d >= off:
        return 'off'
    full = segs[1:-1]
    near = lambda d, x: abs(d - x) <= tol
    # Flash: 4 complete ~1 s runs alternating one colour with OFF.
    # A sequence always has a ~2 s OFF within any 4 runs, so it cannot match here.
    tail = full[-4:]
    lit = {c for c, _, _ in tail if c != OFF}
    if (len(tail) == 4 and len(lit) == 1 and all(near(d, 1) for _, _, d in tail)
            and all((a[0] == OFF) != (b[0] == OFF) for a, b in zip(tail, tail[1:]))):
        return f'{lit.pop().lower()}_flash'
    # Sequence: c1 ~1, OFF ~1, c2 ~1, OFF ~2 within the newest complete cycle.
    for i in range(len(full) - 4, max(len(full) - 8, -1), -1):
        (c1, _, d1), (o1, _, e1), (c2, _, d2), (o2, _, e2) = full[i:i + 4]
        if (OFF not in (c1, c2) and o1 == o2 == OFF
                and near(d1, 1) and near(e1, 1) and near(d2, 1) and near(e2, 2)):
            return f'seq_{c1.lower()}_{c2.lower()}'
    return 'unknown'


class Light:
    def __init__(self, lid, cls):
        self.id, self.cls = lid, cls
        self.cx = self.cy = self.seen = 0.0
        self.samples = deque()  # (t, colour)


class LightTracker:
    """Nearest box of the same class = same light. Enough for a few well-separated lights.

    hold: forget a light not seen for this long (s). window: colour history kept (s).
    max_dist: max jump between frames, in box sizes. max_gap: a longer gap restarts the decoding.
    """

    def __init__(self, hold=2.0, window=12.0, max_dist=1.0, max_gap=0.5):
        self.hold, self.window, self.max_dist, self.max_gap = hold, window, max_dist, max_gap
        self.lights, self.t, self.ids = {}, float('-inf'), count()

    def update(self, t, dets):
        """dets [(cls, cx, cy, w, h, colour)] at time t (s) -> [(light id, state)] in the same order.

        colour None (can't tell): the light keeps its track but gets no sample.
        """
        if t < self.t:  # time went back (bag replayed): start over
            self.lights.clear()
        self.t = t
        for lid in [lid for lid, l in self.lights.items() if t - l.seen > self.hold]:
            del self.lights[lid]
        # Greedy matching, closest pairs first; distance in box sizes works near and far.
        pairs = sorted((hypot(l.cx - cx, l.cy - cy) / max(w, h, 1.0), i, lid)
                       for i, (cls, cx, cy, w, h, _) in enumerate(dets)
                       for lid, l in self.lights.items() if l.cls == cls)
        match = {}
        for d, i, lid in pairs:
            if d > self.max_dist:
                break
            if i not in match and lid not in match.values():
                match[i] = lid
        out = []
        for i, (cls, cx, cy, _, _, c) in enumerate(dets):
            if i not in match:
                match[i] = next(self.ids)
                self.lights[match[i]] = Light(match[i], cls)
            light = self.lights[match[i]]
            light.cx, light.cy, light.seen = cx, cy, t
            if c is not None:
                light.samples.append((t, c))
            while light.samples and light.samples[0][0] < t - self.window:
                light.samples.popleft()
            out.append((light.id, self.state(light.samples)))
        return out

    def state(self, samples):
        """Decode only the newest stretch without a gap longer than max_gap."""
        s = list(samples)
        if not s:
            return 'unknown'
        k = next((i for i in range(len(s) - 1, 0, -1) if s[i][0] - s[i - 1][0] > self.max_gap), 0)
        return decode(runs(s[k:]))
