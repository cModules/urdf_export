from typing import List, Optional, Dict
from dataclasses import dataclass, field

from urdf_exporter.core.link_model import Link
from urdf_exporter.core.joint_model import Joint


@dataclass
class RobotModel:
    name: str = "robot"
    links: List[Link] = field(default_factory=list)
    joints: List[Joint] = field(default_factory=list)
    materials: Dict[str, dict] = field(default_factory=dict)
    package_name: str = "robot_description"

    def add_link(self, link: Link):
        self.links.append(link)

    def add_joint(self, joint: Joint):
        self.joints.append(joint)

    def get_link_by_name(self, name: str) -> Optional[Link]:
        for link in self.links:
            if link.name == name:
                return link
        return None

    def get_joint_by_name(self, name: str) -> Optional[Joint]:
        for joint in self.joints:
            if joint.name == name:
                return joint
        return None

    def get_base_link(self) -> Optional[Link]:
        for link in self.links:
            if link.is_base:
                return link
        if self.links:
            return self.links[0]
        return None

    def build_joint_hierarchy(self):
        for link in self.links:
            link.parent_joint = None
            link.child_joints = []

        for joint in self.joints:
            if joint.parent:
                joint.parent.child_joints.append(joint)
            if joint.child:
                joint.child.parent_joint = joint

    def validate(self) -> List[str]:
        errors = []
        link_names = [link.name for link in self.links]

        if not self.links:
            errors.append("No links defined")

        for joint in self.joints:
            if joint.parent and joint.parent.name not in link_names:
                errors.append(f"Joint '{joint.name}' parent '{joint.parent.name}' not found")
            if joint.child and joint.child.name not in link_names:
                errors.append(f"Joint '{joint.name}' child '{joint.child.name}' not found")
            if joint.parent == joint.child:
                errors.append(f"Joint '{joint.name}' parent and child are the same")

        return errors