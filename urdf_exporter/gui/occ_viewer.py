from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt
import numpy as np


class OccViewerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("3D Viewer")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.layout.addWidget(self.info_text)

        self._meshes = []

    def add_mesh(self, mesh, color=(0.8, 0.8, 0.8), transform=None, name=""):
        info = f"Mesh: {name}\n"
        if mesh is not None:
            info += f"  Vertices: {len(mesh.vertices)}\n"
            info += f"  Faces: {len(mesh.faces)}\n"
            info += f"  Volume: {mesh.volume:.4f}\n"
            info += f"  Bounding Box: {mesh.bounds}\n"
        if transform is not None:
            info += f"  Transform: {transform.shape}\n"
        info += "\n"

        self.info_text.append(info)
        self._meshes.append((mesh, name))

    def add_meshes_from_assembly(self, assembly, color_map=None):
        if color_map is None:
            color_map = {}

        def process_assembly(asm):
            for part in asm.parts:
                part_color = color_map.get(part.name, (0.6 + len(self._meshes) * 0.1 % 0.4,
                                                       0.6 + len(self._meshes) * 0.15 % 0.4,
                                                       0.6 + len(self._meshes) * 0.2 % 0.4))
                self.add_mesh(part.mesh, part_color, part.transform, part.name)

            for sub_asm in asm.subassemblies:
                process_assembly(sub_asm)

        process_assembly(assembly)

    def clear(self):
        self.info_text.clear()
        self._meshes = []

    def zoom_in(self):
        pass

    def zoom_out(self):
        pass

    def fit_all(self):
        pass

    def rotate(self):
        pass

    def pan(self):
        pass

    def set_background_color(self, color):
        pass

    def get_selected_shape(self):
        return None