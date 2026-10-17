from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QDoubleSpinBox, QComboBox, QGroupBox, QLabel)
from PyQt5.QtCore import Qt

from urdf_exporter.core.joint_model import Joint, Limit, Dynamics
from urdf_exporter.core.robot_model import RobotModel


class JointEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._joint = None
        self._robot_model = None
        self._on_changed_callback = None

        self.layout = QVBoxLayout(self)

        self.name_group = QGroupBox("Joint Name")
        self.name_layout = QFormLayout(self.name_group)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_name_changed)
        self.name_layout.addRow("Name:", self.name_edit)
        self.layout.addWidget(self.name_group)

        self.type_group = QGroupBox("Joint Type")
        self.type_layout = QFormLayout(self.type_group)
        self.type_combo = QComboBox()
        self.type_combo.addItems(Joint.JOINT_TYPES)
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        self.type_layout.addRow("Type:", self.type_combo)
        self.layout.addWidget(self.type_group)

        self.parent_group = QGroupBox("Parent Link")
        self.parent_layout = QFormLayout(self.parent_group)
        self.parent_combo = QComboBox()
        self.parent_combo.currentTextChanged.connect(self._on_parent_changed)
        self.parent_layout.addRow("Parent:", self.parent_combo)
        self.layout.addWidget(self.parent_group)

        self.child_group = QGroupBox("Child Link")
        self.child_layout = QFormLayout(self.child_group)
        self.child_combo = QComboBox()
        self.child_combo.currentTextChanged.connect(self._on_child_changed)
        self.child_layout.addRow("Child:", self.child_combo)
        self.layout.addWidget(self.child_group)

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

        self.axis_group = QGroupBox("Axis")
        self.axis_layout = QFormLayout(self.axis_group)
        self.axis_x = QDoubleSpinBox()
        self.axis_x.setRange(-1, 1)
        self.axis_x.setDecimals(4)
        self.axis_y = QDoubleSpinBox()
        self.axis_y.setRange(-1, 1)
        self.axis_y.setDecimals(4)
        self.axis_z = QDoubleSpinBox()
        self.axis_z.setRange(-1, 1)
        self.axis_z.setDecimals(4)
        self.axis_z.setValue(1.0)

        self.axis_layout.addRow("X:", self.axis_x)
        self.axis_layout.addRow("Y:", self.axis_y)
        self.axis_layout.addRow("Z:", self.axis_z)
        self.layout.addWidget(self.axis_group)

        self.limit_group = QGroupBox("Limits")
        self.limit_layout = QFormLayout(self.limit_group)
        self.limit_lower = QDoubleSpinBox()
        self.limit_lower.setRange(-100, 100)
        self.limit_lower.setDecimals(4)
        self.limit_upper = QDoubleSpinBox()
        self.limit_upper.setRange(-100, 100)
        self.limit_upper.setDecimals(4)
        self.limit_effort = QDoubleSpinBox()
        self.limit_effort.setRange(0, 1000)
        self.limit_effort.setDecimals(2)
        self.limit_velocity = QDoubleSpinBox()
        self.limit_velocity.setRange(0, 100)
        self.limit_velocity.setDecimals(2)

        self.limit_layout.addRow("Lower:", self.limit_lower)
        self.limit_layout.addRow("Upper:", self.limit_upper)
        self.limit_layout.addRow("Effort:", self.limit_effort)
        self.limit_layout.addRow("Velocity:", self.limit_velocity)
        self.layout.addWidget(self.limit_group)

        self.dynamics_group = QGroupBox("Dynamics")
        self.dynamics_layout = QFormLayout(self.dynamics_group)
        self.damping = QDoubleSpinBox()
        self.damping.setRange(0, 100)
        self.damping.setDecimals(4)
        self.friction = QDoubleSpinBox()
        self.friction.setRange(0, 100)
        self.friction.setDecimals(4)

        self.dynamics_layout.addRow("Damping:", self.damping)
        self.dynamics_layout.addRow("Friction:", self.friction)
        self.layout.addWidget(self.dynamics_group)

        self.layout.addStretch()

        self.origin_x.valueChanged.connect(self._on_origin_changed)
        self.origin_y.valueChanged.connect(self._on_origin_changed)
        self.origin_z.valueChanged.connect(self._on_origin_changed)
        self.roll.valueChanged.connect(self._on_origin_changed)
        self.pitch.valueChanged.connect(self._on_origin_changed)
        self.yaw.valueChanged.connect(self._on_origin_changed)
        self.axis_x.valueChanged.connect(self._on_axis_changed)
        self.axis_y.valueChanged.connect(self._on_axis_changed)
        self.axis_z.valueChanged.connect(self._on_axis_changed)
        self.limit_lower.valueChanged.connect(self._on_limit_changed)
        self.limit_upper.valueChanged.connect(self._on_limit_changed)
        self.limit_effort.valueChanged.connect(self._on_limit_changed)
        self.limit_velocity.valueChanged.connect(self._on_limit_changed)
        self.damping.valueChanged.connect(self._on_dynamics_changed)
        self.friction.valueChanged.connect(self._on_dynamics_changed)

    def set_robot_model(self, robot_model: RobotModel):
        self._robot_model = robot_model
        self._update_link_combos()

    def _update_link_combos(self):
        self.parent_combo.clear()
        self.child_combo.clear()
        if self._robot_model:
            for link in self._robot_model.links:
                self.parent_combo.addItem(link.name)
                self.child_combo.addItem(link.name)

    def set_joint(self, joint: Joint):
        self._joint = joint
        self._update_ui()

    def _update_ui(self):
        if self._joint is None:
            return

        self.name_edit.setText(self._joint.name)
        idx = self.type_combo.findText(self._joint.joint_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)

        if self._joint.parent:
            idx = self.parent_combo.findText(self._joint.parent.name)
            if idx >= 0:
                self.parent_combo.setCurrentIndex(idx)

        if self._joint.child:
            idx = self.child_combo.findText(self._joint.child.name)
            if idx >= 0:
                self.child_combo.setCurrentIndex(idx)

        self.origin_x.setValue(self._joint.origin.x)
        self.origin_y.setValue(self._joint.origin.y)
        self.origin_z.setValue(self._joint.origin.z)
        self.roll.setValue(self._joint.origin.roll)
        self.pitch.setValue(self._joint.origin.pitch)
        self.yaw.setValue(self._joint.origin.yaw)
        self.axis_x.setValue(self._joint.axis[0])
        self.axis_y.setValue(self._joint.axis[1])
        self.axis_z.setValue(self._joint.axis[2])
        self.limit_lower.setValue(self._joint.limit.lower)
        self.limit_upper.setValue(self._joint.limit.upper)
        self.limit_effort.setValue(self._joint.limit.effort)
        self.limit_velocity.setValue(self._joint.limit.velocity)
        self.damping.setValue(self._joint.dynamics.damping)
        self.friction.setValue(self._joint.dynamics.friction)

    def _on_name_changed(self, text):
        if self._joint:
            self._joint.name = text
            self._notify_changed()

    def _on_type_changed(self, text):
        if self._joint:
            self._joint.joint_type = text
            self._notify_changed()

    def _on_parent_changed(self, text):
        if self._joint and self._robot_model:
            self._joint.parent = self._robot_model.get_link_by_name(text)
            self._notify_changed()

    def _on_child_changed(self, text):
        if self._joint and self._robot_model:
            self._joint.child = self._robot_model.get_link_by_name(text)
            self._notify_changed()

    def _on_origin_changed(self):
        if self._joint:
            self._joint.origin.x = self.origin_x.value()
            self._joint.origin.y = self.origin_y.value()
            self._joint.origin.z = self.origin_z.value()
            self._joint.origin.roll = self.roll.value()
            self._joint.origin.pitch = self.pitch.value()
            self._joint.origin.yaw = self.yaw.value()
            self._notify_changed()

    def _on_axis_changed(self):
        if self._joint:
            self._joint.axis = [self.axis_x.value(), self.axis_y.value(), self.axis_z.value()]
            self._notify_changed()

    def _on_limit_changed(self):
        if self._joint:
            self._joint.limit.lower = self.limit_lower.value()
            self._joint.limit.upper = self.limit_upper.value()
            self._joint.limit.effort = self.limit_effort.value()
            self._joint.limit.velocity = self.limit_velocity.value()
            self._notify_changed()

    def _on_dynamics_changed(self):
        if self._joint:
            self._joint.dynamics.damping = self.damping.value()
            self._joint.dynamics.friction = self.friction.value()
            self._notify_changed()

    def set_on_changed_callback(self, callback):
        self._on_changed_callback = callback

    def _notify_changed(self):
        if self._on_changed_callback:
            self._on_changed_callback(self._joint)