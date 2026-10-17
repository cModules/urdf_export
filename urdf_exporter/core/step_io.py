import os
import trimesh
import numpy as np
from typing import List, Optional


class StepPart:
    def __init__(self, name: str, mesh=None, transform=None):
        self.name = name
        self.mesh = mesh
        self.transform = transform if transform is not None else np.eye(4)
        self.color = None
        self.mass = 0.0
        self.inertia = [0.0] * 6
        self.center_of_mass = np.array([0, 0, 0])


class StepAssembly:
    def __init__(self, name: str):
        self.name = name
        self.parts: List[StepPart] = []
        self.subassemblies: List[StepAssembly] = []

    def add_part(self, part: StepPart):
        self.parts.append(part)

    def add_subassembly(self, subassembly: 'StepAssembly'):
        self.subassemblies.append(subassembly)


class StepImporter:
    def __init__(self):
        pass

    def import_file(self, file_path: str) -> StepAssembly:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            mesh = trimesh.load(file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to read STEP file: {str(e)}")

        assembly = StepAssembly(os.path.splitext(os.path.basename(file_path))[0])

        if isinstance(mesh, trimesh.Trimesh):
            part = StepPart(assembly.name, mesh, np.eye(4))
            self._compute_mass_properties(part)
            assembly.add_part(part)
        elif isinstance(mesh, trimesh.Scene):
            self._extract_from_scene(mesh, assembly)
        elif hasattr(mesh, 'geometry'):
            for name, geom in mesh.geometry.items():
                if isinstance(geom, trimesh.Trimesh):
                    part = StepPart(name, geom, np.eye(4))
                    self._compute_mass_properties(part)
                    assembly.add_part(part)

        return assembly

    def _extract_from_scene(self, scene: trimesh.Scene, parent_assembly: StepAssembly):
        for node_name in scene.graph.nodes_geometry:
            try:
                result = scene.graph.get(node_name)
                if isinstance(result, tuple):
                    transform = result[0]
                    geom_name = result[1]
                else:
                    transform = result
                    geom_name = node_name
            except Exception:
                transform = np.eye(4)
                geom_name = node_name
            
            geom = scene.geometry.get(geom_name)
            if isinstance(geom, trimesh.Trimesh):
                part = StepPart(geom_name, geom, transform)
                self._compute_mass_properties(part)
                parent_assembly.add_part(part)

    def _compute_mass_properties(self, part: StepPart):
        if part.mesh is not None and part.mesh.volume > 0:
            part.mass = part.mesh.volume * 7850
            part.center_of_mass = part.mesh.center_mass

            inertia = part.mesh.moment_inertia
            part.inertia = [
                inertia[0, 0], inertia[0, 1], inertia[0, 2],
                inertia[1, 1], inertia[1, 2], inertia[2, 2]
            ]