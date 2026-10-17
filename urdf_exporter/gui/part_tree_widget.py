from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView
from PyQt5.QtCore import Qt

from urdf_exporter.core.step_io import StepAssembly, StepPart


class PartTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Name", "Type", "Status"])
        self.header().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionMode(QTreeWidget.ExtendedSelection)

        self._assembly = None

    def load_assembly(self, assembly: StepAssembly):
        self.clear()
        self._assembly = assembly
        self._add_assembly_to_tree(assembly)

    def _add_assembly_to_tree(self, assembly: StepAssembly, parent_item: QTreeWidgetItem = None):
        item = QTreeWidgetItem([assembly.name, "Assembly", "Loaded"])
        item.setData(0, Qt.UserRole, assembly)
        item.setData(0, Qt.UserRole + 1, "assembly")

        if parent_item:
            parent_item.addChild(item)
        else:
            self.addTopLevelItem(item)

        for part in assembly.parts:
            part_item = QTreeWidgetItem([part.name, "Part", "Unassigned"])
            part_item.setData(0, Qt.UserRole, part)
            part_item.setData(0, Qt.UserRole + 1, "part")
            item.addChild(part_item)

        for sub_asm in assembly.subassemblies:
            self._add_assembly_to_tree(sub_asm, item)

    def get_selected_items(self):
        items = []
        for selected in self.selectedItems():
            item_type = selected.data(0, Qt.UserRole + 1)
            data = selected.data(0, Qt.UserRole)
            items.append((item_type, data))
        return items

    def update_part_status(self, part_name: str, status: str):
        items = self.findItems(part_name, Qt.MatchExactly, 0)
        for item in items:
            if item.data(0, Qt.UserRole + 1) == "part":
                item.setText(2, status)

    def get_all_parts(self):
        parts = []

        def collect_parts(item):
            item_type = item.data(0, Qt.UserRole + 1)
            data = item.data(0, Qt.UserRole)
            if item_type == "part":
                parts.append(data)
            for i in range(item.childCount()):
                collect_parts(item.child(i))

        for i in range(self.topLevelItemCount()):
            collect_parts(self.topLevelItem(i))

        return parts