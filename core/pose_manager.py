import os
import json


class PoseManager:

    def __init__(self):

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        self.pose_directory = os.path.join(
            project_root,
            "assets",
            "reference_poses"
        )

    def load_pose(self, pose_name):

        filename = f"{pose_name}.json"

        pose_path = os.path.join(
            self.pose_directory,
            filename
        )

        print(f"[INFO] Loading pose: {pose_path}")

        if not os.path.exists(pose_path):

            print(f"[ERROR] Pose file not found: {pose_path}")
            return None

        try:

            with open(
                pose_path,
                "r",
                encoding="utf-8"
            ) as file:

                pose_data = json.load(file)

            # Normalize pose format: accept either
            # 1) { "landmarks": { ... } }
            # 2) { "nose": [x,y], ... } (top-level landmarks map)
            if isinstance(pose_data, dict):
                if "landmarks" in pose_data and isinstance(pose_data["landmarks"], dict):
                    normalized = pose_data
                else:
                    # detect if dict looks like a landmarks mapping (values are lists of numbers)
                    all_lists = all(
                        isinstance(v, list) and len(v) >= 2
                        for v in pose_data.values()
                    ) if pose_data else False

                    if all_lists:
                        normalized = {"landmarks": pose_data}
                    else:
                        normalized = pose_data
            else:
                normalized = pose_data

            print("[SUCCESS] Pose loaded successfully")

            return normalized

        except Exception as e:

            print(f"[ERROR] {e}")

            return None

    def _load_instructions_data(self):
        if getattr(self, "_instructions_data", None) is not None:
            return self._instructions_data

        instructions_path = os.path.join(self.pose_directory, "Instructions.json")
        if not os.path.exists(instructions_path):
            print(f"[ERROR] Instructions file not found: {instructions_path}")
            self._instructions_data = {}
            return self._instructions_data

        try:
            with open(instructions_path, "r", encoding="utf-8") as file:
                self._instructions_data = json.load(file)
        except Exception as e:
            print(f"[ERROR] Failed to load instructions: {e}")
            self._instructions_data = {}

        return self._instructions_data

    def _build_instruction_lookup(self):
        data = self._load_instructions_data()
        return {
            self._normalize_key(key): value
            for key, value in data.items()
        }

    def _resolve_pose_key(self, pose_name):
        normalized_pose = self._normalize_key(pose_name)
        aliases = {
            "triangle pose (utthita trikonasana)": "Triangle Pose (Trikonasana)",
            "warrior 1 (virabhadrasana i)": "Warrior I (Virabhadrasana I)",
            "warrior 2 (virabhadrasana li)": "Warrior II (Virabhadrasana II)",
            "warrior 3 (virabhadrasana lli)": "Warrior III (Virabhadrasana III)",
            "plank pose (kumbhakasana)": "Plank Pose (Phalakasana)",
            "garland pose (chaturanga dandasana)": "Garland Pose (Malasana)",
            "four limbed staff pose (chaturanga dandasana)": "Four‑Limbed Staff Pose (Chaturanga Dandasana)"
        }
        if normalized_pose in aliases:
            return self._normalize_key(aliases[normalized_pose])
        return normalized_pose

    def get_instruction_data(self, pose_name):
        try:
            lookup = self._build_instruction_lookup()
            normalized_pose = self._resolve_pose_key(pose_name)

            if normalized_pose in lookup:
                return lookup[normalized_pose]

            for key, value in lookup.items():
                if normalized_pose in key or key in normalized_pose:
                    return value

            target_tokens = set(normalized_pose.split())
            best_match = None
            best_score = 0.0
            for key, value in lookup.items():
                key_tokens = set(key.split())
                if not key_tokens:
                    continue
                shared = target_tokens & key_tokens
                score = len(shared) / len(key_tokens)
                if score > best_score:
                    best_score = score
                    best_match = value

            if best_match and best_score >= 0.5:
                return best_match
        except Exception as e:
            print(f"[ERROR] get_instruction_data failed for '{pose_name}': {e}")

        return None

    def load_instructions(self, pose_name):
        data = self.get_instruction_data(pose_name)
        if data is None:
            print(f"[WARN] No instructions found for pose: {pose_name}")
            return None
        return self._format_instruction(data)

    def _format_instruction(self, data):
        if not isinstance(data, dict):
            return None

        level = data.get("level", "")
        benefits = data.get("benefits", "")
        instructions = data.get("instructions", "")

        parts = []
        if level:
            parts.append(f"level: {level}")
        if benefits:
            parts.append(f"benefits: {benefits}")
        if instructions:
            parts.append(f"instructions: {instructions}")

        return "\n".join(parts) if parts else None


    def _normalize_key(self, text):
        if not isinstance(text, str):
            return ""
        cleaned = text.replace("_", " ").replace("-", " ")
        cleaned = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in cleaned)
        return " ".join(cleaned.split())
