# robotx_cv

YOLO (TensorRT) detector: for each object, its class, score, box, LED state and distance.
It only subscribes; the camera is published elsewhere (`publish_image`, or a bag).

```text
/image_raw/compressed ─┐
/camera_info ──────────┴─► /detector ─► /<env>/cv/objects                 (robotx_cv/ObjectArray)
                                     └► /<env>/cv/debug_image/compressed  (boxes drawn, debug_image:=true)
```

| File | |
|---|---|
| `robotx_cv/detector.py` | ROS node: YOLO, then LED and distance per box, publish |
| `robotx_cv/light.py` | LED colour in a box (HSV), same light across frames, blink pattern |
| `robotx_cv/dock.py` | Dock face box -> its 2 windows (black frames, top) + indicator colour (strip, bottom) |
| `robotx_cv/ranging.py` | Distance from the real size and the camera calibration |
| `config/<env>.yaml` | Model and objects of one environment |
| `msg/` | `Object`, `ObjectArray` |

## Setup

Jetson JetPack 6, ROS 2 Humble, `ros-humble-vision-msgs`, Ultralytics with the Jetson CUDA torch
([guide](https://docs.ultralytics.com/guides/nvidia-jetson/)).

```bash
colcon build --symlink-install --packages-select robotx_cv && source install/setup.bash
```

## Train (server)

```bash
conda create -n robotx python=3.11 -y && conda activate robotx   # once
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128 && pip install ultralytics

cd ~/RobotX_2026/src/data   # data.yaml names = config/<env>.yaml classes
yolo detect train data=usv_buoy/data.yaml model=yolo11s.pt imgsz=640 epochs=150 patience=40 batch=32 \
  degrees=0 flipud=0 hsv_h=0.01 project=runs name=usv_v1       # uuv: yolo obb train ... model=yolo11s-obb.pt
yolo train resume model=runs/usv_v1/weights/last.pt              # resume
yolo val model=runs/usv_v1/weights/best.pt data=usv_buoy/data.yaml
```

## TensorRT (Jetson, once per model)

Copy `best.pt` to `models/usv.pt`. The engine only runs on the GPU it was built on.

```bash
yolo export model=models/usv.pt format=engine half=True 'imgsz=[384,640]' batch=1 device=0   # imgsz = env imgsz
```

## Run

```bash
# ros2 bag play /workspace/data/bags/lab_01 --loop   # needs /image_raw/compressed
ros2 launch robotx_cv detector.launch.py env:=uuv
# ros2 run robotx_cv detector.py --ros-args -p env:=uuv   # same, without the launch file
ros2 topic echo /uuv/cv/objects --field objects
```

The outputs are named after the env (one model per env): `/uuv/cv/...`, `/usv/cv/...`, `/coco/cv/...`;
for a config path, after the file name. The input topics stay as given.

### Parameters

| Parameter | Default | |
|---|---|---|
| `env` | `coco` | `uuv` / `usv` / `uav` / `coco`, or a config `.yaml` path; also names the outputs |
| `model` | from the env | Override the env model |
| `image_topic` | `/image_raw/compressed` | |
| `camera_info_topic` | `/camera_info` | Calibration for distance |
| `camera_info` | `config/camera/bull_camera.yaml` | Used until a valid `camera_info_topic` arrives |
| `conf` | `-1.0` | Min score; < 0 takes `conf:` of the env config, else 0.25 |
| `rate` | `15.0` | Detections per second, always on the newest frame. LED patterns need >= 10 Hz really achieved (5 Hz: flash only) |
| `debug_image` | `false` | Publish `/<env>/cv/debug_image/compressed` |

Editing `.py` / `.yaml` needs no rebuild (`--symlink-install`); editing `msg/` or adding a config does.

## Environments

One model per environment, one box type per model: `uuv` is `task: obb` (rotated boxes),
`usv`, `uav` and `coco` (stock `yolo11s`, bench test) are plain `detect`.

| `env` | Vehicle | Objects (LED) |
|---|---|---|
| `uuv` | UUV | **light_node** (red / green), pipe (the 3" pipeline) |
| `usv` | USV | robobuoy, **light_beacon**, color_indicator_red/green, dock_structure, **window** |
| `uav` | UAV | robobuoy, **light_beacon**, platform, circle_red/green/blue, tin, uav_pad |

`color_indicator` is not in `uav`: it is only visible from the side.

```yaml
objects:
  light_node: {size: 0.0445, dim: max, light: {colours: [RED, GREEN]}}  # real size (m), box side for distance, LED
  pipe:       {size: 0.0889, dim: min}                                 # {} = no distance
```

- Only the listed classes are published; other model classes are dropped (`pipe_stand`, `pipe_base` in `uuv`).
  Class names must match the model.
- `dim`: `w` / `h` (side closer to horizontal / vertical in the image), `max` (round objects),
  `min` (thickness of long objects).
- `light: true` looks for red, green and blue; `colours` restricts it.

### Labelling

Draw the box around the part the size refers to. Sizes are preliminary (handbook 2026-10-15).
In `uuv` OBB labels (`class x1 y1 x2 y2 x3 y3 x4 y4`), classes that need no rotation are plain boxes.

| Env | Class | Box around | Box | Size |
|---|---|---|---|---|
| `uuv` | `pipe` | one straight 3" run between elbows, tees included | rotated | Ø 88.9 mm |
| `uuv` | `pipe_stand`, `pipe_base` | the vertical 2" legs, the frames on the floor | rotated as seen | not published |
| `uuv` | `light_node` | the LED ring only | plain; rotated along the ellipse if clearly oblique | Ø 44.5 mm |
| `usv` | `light_beacon` | the LED pipe | plain | Ø 88.9 mm |
| `usv` | `window` | the hole with its black border | plain | 0.25 m |
| `usv` | `color_indicator_*` | the coloured cylinder | plain | ~135 x 128 mm |
| `usv` | `robobuoy` | the whole buoy, top cylinder included | plain | 0.43 m |
| `usv` | `dock_structure` | the whole object | plain | - |

Label objects with an LED both lit and unlit, same class, same box (not the glow): YOLO must
still find them in every state, otherwise their history restarts every off phase and the state
stays `unknown` (or wrongly `off`, if it only finds them unlit).

## Task 1 (light beacons only)

`task1.py` runs the Task 1 model alone: buoys, the state of the light beacon on top, distance. One config per
vehicle, `config/<vehicle>_task1.yaml`; outputs on `/<vehicle>/task1/` (`usv_task1` -> `/usv/task1/`).

```bash
ros2 launch robotx_cv task1.launch.py image_topic:=/zed/zed_node/left/color/rect/image/compressed \
  camera_info_topic:=/zed/zed_node/left/color/rect/camera_info depth_topic:=/depth/image_raw debug_image:=true
ros2 topic echo /usv/task1/detections --field detections
```

1. YOLO (`models/buoy_beacon.pt`): `robobuoy` boxes (the buoy only) and `light_beacon` boxes (the
   beacon on top, lit or not).
2. Per frame, LED colour of each buoy. Lit pixels: one channel >= 100 and 40 above both others
   (LEDs are primary colours; sky and water are blue AND green). In the `light_beacon` box over the
   buoy if there is one (`beacon_class`): lit pixels of the top colour / box, under 5 %: `OFF`.
   Else above the buoy box: `roi` is 80 % of the box width (tilted buoys move the beacon sideways),
   half its height, the lit pixels counted in a window 1/3 of the box wide slid across it; buoys
   under 25 px wide are not read. A steady coloured background (red umbrella) reads lit every frame:
   `unknown`, never `flashing_*`.
3. Same beacon across frames: nearest buoy box (up to 3 box sizes away: the boat rolls). Frames form lit / dark runs (misreads < 0.3 s merged).
   Confirmed after 3 lit + 3 dark runs of 1 ± 0.5 s (`flashing_<colour>`), or 6 s lit blue
   (`solid_blue`) / dark (`off`); `unknown` before. A gap > 0.5 s restarts it: a beacon only found
   while lit stays `unknown`, never `solid`.
4. Position from the depth camera: the depth at the box centroid (median of a small patch, from
   `depth_topic`, default `/depth/image_raw`, `16UC1` mm or `32FC1` m, aligned to the colour image) is
   deprojected with the `camera_info` intrinsics (`Ranger.deproject`, lens distortion removed) to a 3D
   point in the ROS camera axes (x forward, y left, z up; `ros_frame:=false`: optical axes).
   `distance` is its length. NaN if there is no valid depth at the centroid; the buoy size is not used.

`/usv/task1/detections` (`robotx_cv/DetectionArray`, header of the image), per object (`Detection`):
`class_name`, `score`, `id`, `bbox`, `state` (`off`, `flashing_red`, `flashing_green`,
`flashing_blue`, `solid_blue`, `unknown`), `distance`, `position` (camera, ROS axes: x forward, y left, z up; `ros_frame:=false` gives optical x right, y down, z forward). `Detection` is
generic (`state` '' for classes without one), for other vehicles and tasks. The debug image
(`/usv/task1/debug_image/compressed`) shows the roi (yellow), the beacon box or window read
(magenta), and the colour and lit % of each frame.

Pool bag with a real flashing red beacon (185 s, ~5 fps): `flashing_red` ~5 s after the buoy comes
into view, no wrong state; bags with painted red / green indicators: never `flashing_*`. Colour in
the beacon box and above the buoy agree on 287 / 288 frames; the beacon box also reads buoys
under 25 px. Comparison scripts: `data/buoy_colour_test/beacon_cmp/`.

### Live camera (ZED on the USV)

One terminal each. The ZED runs on the Jetson host; the rest in the `rov` container
(`docker exec -it rov bash && source /workspace/install/setup.bash`, host network, so it sees the ZED topics).

```bash
# 1. Jetson at full power, then the ZED with fixed exposure / white balance (auto shifts the LED hues)
sudo nvpmodel -m 0 && sudo jetson_clocks
ros2 launch zed_wrapper zed_camera.launch.py camera_model:=zed2 \
  ros_params_override_path:=$HOME/RobotX_2026/src/robotx_usv/config/zed.yaml

# 2. Topic names depend on the wrapper version: left/... or rgb/...
ros2 topic list | grep color/rect

# 3. Once per model, on the Jetson: the TensorRT engine of usv_task1.yaml (imgsz = config imgsz)
yolo export model=/workspace/models/buoy_beacon.pt format=engine half=True 'imgsz=[736,1280]' batch=1 device=0

# 4. Task 1 (config:=usv_task1 by default)
ros2 launch robotx_cv task1.launch.py \
  image_topic:=/zed/zed_node/left/color/rect/image/compressed \
  camera_info_topic:=/zed/zed_node/left/color/rect/camera_info debug_image:=true

# 5. Check
ros2 topic echo /usv/task1/detections --field detections
ros2 topic hz /usv/task1/detections                                            # >= 10 Hz
ros2 run rqt_image_view rqt_image_view /usv/task1/debug_image/compressed
```

The log must show `camera_info: 1920x1080 fx=...` at start; without it the distance uses
`config/camera/bull_camera.yaml`. No engine yet: add `model:=/workspace/models/buoy_beacon.pt` (slower).

## Output

`robotx_cv/ObjectArray`, same header as the image. Per object:

| Field | |
|---|---|
| `class_name`, `score` | YOLO class and confidence |
| `bbox` | pixels, original image; `center.theta` = rotation (rad, OBB), 0 for upright boxes |
| `parent`, `part`, `found` | parts of a `dock_face` (`window_left`, `window_right`: class `window`; `indicator`: class `dock_indicator`): index of their dock face in `objects`, which part, `found` false if placed from the layout (frame not seen). `-1`, `''`, true otherwise |
| `light` | `''` if the class has no LED, else a state below (`dock_indicator`: `red` / `green` steady) |
| `light_id` | same light across frames, `-1` if no LED |
| `colour` | colour of this frame only (`red`, `green`, `blue`, `off`; `''` can't tell), no delay |
| `distance` | m; `NaN` if no size, box touching the image edge (`dim: min`: its thickness), or < 12 px. A dock face and its parts share one depth: their size estimates weighted by size in px |
| `position` | m, camera frame (x right, y down, z forward); `NaN` like `distance` |

| `light` | Meaning |
|---|---|
| `red` / `green` / `blue` | steady > 2.5 s |
| `red_flash` ... | 1 s on / 1 s off, after ~4 s |
| `seq_red_blue` ... | c1 1 s, off 1 s, c2 1 s, off 2 s, after ~5-10 s |
| `off` | dark > 4 s (longer than any off phase of a pattern) |
| `unknown` | not enough history yet |

LED colour per frame: in the box, count the pixels both bright and saturated (blown-out white
cores and glare do not count) per allowed colour. Fewer than 5 % of the box: `OFF`; the top
colour under 2x the runner-up, or a box under 12 px: no sample (the light keeps its id).
Needs fixed exposure, gain and white balance.

`config/camera/bull_camera.yaml` is an approximation (80° FOV, no distortion): replace it with the
`camera_calibration` result, done in water for the UUV, and use the same file for the camera's `camera_info_url`.
