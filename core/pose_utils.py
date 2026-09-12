import math

GREEN_THRESHOLD = 0.06
YELLOW_THRESHOLD = 0.12

POSE_CONNECTIONS = [
    ("nose", "left_eye_inner"),
    ("left_eye_inner", "left_eye"),
    ("left_eye", "left_eye_outer"),
    ("nose", "right_eye_inner"),
    ("right_eye_inner", "right_eye"),
    ("right_eye", "right_eye_outer"),
    ("nose", "left_shoulder"),
    ("nose", "right_shoulder"),
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("left_wrist", "left_thumb"),
    ("left_wrist", "left_index"),
    ("left_wrist", "left_pinky"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
    ("right_wrist", "right_thumb"),
    ("right_wrist", "right_index"),
    ("right_wrist", "right_pinky"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("left_ankle", "left_heel"),
    ("left_heel", "left_foot_index"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("right_ankle", "right_heel"),
    ("right_heel", "right_foot_index"),
]


def get_reference_landmarks(pose_data):
    if pose_data is None:
        return {}

    if isinstance(pose_data, dict) and "landmarks" in pose_data:
        source = pose_data["landmarks"]
    else:
        source = pose_data or {}

    landmarks = {}
    for name, point in source.items():
        if not isinstance(point, (list, tuple)) or len(point) < 2:
            continue
        try:
            landmarks[name] = (float(point[0]), float(point[1]))
        except (TypeError, ValueError):
            continue

    return landmarks


def extract_user_landmarks(results, mp_pose):
    if results is None or results.pose_landmarks is None:
        return {}

    landmarks = {}
    try:
        for landmark_id, lm in enumerate(results.pose_landmarks.landmark):
            name = mp_pose.PoseLandmark(landmark_id).name.lower()
            landmarks[name] = (lm.x, lm.y)
    except Exception as e:
        print(f"[ERROR] extract_user_landmarks failed: {e}")

    return landmarks


def landmark_distance(user_point, reference_point):
    dx = user_point[0] - reference_point[0]
    dy = user_point[1] - reference_point[1]
    return math.sqrt(dx * dx + dy * dy)


def distance_to_color(distance):
    if distance <= GREEN_THRESHOLD:
        return (0, 255, 0)
    if distance <= YELLOW_THRESHOLD:
        return (0, 255, 255)
    return (0, 0, 255)


def distance_to_score(distance):
    if distance <= GREEN_THRESHOLD:
        return 1.0
    if distance <= YELLOW_THRESHOLD:
        return 0.5
    return 0.0


def compare_pose_landmarks(reference_pose, user_landmarks):
    try:
        ref_landmarks = get_reference_landmarks(reference_pose)
        if not ref_landmarks or not user_landmarks:
            return {}, 0.0

        colors = {}
        scores = []

        for name, ref_point in ref_landmarks.items():
            if name not in user_landmarks:
                continue

            distance = landmark_distance(user_landmarks[name], ref_point)
            colors[name] = {
                "color": distance_to_color(distance),
                "distance": distance,
            }
            scores.append(distance_to_score(distance))

        if not scores:
            return colors, 0.0

        accuracy = (sum(scores) / len(scores)) * 100
        return colors, accuracy
    except Exception as e:
        print(f"[ERROR] compare_pose_landmarks failed: {e}")
        return {}, 0.0


def angle_between_points(a, b, c):
    """
    محاسبه زاویه ∠ABC بین سه نقطه
    a, b, c = (x, y)
    خروجی: زاویه بر حسب درجه
    """
    ab = (a[0]-b[0], a[1]-b[1])
    cb = (c[0]-b[0], c[1]-b[1])

    dot = ab[0]*cb[0] + ab[1]*cb[1]
    mag_ab = math.sqrt(ab[0]**2 + ab[1]**2)
    mag_cb = math.sqrt(cb[0]**2 + cb[1]**2)

    if mag_ab * mag_cb == 0:
        return 0

    cos_angle = dot / (mag_ab * mag_cb)
    cos_angle = max(-1, min(1, cos_angle))

    angle = math.degrees(math.acos(cos_angle))

    return angle