from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QDoubleSpinBox, QCheckBox, QGroupBox, QLabel,
                             QPushButton, QColorDialog)
from PyQt5.QtCore import Qt

from urdf_exporter.core.link_model import Link, Origin, Inertia


class LinkEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._link = None
        self._on_changed_callback = None

        self.layout = QVBoxLayout(self)

        self.name_group = QGroupBox("Link Name")
        self.name_layout = QFormLayout(self.name_group)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.name_layout.addRow("Name:", self.name_edit)
        self.layout.addWidget(self.name_group)

        self.origin_group = QGroupBox("Origin")
        self.origin_layout = QFormLayout(self.origin_group)
        self.origin_x = QDoubleSpinBox()
        self.origin_x.setRange(-1000, 1000)
        self.origin_x.setDecimals(4)
        self.origin_y = QDoubleSpinBox()
        self.origin_y.setRange(-1000, 1000)
        self.origin_y.setDecimals(4)
        self.origin_z = QDoubleSpinBox()
        self.origin_z.setRange(-1000, 1000)
        self.origin_z.setDecimals(4)
        self.roll = QDoubleSpinBox()
        self.roll.setRange(-180, 180)
        self.roll.setDecimals(4)
        self.pitch = QDoubleSpinBox()
        self.pitch.setRange(-180, 180)
        self.pitch.setDecimals(4)
        self.yaw = QDoubleSpinBox()
        self.yaw.setRange(-180, 180)
        self.yaw.setDecimals(4)

        self.origin_layout.addRow("X:", self.origin_x)
        self.origin_layout.addRow("Y:", self.origin_y)
        self.origin_layout.addRow("Z:", self.origin_z)
        self.origin_layout.addRow("Roll:", self.roll)
        self.origin_layout.addRow("Pitch:", self.pitch)
        self.origin_layout.addRow("Yaw:", self.yaw)
        self.layout.addWidget(self.origin_group)

        self.mass_group = QGroupBox("Physical Properties")
        self.mass_layout = QFormLayout(self.mass_group)
        self.mass_edit = QDoubleSpinBox()
        self.mass_edit.setRange(0, 10000)
        self.mass_edit.setDecimals(4)
        self.mass_layout.addRow("Mass (kg):", self.mass_edit)
        self.layout.addWidget(self.mass_group)

        self.inertia_group = QGroupBox("Inertia")
        self.inertia_layout = QFormLayout(self.inertia_group)
        self.ixx = QDoubleSpinBox()
        self.ixx.setRange(0, 1000)
        self.ixx.setDecimals(6)
        self.ixy = QDoubleSpinBox()
        self.ixy.setRange(-1000, 1000)
        self.ixy.setDecimals(6)
        self.ixz = QDoubleSpinBox()
        self.ixz.setRange(-1000, 1000)
        self.ixz.setDecimals(6)
        self.iyy = QDoubleSpinBox()
        self.iyy.setRange(0, 1000)
        self.iyy.setDecimals(6)
        self.iyz = QDoubleSpinBox()
        self.iyz.setRange(-1000, 1000)
        self.iyz.setDecimals(6)
        self.izz = QDoubleSpinBox()
        self.izz.setRange(0, 1000)
        self.izz.setDecimals(6)

        self.inertia_layout.addRow("Ixx:", self.ixx)
        self.inertia_layout.addRow("Ixy:", self.ixy)
        self.inertia_layout.addRow("Ixz:", self.ixz)
        self.inertia_layout.addRow("Iyy:", self.iyy)
        self.inertia_layout.addRow("Iyz:", self.iyz)
        self.inertia_layout.addRow("Izz:", self.izz)
        self.layout.addWidget(self.inertia_group)

        self.base_checkbox = QCheckBox("Set as Base Link")
        self.base_checkbox.stateChanged.connect(self._on_base_changed)
        self.layout.addWidget(self.base_checkbox)

        self.color_button = QPushButton("Set Color")
        self.color_button.clicked.connect(self._on_color_clicked)
        self.layout.addWidget(self.color_button)

        self.layout.addStretch()

        self.origin_x.valueChanged.connect(self._on_origin_changed)
        self.origin_y.valueChanged.connect(self._on_origin_changed)
        self.origin_z.valueChanged.connect(self._on_origin_changed)
        self.roll.valueChanged.connect(self._on_origin_changed)
        self.pitch.valueChanged.connect(self._on_origin_changed)
        self.yaw.valueChanged.connect(self._on_origin_changed)
        self.mass_edit.valueChanged.connect(self._on_mass_changed)
        self.ixx.valueChanged.connect(self._on_inertia_changed)
        self.ixy.valueChanged.connect(self._on_inertia_changed)
        self.ixz.valueChanged.connect(self._on_inertia_changed)
        self.iyy.valueChanged.connect(self._on_inertia_changed)
        self.iyz.valueChanged.connect(self._on_inertia_changed)
        self.izz.valueChanged.connect(self._on_inertia_changed)

    def set_link(self, link: Link):
        self._link = link
        self._update_ui()

    def _update_ui(self):
        if self._link is None:
            return

        self.name_edit.setText(self._link.name)
        self.origin_x.setValue(self._link.origin.x)
        self.origin_y.setValue(self._link.origin.y)
        self.origin_z.setValue(self._link.origin.z)
        self.roll.setValue(self._link.origin.roll)
        self.pitch.setValue(self._link.origin.pitch)
        self.yaw.setValue(self._link.origin.yaw)
        self.mass_edit.setValue(self._link.mass)
        self.ixx.setValue(self._link.inertia.ixx)
        self.ixy.setValue(self._link.inertia.ixy)
        self.ixz.setValue(self._link.inertia.ixz)
        self.iyy.setValue(self._link.inertia.iyy)
        self.iyz.setValue(self._link.inertia.iyz)
        self.izz.setValue(self._link.inertia.izz)
        self.base_checkbox.setChecked(self._link.is_base)

    def _on_name_changed(self, text):
        if self._link:
            self._link.name = text
            self._notify_changed()

    def _on_origin_changed(self):
        if self._link:
            self._link.origin.x = self.origin_x.value()
            self._link.origin.y = self.origin_y.value()
            self._link.origin.z = self.origin_z.value()
            self._link.origin.roll = self.roll.value()
            self._link.origin.pitch = self.pitch.value()
            self._link.origin.yaw = self.yaw.value()
            self._notify_changed()

    def _on_mass_changed(self, value):
        if self._link:
            self._link.mass = value
            self._notify_changed()

    def _on_inertia_changed(self):
        if self._link:
            self._link.inertia.ixx = self.ixx.value()
            self._link.inertia.ixy = self.ixy.value()
            self._link.inertia.ixz = self.ixz.value()
            self._link.inertia.iyy = self.iyy.value()
            self._link.inertia.iyz = self.iyz.value()
            self._link.inertia.izz = self.izz.value()
            self._notify_changed()

    def _on_base_changed(self, state):
        if self._link:
            self._link.is_base = (state == Qt.Checked)
            self._notify_changed()

    def _on_color_clicked(self):
        color = QColorDialog.getColor()
        if color.isValid() and self._link:
            r, g, b, a = color.getRgbF()
            self._link.visual.color = [r, g, b]
            self._notify_changed()

    def set_on_changed_callback(self, callback):
        self._on_changed_callback = callback

    def _notify_changed(self):
        if self._on_changed_callback:
            self._on_changed_callback(self._link)