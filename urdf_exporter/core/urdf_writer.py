import os
from lxml import etree

from urdf_exporter.core.robot_model import RobotModel
from urdf_exporter.core.link_model import Link, Origin, Inertia, Visual, Collision
from urdf_exporter.core.joint_model import Joint, Limit, Dynamics


class UrdfWriter:
    def __init__(self):
        self.ros_version = "ros2"

    def set_ros_version(self, version: str):
        if version in ["ros1", "ros2"]:
            self.ros_version = version

    def write_urdf(self, robot_model: RobotModel, output_path: str):
        root = etree.Element("robot", name=robot_model.name)

        for link in robot_model.links:
            link_elem = self._create_link_element(link)
            root.append(link_elem)

        for joint in robot_model.joints:
            joint_elem = self._create_joint_element(joint)
            root.append(joint_elem)

        if robot_model.materials:
            for mat_name, mat_data in robot_model.materials.items():
                mat_elem = etree.SubElement(root, "material", name=mat_name)
                if "color" in mat_data:
                    rgba = mat_data["color"]
                    etree.SubElement(mat_elem, "color", rgba=f"{rgba[0]} {rgba[1]} {rgba[2]} {rgba[3]}")

        tree = etree.ElementTree(root)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def _create_link_element(self, link: Link) -> etree.Element:
        link_elem = etree.Element("link", name=link.name)

        if link.origin.x != 0 or link.origin.y != 0 or link.origin.z != 0:
            origin_elem = self._create_origin_element(link.origin)
            link_elem.append(origin_elem)

        if link.visual.mesh.filename:
            visual_elem = self._create_visual_element(link.visual)
            link_elem.append(visual_elem)

        if link.collision.mesh.filename:
            collision_elem = self._create_collision_element(link.collision)
            link_elem.append(collision_elem)

        if link.mass > 0:
            inertial_elem = etree.SubElement(link_elem, "inertial")
            com_x = getattr(link, 'center_of_mass', [0, 0, 0])[0]
            com_y = getattr(link, 'center_of_mass', [0, 0, 0])[1]
            com_z = getattr(link, 'center_of_mass', [0, 0, 0])[2]
            origin_elem = etree.SubElement(inertial_elem, "origin",
                                           xyz=f"{com_x} {com_y} {com_z}")
            mass_elem = etree.SubElement(inertial_elem, "mass", value=str(link.mass))
            inertia_elem = etree.SubElement(inertial_elem, "inertia",
                                           ixx=str(link.inertia.ixx),
                                           ixy=str(link.inertia.ixy),
                                           ixz=str(link.inertia.ixz),
                                           iyy=str(link.inertia.iyy),
                                           iyz=str(link.inertia.iyz),
                                           izz=str(link.inertia.izz))

        return link_elem

    def _create_joint_element(self, joint: Joint) -> etree.Element:
        joint_elem = etree.Element("joint", name=joint.name, type=joint.joint_type)

        origin_elem = self._create_origin_element(joint.origin)
        joint_elem.append(origin_elem)

        parent_elem = etree.SubElement(joint_elem, "parent", link=joint.parent.name if joint.parent else "")
        child_elem = etree.SubElement(joint_elem, "child", link=joint.child.name if joint.child else "")

        if joint.joint_type in ["revolute", "continuous", "prismatic"]:
            axis_elem = etree.SubElement(joint_elem, "axis",
                                         xyz=f"{joint.axis[0]} {joint.axis[1]} {joint.axis[2]}")

        if joint.joint_type in ["revolute", "prismatic"]:
            limit_elem = etree.SubElement(joint_elem, "limit",
                                          lower=str(joint.limit.lower),
                                          upper=str(joint.limit.upper),
                                          effort=str(joint.limit.effort),
                                          velocity=str(joint.limit.velocity))

        if joint.dynamics.damping > 0 or joint.dynamics.friction > 0:
            dynamics_elem = etree.SubElement(joint_elem, "dynamics",
                                             damping=str(joint.dynamics.damping),
                                             friction=str(joint.dynamics.friction))

        return joint_elem

    def _create_origin_element(self, origin: Origin) -> etree.Element:
        xyz = f"{origin.x} {origin.y} {origin.z}"
        rpy = f"{origin.roll} {origin.pitch} {origin.yaw}"
        return etree.Element("origin", xyz=xyz, rpy=rpy)

    def _create_visual_element(self, visual: Visual) -> etree.Element:
        visual_elem = etree.Element("visual")

        origin_elem = self._create_origin_element(visual.origin)
        visual_elem.append(origin_elem)

        geometry_elem = etree.SubElement(visual_elem, "geometry")

        if visual.geometry_type == "mesh":
            mesh_elem = etree.SubElement(geometry_elem, "mesh", filename=visual.mesh.filename)
            if visual.mesh.scale != [1.0, 1.0, 1.0]:
                mesh_elem.set("scale", f"{visual.mesh.scale[0]} {visual.mesh.scale[1]} {visual.mesh.scale[2]}")

        material_elem = etree.SubElement(visual_elem, "material")
        rgba = f"{visual.color[0]} {visual.color[1]} {visual.color[2]} 1.0"
        color_elem = etree.SubElement(material_elem, "color", rgba=rgba)

        return visual_elem

    def _create_collision_element(self, collision: Collision) -> etree.Element:
        collision_elem = etree.Element("collision")

        origin_elem = self._create_origin_element(collision.origin)
        collision_elem.append(origin_elem)

        geometry_elem = etree.SubElement(collision_elem, "geometry")

        if collision.geometry_type == "mesh":
            mesh_elem = etree.SubElement(geometry_elem, "mesh", filename=collision.mesh.filename)
            if collision.mesh.scale != [1.0, 1.0, 1.0]:
                mesh_elem.set("scale", f"{collision.mesh.scale[0]} {collision.mesh.scale[1]} {collision.mesh.scale[2]}")

        return collision_elem

    def write_package_xml(self, robot_model: RobotModel, output_path: str):
        root = etree.Element("package", format="3", version="0.0.0", name=robot_model.package_name)

        etree.SubElement(root, "description").text = f"{robot_model.name} description package"
        etree.SubElement(root, "maintainer", email="dev@example.com").text = "Developer"
        etree.SubElement(root, "license").text = "MIT"

        if self.ros_version == "ros2":
            etree.SubElement(root, "buildtool_depend").text = "ament_cmake"
            etree.SubElement(root, "depend").text = "urdf"
            etree.SubElement(root, "export")
        else:
            etree.SubElement(root, "buildtool_depend").text = "catkin"
            etree.SubElement(root, "build_depend").text = "urdf"
            etree.SubElement(root, "build_export_depend").text = "urdf"
            etree.SubElement(root, "exec_depend").text = "urdf"

        tree = etree.ElementTree(root)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        tree.write(output_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def write_cmake_lists(self, robot_model: RobotModel, output_path: str):
        if self.ros_version == "ros2":
            content = f"""cmake_minimum_required(VERSION 3.8)
project({robot_model.package_name})

if(CMAKE_COMPILER_IS_GNUCXX OR (CMAKE_CXX_COMPILER_ID MATCHES "Clang"))
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)

install(DIRECTORY urdf meshes
  DESTINATION share/${{PROJECT_NAME}})

ament_package()
"""
        else:
            content = f"""cmake_minimum_required(VERSION 3.0.2)
project({robot_model.package_name})

find_package(catkin REQUIRED COMPONENTS urdf)

catkin_package()

install(DIRECTORY urdf meshes
  DESTINATION ${{CATKIN_PACKAGE_SHARE_DESTINATION}})
"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(content)