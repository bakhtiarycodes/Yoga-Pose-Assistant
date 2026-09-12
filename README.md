# Yoga Pose Assistant

A desktop application that helps you practice yoga with real-time pose feedback. Using your webcam, MediaPipe detects your body landmarks and compares them to stored reference poses. Color-coded skeleton overlays and an accuracy score show how closely you match each pose.

## Features

- **Live pose detection** — MediaPipe Pose tracks your body in real time from a webcam feed.
- **28 reference yoga poses** — Pre-loaded landmark data for common asanas, grouped by difficulty.
- **Visual feedback** — Gray skeleton shows the target pose; your skeleton turns green, yellow, or red per landmark based on alignment.
- **Pose matching accuracy** — A 0–100% score reflects how well your pose matches the reference.
- **Pose instructions** — Benefits, difficulty level, and step-by-step guidance for each pose.
- **Guided yoga programs** — Automated sessions with configurable hold time, rest time, and repetitions for Beginner, Intermediate, and Advanced levels.
- **Capture and save** — Freeze a frame with overlays and save it to `data/captured_images/`.
- **Built-in user guide** — Onboarding dialog with tips for best results (optional on startup).

## Tech Stack

| Component | Library |
|-----------|---------|
| Desktop UI | [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) |
| Webcam & image processing | [OpenCV](https://opencv.org/) |
| Pose estimation | [MediaPipe Pose](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker) |
| Numerical operations | [NumPy](https://numpy.org/) |

## Requirements

- **Python** 3.9, 3.10, 3.11, or 3.12
- A **webcam** (built-in or USB)
- Enough room in front of the camera to show your **full body** (head to feet)

## Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd yoga_pose_assistant
```

### 2. Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

From the project root:

```bash
python main.py
```

The window opens maximized. A user guide may appear on first launch; you can disable it with the checkbox at the bottom of that dialog.

## Quick Start

1. **Select a pose** from the left panel (tabs: All, Beginner, Intermediate, Advanced).
2. Click **▶ Start Camera** to begin the live feed.
3. Stand so your **full body** is visible in the frame.
4. Align yourself with the **gray reference skeleton** overlaid on the video.
5. Watch your **colored skeleton** and **Pose Matching Accuracy** in the right panel:
   - **Green** — landmark matches the reference well
   - **Yellow** — close, needs a small adjustment
   - **Red** — far from the reference; adjust that body part

## User Interface

```
┌─────────────────┬──────────────────────────────────┬─────────────────┐
│  Pose Selection │         Camera View              │  Status Panel   │
│  (left)         │    (reference + live skeleton)   │  FPS, accuracy  │
│                 ├──────────────────────────────────┤  program timer  │
│                 │      Instructions (bottom)       │  reference img  │
│                 ├──────────────────────────────────┤                 │
│                 │  Start | Stop | Capture | Save   │                 │
└─────────────────┴──────────────────────────────────┴─────────────────┘
```

### Toolbar buttons

| Button | Action |
|--------|--------|
| ▶ Start Camera | Opens the webcam and starts pose detection |
| ■ Stop Camera | Stops the feed and releases the camera |
| 📸 Capture | Freezes the current frame (with overlays) on screen |
| 💾 Save | Saves the last captured image to `data/captured_images/` |
| ❓ User Guide | Opens the in-app help dialog |

### Guided yoga program

In the right panel:

1. Choose a **Program Level** (Beginner, Intermediate, or Advanced).
2. Set **Hold Time** (seconds per pose), **Rest Time** (break between poses), and **Repetitions**.
3. Click **Start Program** — the app cycles through poses with a countdown timer.
4. During rest periods, skeleton drawing pauses and a preview of the next pose may appear.
5. Click **Stop Program** to end the session at any time.

Default hold/rep settings change automatically when you switch program level.

## How Pose Matching Works

1. **Reference landmarks** are loaded from JSON files in `assets/reference_poses/`. Each file stores normalized `(x, y)` coordinates for MediaPipe body landmarks (e.g. shoulders, hips, knees).

2. **Live detection** — MediaPipe processes each webcam frame and extracts your landmark positions.

3. **Comparison** — For each shared landmark, the Euclidean distance to the reference point is computed:
   - Distance ≤ 0.06 → green (score 1.0)
   - Distance ≤ 0.12 → yellow (score 0.5)
   - Distance > 0.12 → red (score 0.0)

4. **Accuracy** — The percentage is the average landmark score × 100.

Reference pose JSON accepts either format:

```json
{ "landmarks": { "nose": [0.15, 0.31], ... } }
```

or a flat landmark map:

```json
{ "nose": [0.15, 0.31], ... }
```

## Project Structure

```
yoga_pose_assistant/
├── main.py                      # Application entry point
├── requirements.txt
├── README.md
├── core/
│   ├── pose_detector.py         # MediaPipe Pose wrapper
│   ├── pose_manager.py          # Load poses & instructions from JSON
│   ├── pose_renderer.py         # Draw reference & user skeletons
│   └── pose_utils.py            # Landmark comparison & scoring
├── ui/
│   ├── main_window.py           # Main window & program logic
│   ├── camera_widget.py         # Webcam feed & stats
│   ├── pose_selection_panel.py  # Pose list with difficulty tabs
│   ├── instruction_panel.py     # Pose instructions display
│   ├── status_panel.py          # Metrics & guided program controls
│   ├── user_guide_dialog.py     # In-app help
│   └── styles.py                # Application stylesheet
├── assets/
│   └── reference_poses/         # Pose landmark JSON + Instructions.json
└── data/
    ├── captured_images/         # Saved captures (created at runtime)
    └── poses/                   # Optional reference images (.png, .jpg)
```

## Included Poses

28 poses with landmark data are included, for example:

| Beginner | Intermediate | Advanced |
|----------|--------------|----------|
| Bound Angle Pose | Boat Pose | Crane Pose |
| Bridge Pose | Bow Pose | Lord Shiva's Pose |
| Cat / Cow Pose | Camel Pose | Monkey Pose |
| Cobra Pose | Half Moon Pose | Plow Pose |
| Downward Facing Dog | Revolved Triangle | Warrior 3 |
| Easy Pose | Table Pose | |
| Hero Pose | Warrior 2 | |
| Plank Pose | | |
| Warrior 1 | | |

Full metadata (level, benefits, instructions) lives in `assets/reference_poses/Instructions.json`.

## Tips for Best Results

- Use **good lighting** and a plain background when possible.
- Stand **far enough** from the camera that head, arms, and legs are all visible.
- Select a pose before or after starting the camera — both work.
- Read the **instructions panel** for alignment and breathing cues.
- Aim for **green landmarks** and rising accuracy before capturing your best pose.

## Troubleshooting

| Issue | Suggested fix |
|-------|----------------|
| Camera does not open | Close other apps using the webcam. On Linux, check camera permissions. |
| Low confidence / no skeleton | Improve lighting; step back so your full body is in frame. |
| Low accuracy | Reference poses are normalized; mirror your body to match the gray skeleton orientation. |
| `pip install mediapipe` fails | Use Python 3.9–3.12. On Apple Silicon, ensure you use a native ARM Python build. |
| Pose file not found | Pose names must match JSON filenames in `assets/reference_poses/` exactly. |
| Save does nothing | Capture a frame first with **📸 Capture**, then click **💾 Save**. |

## Adding a New Pose

1. Record landmark coordinates (normalized 0–1) for a pose, or export from an existing MediaPipe session.
2. Save as `assets/reference_poses/Your Pose Name.json`.
3. Add an entry to `assets/reference_poses/Instructions.json` with `level`, `benefits`, and `instructions`.
4. Optionally add a reference image under `data/poses/`.

## License

This project is provided as-is for educational and personal use. Check individual library licenses (PyQt5, OpenCV, MediaPipe) for commercial deployment requirements.
