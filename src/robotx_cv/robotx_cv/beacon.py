"""Task 1 light beacons (RobotX 2026): LED colour in the beacon box on top of a buoy (or in an area
above the buoy box), state over time.

Beacon modes (handbook 3.3.2 and the official beacon firmware): off, flashing red / green / blue
(1 s on, 1 s off), solid blue. Each frame gives a colour (or OFF); consecutive frames form lit / dark
runs. A state is only confirmed after `cycles` lit and `cycles` dark runs of ~1 s (flashing), or
`cycles` full periods of one kind (solid blue: always lit, off: always dark).
"""
from collections import Counter, deque
from itertools import count
from math import hypot

import cv2
import numpy as np

OFF = 'OFF'
BGR = ('BLUE', 'GREEN', 'RED')  # channel order of OpenCV images
STATES = ('off', 'flashing_red', 'flashing_green', 'flashing_blue', 'solid_blue', 'unknown')


def roi(box, frac):
    """Area given as fractions (x0, y0, x1, y1) of an upright box (cx, cy, w, h, rot); < 0 or > 1 is
    outside it (y0 = -0.5, y1 = 0: half the box height above it)."""
    cx, cy, w, h, _ = box
    x0, y0, x1, y1 = frac
    left, top = cx - w / 2, cy - h / 2
    return (left + (x0 + x1) / 2 * w, top + (y0 + y1) / 2 * h, (x1 - x0) * w, (y1 - y0) * h, 0.0)


def beacon_on(buoy, beacons, frac):
    """Index of the beacon box on top of this buoy: centre in the buoy's `frac` area widened by half
    its size, bottom nearest the buoy top. None if there is none."""
    cx, cy, w, h, _ = roi(buoy, frac)
    top = buoy[1] - buoy[3] / 2
    near = [(abs(bx - buoy[0]) + abs(by + bh / 2 - top), k) for k, (bx, by, bw, bh, _) in enumerate(beacons)
            if abs(bx - cx) < w and abs(by - cy) < h]
    return min(near)[1] if near else None


def lit_masks(p, excess, v_min, blue_green=None):
    """(B, G, R) masks of lit LED pixels: the channel >= v_min and `excess` above both others (blue:
    `blue_green` above green, a blue LED looks cyan-blue to the camera). Sky and water (blue AND
    green), white PVC, glare and blown-out cores are not lit; a far LED mixed with the white pipe
    (pink, pale green) still is."""
    b, g, r = p[..., 0], p[..., 1], p[..., 2]
    bg = excess if blue_green is None else blue_green
    return ((b >= v_min) & (b - g >= bg) & (b - r >= excess),
            (g >= v_min) & (g - b >= excess) & (g - r >= excess),
            (r >= v_min) & (r - b >= excess) & (r - g >= excess))


def blown_colour(p, blown, min_ratio, ring_excess):
    """Over-exposed LED core (all channels >= blown, not touching the edge: that is sky, ceiling,
    glare) over min_ratio of p -> (colour of the ring around it if `ring_excess` above the others,
    else None, core ratio); no core -> None."""
    core = (p.min(axis=2) >= blown).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
    H, W = core.shape
    keep = (st[:, 0] > 0) & (st[:, 1] > 0) & (st[:, 0] + st[:, 2] < W) & (st[:, 1] + st[:, 3] < H)
    keep[0] = False  # background label
    core = keep[lab].astype(np.uint8)
    ratio = float(core.mean())
    if ratio < min_ratio:
        return None
    ring = cv2.dilate(core, np.ones((5, 5), np.uint8)).astype(bool) & ~core.astype(bool)
    m = p[ring].mean(axis=0)
    c = int(np.argmax(m))
    return (BGR[c] if m[c] - np.delete(m, c).max() >= ring_excess else None), ratio


def led_colour(frame, box, frac, window=0.333, excess=40, v_min=100, min_ratio=0.05, dominance=2.0,
               min_box=25, blue_green=None, blown=0, ring_excess=20):
    """LED in `frac` of `box` -> (RED / GREEN / BLUE / OFF / None, lit ratio, window box).

    A window `window` x the box width slides across `frac` (wide, for tilted buoys); the window with
    the most lit pixels of one colour (lit_masks) is the beacon, ratio = those / window pixels. Under
    min_ratio: OFF, unless blown > 0 and there is an over-exposed core (far LEDs are only that, see
    blown_colour): its colour or None, never OFF. None (can't tell): box under min_box px wide,
    area off the image, or the top colour under `dominance` x the runner-up.
    The beacon box itself: frac (0, 0, 1, 1), window 1, min_box 0.
    """
    cx, cy, w, h, _ = roi(box, frac)
    H, W = frame.shape[:2]
    x0, y0 = int(np.clip(cx - w / 2, 0, W)), int(np.clip(cy - h / 2, 0, H))
    x1, y1 = int(np.clip(np.ceil(cx + w / 2), 0, W)), int(np.clip(np.ceil(cy + h / 2), 0, H))
    if box[2] < min_box or x1 <= x0 or y1 <= y0:
        return None, 0.0, (cx, cy, min(window * box[2], w), h, 0.0)
    p = frame[y0:y1, x0:x1].astype(np.int16)
    k = int(np.clip(round(window * box[2]), 1, x1 - x0))
    lit = np.stack(lit_masks(p, excess, v_min, blue_green)).sum(axis=1)  # per colour, per column
    cum = np.pad(np.cumsum(lit, axis=1), ((0, 0), (1, 0)))
    cols = cum[:, k:] - cum[:, :-k]  # per colour, per window position
    c, x = np.unravel_index(np.argmax(cols), cols.shape)
    n1, n2 = cols[c, x], np.delete(cols[:, x], c).max()
    ratio = float(n1) / (k * (y1 - y0))
    win = (x0 + x + k / 2 if n1 else (x0 + x1) / 2, (y0 + y1) / 2, k, y1 - y0, 0.0)
    if ratio < min_ratio:
        core = blown_colour(p, blown, min_ratio, ring_excess) if blown else None
        return (*core, win) if core else (OFF, ratio, win)
    return (BGR[c] if n1 >= dominance * n2 else None), ratio, win


def runs(samples, min_run=0.3, max_gap=0.5):
    """[(t, colour)] -> [[lit, start, duration, [colours]]]; None samples are skipped, runs shorter
    than min_run between two of the other kind are a misread and merged into them. Only the samples
    after the last gap > max_gap without a colour count (a dark second read as None is no lit run)."""
    seq = [(t, c) for t, c in samples if c is not None]
    k = next((i for i in range(len(seq) - 1, 0, -1) if seq[i][0] - seq[i - 1][0] > max_gap), 0)
    seq = seq[k:]
    out = []
    for t, c in seq:
        if out and out[-1][0] == (c != OFF):
            out[-1][3].append(c)
        else:
            out.append([c != OFF, t, 0.0, [c]])
    if not out:
        return out
    dt = (seq[-1][0] - seq[0][0]) / max(len(seq) - 1, 1)
    for r, nxt in zip(out, out[1:] + [None]):
        r[2] = (nxt[1] if nxt else seq[-1][0] + dt) - r[1]
    i = 1
    while i < len(out) - 1:
        if out[i][2] < min_run:
            prev, glitch, nxt = out[i - 1], out[i], out.pop(i + 1)
            prev[2] += glitch[2] + nxt[2]
            prev[3] += glitch[3] + nxt[3]
            out.pop(i)
            i = max(i - 1, 1)
        else:
            i += 1
    return out


def decode(samples, cycles=3, flash=1.0, tol=0.5, min_run=0.3, min_share=0.7, max_gap=0.5):
    """[(t, colour)] without long gaps, oldest first -> one of STATES.

    flashing_<c>: the newest runs hold >= cycles lit and >= cycles dark runs, each ~`flash` s (± tol;
    the oldest and the ongoing one may be shorter, they are cut by the history / not over yet).
    solid_blue / off: one lit (blue) / dark run for >= cycles full periods (2 * flash each).
    """
    rs = runs(samples, min_run, max_gap)
    if rs and rs[-1][2] < min_run:  # the ongoing run may still be a misread
        rs = rs[:-1]
    if not rs:
        return 'unknown'
    lit, _, d, cs = rs[-1]
    if d >= cycles * 2 * flash:
        if not lit:
            return 'off'
        return 'solid_blue' if majority(cs, min_share) == 'BLUE' else 'unknown'  # only blue is ever solid
    counted = []
    for k in range(len(rs) - 1, -1, -1):
        partial = k in (0, len(rs) - 1)
        if rs[k][2] > flash + tol or (not partial and rs[k][2] < flash - tol):
            break
        counted.append(rs[k])
    if sum(r[0] for r in counted) < cycles or sum(not r[0] for r in counted) < cycles:
        return 'unknown'
    c = majority([c for r in counted if r[0] for c in r[3]], min_share)
    return f'flashing_{c.lower()}' if c else 'unknown'


def majority(colours, min_share):
    """The most common colour if it is >= min_share of them, else None."""
    if not colours:
        return None
    best, n = Counter(colours).most_common(1)[0]
    return best if n >= min_share * len(colours) else None


class BeaconTracker:
    """Nearest box = same beacon (a few well-separated beacons).

    hold: forget a beacon unseen this long (s). max_dist: max jump between frames, in box sizes.
    max_gap: a longer gap in the samples restarts the decoding (a flashing beacon missed while
    dark would otherwise look solid). history: samples kept (s).
    """

    def __init__(self, hold=2.0, max_dist=1.0, max_gap=0.5, history=10.0, **decode_kw):
        self.hold, self.max_dist, self.max_gap, self.history = hold, max_dist, max_gap, history
        self.decode_kw = decode_kw
        self.tracks, self.t, self.ids = {}, float('-inf'), count()

    def update(self, t, dets):
        """dets [(cx, cy, w, h, colour)] at time t (s) -> [(id, state)] in the same order."""
        if t < self.t:  # bag replayed from the start
            self.tracks.clear()
        self.t = t
        for i in [i for i, tr in self.tracks.items() if t - tr['seen'] > self.hold]:
            del self.tracks[i]
        pairs = sorted((hypot(tr['cx'] - cx, tr['cy'] - cy) / max(w, h, 1.0), k, i)
                       for k, (cx, cy, w, h, _) in enumerate(dets) for i, tr in self.tracks.items())
        match = {}
        for d, k, i in pairs:
            if d > self.max_dist:
                break
            if k not in match and i not in match.values():
                match[k] = i
        out = []
        for k, (cx, cy, _, _, c) in enumerate(dets):
            if k not in match:
                match[k] = next(self.ids)
                self.tracks[match[k]] = {'samples': deque()}
            tr = self.tracks[match[k]]
            tr.update(cx=cx, cy=cy, seen=t)
            s = tr['samples']
            if s and t - s[-1][0] > self.max_gap:
                s.clear()
            s.append((t, c))
            while s[0][0] < t - self.history:
                s.popleft()
            out.append((match[k], decode(list(s), max_gap=self.max_gap, **self.decode_kw)))
        return out
