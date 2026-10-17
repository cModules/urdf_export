import os
import numpy as np


class MeshExporter:
    def __init__(self):
        pass

    def export_stl(self, mesh, file_path: str, transform: np.ndarray = None):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if transform is not None and not np.allclose(transform, np.eye(4)):
            mesh = mesh.apply_transform(transform)

        mesh.export(file_path)

    def export_dae(self, mesh, file_path: str, transform: np.ndarray = None):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if transform is not None and not np.allclose(transform, np.eye(4)):
            mesh = mesh.apply_transform(transform)

        mesh.export(file_path)

    def export_all_meshes(self, robot_model, output_dir: str, mesh_format: str = "stl"):
        meshes_dir = os.path.join(output_dir, "meshes")
        os.makedirs(meshes_dir, exist_ok=True)

        for link in robot_model.links:
            if link.mesh is None:
                continue

            mesh_filename = f"{link.name}.{mesh_format}"
            mesh_path = os.path.join(meshes_dir, mesh_filename)

            if mesh_format == "stl":
                self.export_stl(link.mesh, mesh_path, link.transform)
            elif mesh_format == "dae":
                self.export_dae(link.mesh, mesh_path, link.transform)

            link.visual.mesh.filename = f"package://{robot_model.package_name}/meshes/{mesh_filename}"
            link.collision.mesh.filename = f"package://{robot_model.package_name}/meshes/{mesh_filename}"

        return meshes_dir