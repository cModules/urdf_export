import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QAction, QToolBar, QStatusBar,
                             QMenuBar, QMessageBox, QFileDialog, QTabWidget,
                             QPushButton, QTreeWidget, QTreeWidgetItem,
                             QLabel)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from urdf_exporter.core.step_io import StepImporter, StepAssembly
from urdf_exporter.core.link_model import Link
from urdf_exporter.core.joint_model import Joint
from urdf_exporter.core.robot_model import RobotModel
from urdf_exporter.core.urdf_writer import UrdfWriter
from urdf_exporter.core.mesh_exporter import MeshExporter
from urdf_exporter.gui.occ_viewer import OccViewerWidget
from urdf_exporter.gui.part_tree_widget import PartTreeWidget
from urdf_exporter.gui.link_editor import LinkEditorWidget
from urdf_exporter.gui.joint_editor import JointEditorWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("URDF Exporter")
        self.setMinimumSize(1200, 800)

        self.step_importer = StepImporter()
        self.urdf_writer = UrdfWriter()
        self.mesh_exporter = MeshExporter()

        self.assembly = None
        self.robot_model = RobotModel()

        self._init_ui()
        self._init_actions()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_splitter = QSplitter(Qt.Vertical)
        right_splitter = QSplitter(Qt.Vertical)
        main_splitter = QSplitter(Qt.Horizontal)

        self.part_tree = PartTreeWidget()
        self.part_tree.itemSelectionChanged.connect(self._on_part_selected)

        self.robot_tree = QTreeWidget()
        self.robot_tree.setHeaderLabels(["Element", "Type"])

        left_splitter.addWidget(self.part_tree)
        left_splitter.addWidget(self.robot_tree)

        self.viewer = OccViewerWidget()

        self.tab_widget = QTabWidget()

        self.link_editor = LinkEditorWidget()
        self.link_editor.set_on_changed_callback(self._on_link_changed)

        self.joint_editor = JointEditorWidget()
        self.joint_editor.set_on_changed_callback(self._on_joint_changed)

        self.tab_widget.addTab(self.link_editor, "Link Editor")
        self.tab_widget.addTab(self.joint_editor, "Joint Editor")

        right_splitter.addWidget(self.tab_widget)

        toolbar_widget = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.add_link_btn = QPushButton("Add Link")
        self.add_link_btn.clicked.connect(self._on_add_link)
        self.add_link_btn.setEnabled(False)

        self.add_joint_btn = QPushButton("Add Joint")
        self.add_joint_btn.clicked.connect(self._on_add_joint)
        self.add_joint_btn.setEnabled(False)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setEnabled(False)

        toolbar_layout.addWidget(self.add_link_btn)
        toolbar_layout.addWidget(self.add_joint_btn)
        toolbar_layout.addWidget(self.delete_btn)
        toolbar_layout.addStretch()

        right_splitter.addWidget(toolbar_widget)

        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.viewer)
        main_splitter.addWidget(right_splitter)

        main_splitter.setSizes([250, 600, 350])

        main_layout.addWidget(main_splitter)

        self._init_toolbar()
        self._init_statusbar()

    def _init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        self.open_action = QAction("Open STEP", self)
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.triggered.connect(self._on_open_step)
        toolbar.addAction(self.open_action)

        toolbar.addSeparator()

        self.export_urdf_action = QAction("Export URDF", self)
        self.export_urdf_action.setShortcut("Ctrl+E")
        self.export_urdf_action.triggered.connect(self._on_export_urdf)
        self.export_urdf_action.setEnabled(False)
        toolbar.addAction(self.export_urdf_action)

        toolbar.addSeparator()

        self.fit_action = QAction("Fit All", self)
        self.fit_action.triggered.connect(self.viewer.fit_all)
        toolbar.addAction(self.fit_action)

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.triggered.connect(self.viewer.zoom_in)
        toolbar.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.viewer.zoom_out)
        toolbar.addAction(self.zoom_out_action)

    def _init_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)

    def _init_actions(self):
        self.robot_tree.itemSelectionChanged.connect(self._on_robot_tree_selected)

    def _on_open_step(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open STEP File", "", "STEP Files (*.step *.stp);;All Files (*)"
        )

        if file_path:
            try:
                self.status_label.setText(f"Loading STEP file: {file_path}")
                self.assembly = self.step_importer.import_file(file_path)

                self.viewer.clear()
                self.viewer.add_meshes_from_assembly(self.assembly)

                self.part_tree.load_assembly(self.assembly)

                self.robot_model = RobotModel(name=os.path.splitext(os.path.basename(file_path))[0])
                self._update_robot_tree()

                self.add_link_btn.setEnabled(True)
                self.export_urdf_action.setEnabled(True)

                self.status_label.setText(f"Loaded {len(self.part_tree.get_all_parts())} parts")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load STEP file:\n{str(e)}")
                self.status_label.setText("Error loading file")

    def _on_part_selected(self):
        selected = self.part_tree.get_selected_items()
        self.add_link_btn.setEnabled(len(selected) > 0)

    def _on_add_link(self):
        selected = self.part_tree.get_selected_items()
        parts = [item[1] for item in selected if item[0] == "part"]

        for part in parts:
            link = Link(name=part.name)
            link.mesh = part.mesh
            link.transform = part.transform
            link.mass = part.mass
            link.center_of_mass = part.center_of_mass.tolist() if hasattr(part.center_of_mass, 'tolist') else [0, 0, 0]
            link.inertia.ixx = part.inertia[0]
            link.inertia.ixy = part.inertia[1]
            link.inertia.ixz = part.inertia[2]
            link.inertia.iyy = part.inertia[3]
            link.inertia.iyz = part.inertia[4]
            link.inertia.izz = part.inertia[5]

            if not self.robot_model.links:
                link.is_base = True

            self.robot_model.add_link(link)
            self.part_tree.update_part_status(part.name, "Assigned")

        self._update_robot_tree()
        self.joint_editor.set_robot_model(self.robot_model)
        self.add_joint_btn.setEnabled(len(self.robot_model.links) >= 2)

    def _on_add_joint(self):
        if len(self.robot_model.links) < 2:
            QMessageBox.warning(self, "Warning", "Need at least 2 links to create a joint")
            return

        joint_count = len(self.robot_model.joints)
        joint = Joint(name=f"joint_{joint_count}")

        if self.robot_model.links:
            joint.parent = self.robot_model.links[0]
            if len(self.robot_model.links) > 1:
                joint.child = self.robot_model.links[-1]

        self.robot_model.add_joint(joint)
        self._update_robot_tree()

    def _on_delete(self):
        selected_items = self.robot_tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_type = item.data(0, Qt.UserRole + 1)
        data = item.data(0, Qt.UserRole)

        if item_type == "link":
            self.robot_model.links.remove(data)
            self.part_tree.update_part_status(data.name, "Unassigned")
        elif item_type == "joint":
            self.robot_model.joints.remove(data)

        self._update_robot_tree()
        self.joint_editor.set_robot_model(self.robot_model)

        if len(self.robot_model.links) < 2:
            self.add_joint_btn.setEnabled(False)

    def _on_robot_tree_selected(self):
        selected_items = self.robot_tree.selectedItems()
        if not selected_items:
            self.delete_btn.setEnabled(False)
            return

        item = selected_items[0]
        item_type = item.data(0, Qt.UserRole + 1)
        data = item.data(0, Qt.UserRole)

        self.delete_btn.setEnabled(True)

        if item_type == "link":
            self.tab_widget.setCurrentIndex(0)
            self.link_editor.set_link(data)
        elif item_type == "joint":
            self.tab_widget.setCurrentIndex(1)
            self.joint_editor.set_joint(data)

    def _on_link_changed(self, link):
        self._update_robot_tree()

    def _on_joint_changed(self, joint):
        self._update_robot_tree()

    def _update_robot_tree(self):
        self.robot_tree.clear()

        base_item = QTreeWidgetItem(["Links", ""])
        self.robot_tree.addTopLevelItem(base_item)

        for link in self.robot_model.links:
            link_item = QTreeWidgetItem([link.name, "link"])
            link_item.setData(0, Qt.UserRole, link)
            link_item.setData(0, Qt.UserRole + 1, "link")
            if link.is_base:
                link_item.setText(1, "base_link")
            base_item.addChild(link_item)

        joint_item = QTreeWidgetItem(["Joints", ""])
        self.robot_tree.addTopLevelItem(joint_item)

        for joint in self.robot_model.joints:
            parent_name = joint.parent.name if joint.parent else "None"
            child_name = joint.child.name if joint.child else "None"
            joint_label = f"{joint.name} ({parent_name} -> {child_name})"
            j_item = QTreeWidgetItem([joint_label, joint.joint_type])
            j_item.setData(0, Qt.UserRole, joint)
            j_item.setData(0, Qt.UserRole + 1, "joint")
            joint_item.addChild(j_item)

        self.robot_tree.expandAll()

    def _on_export_urdf(self):
        if not self.robot_model.links:
            QMessageBox.warning(self, "Warning", "No links defined")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir:
            return

        try:
            self.status_label.setText("Exporting URDF...")

            urdf_dir = os.path.join(output_dir, "urdf")
            os.makedirs(urdf_dir, exist_ok=True)

            self.mesh_exporter.export_all_meshes(self.robot_model, output_dir, "stl")

            urdf_path = os.path.join(urdf_dir, f"{self.robot_model.name}.urdf")
            self.urdf_writer.write_urdf(self.robot_model, urdf_path)

            package_xml_path = os.path.join(output_dir, "package.xml")
            self.urdf_writer.write_package_xml(self.robot_model, package_xml_path)

            cmake_path = os.path.join(output_dir, "CMakeLists.txt")
            self.urdf_writer.write_cmake_lists(self.robot_model, cmake_path)

            self.status_label.setText(f"URDF exported to {urdf_path}")
            QMessageBox.information(self, "Success", f"URDF exported successfully!\n\nOutput:\n- {urdf_path}\n- {os.path.join(output_dir, 'meshes')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export URDF:\n{str(e)}")
            self.status_label.setText("Export failed")