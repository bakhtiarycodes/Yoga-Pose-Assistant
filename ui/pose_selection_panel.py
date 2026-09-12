from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QTabWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal
import os

from core.pose_manager import PoseManager


BEGINNER_POSE_ORDER = [
    "Bound angle pose (Baddha Konasana)",
    "Cobra Pose (Bhujangasana)",
    "Hero Pose (Virasana)",
    "Plank Pose (Kumbhakasana)",
    "Warrior 2 (Virabhadrasana lI)",
]


class PoseSelectionPanel(QWidget):
    pose_selected = pyqtSignal(str)

    def __init__(self, json_folder=None):
        super().__init__()
        self.pose_manager = PoseManager()
        self.json_folder = json_folder or self.pose_manager.pose_directory

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Select Yoga Pose")
        label.setFont(QFont("Arial", 24, weight=QFont.Bold))
        layout.addWidget(label)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.all_list = QListWidget()
        self.beginner_list = QListWidget()
        self.intermediate_list = QListWidget()
        self.advanced_list = QListWidget()

        self._add_tab("All", self.all_list)
        self._add_tab("Beginner", self.beginner_list)
        self._add_tab("Intermediate", self.intermediate_list)
        self._add_tab("Advanced", self.advanced_list)

        self.load_poses()

    def _add_tab(self, title, list_widget):
        page = QWidget()
        page_layout = QVBoxLayout()
        page.setLayout(page_layout)
        page_layout.addWidget(list_widget)
        self.tab_widget.addTab(page, title)

        list_widget.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item):
        self.pose_selected.emit(item.text())

    def _sort_beginner_poses(self, poses):
        order_index = {name: index for index, name in enumerate(BEGINNER_POSE_ORDER)}

        def sort_key(name):
            if name in order_index:
                return (0, order_index[name])
            return (1, name.lower())

        return sorted(poses, key=sort_key)

    def load_poses(self):
        self.all_list.clear()
        self.beginner_list.clear()
        self.intermediate_list.clear()
        self.advanced_list.clear()

        try:
            if not os.path.exists(self.json_folder):
                print(f"[ERROR] Pose folder not found: {self.json_folder}")
                return

            files = [
                f for f in os.listdir(self.json_folder)
                if f.endswith(".json") and f != "Instructions.json"
            ]
            files.sort()

            beginner_poses = []

            for filename in files:
                try:
                    pose_name = os.path.splitext(filename)[0]
                    metadata = self.pose_manager.get_instruction_data(pose_name)
                    level = "unknown"
                    if metadata and isinstance(metadata, dict):
                        level = metadata.get("level", "unknown").lower()

                    self.all_list.addItem(pose_name)
                    if level == "beginner":
                        beginner_poses.append(pose_name)
                    elif level == "intermediate":
                        self.intermediate_list.addItem(pose_name)
                    elif level == "advanced":
                        self.advanced_list.addItem(pose_name)
                except Exception as e:
                    print(f"[ERROR] Failed to load pose entry '{filename}': {e}")

            for pose_name in self._sort_beginner_poses(beginner_poses):
                self.beginner_list.addItem(pose_name)
        except Exception as e:
            print(f"[ERROR] load_poses failed: {e}")

    def get_poses_by_level(self, level):
        level = (level or "all").strip().lower()
        if level == "beginner":
            widget = self.beginner_list
        elif level == "intermediate":
            widget = self.intermediate_list
        elif level == "advanced":
            widget = self.advanced_list
        else:
            widget = self.all_list

        return [widget.item(i).text() for i in range(widget.count())]

    def get_selected_pose(self):
        current_page = self.tab_widget.currentWidget()
        if not current_page:
            return None
        current_list = current_page.findChild(QListWidget)
        if current_list:
            selected_items = current_list.selectedItems()
            if selected_items:
                return selected_items[0].text()
        return None