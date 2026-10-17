from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Origin:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0


@dataclass
class Inertia:
    ixx: float = 0.0
    ixy: float = 0.0
    ixz: float = 0.0
    iyy: float = 0.0
    iyz: float = 0.0
    izz: float = 0.0


@dataclass
class MeshGeometry:
    filename: str = ""
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])


@dataclass
class Visual:
    origin: Origin = field(default_factory=Origin)
    geometry_type: str = "mesh"
    mesh: MeshGeometry = field(default_factory=MeshGeometry)
    color: List[float] = field(default_factory=lambda: [0.8, 0.8, 0.8])


@dataclass
class Collision:
    origin: Origin = field(default_factory=Origin)
    geometry_type: str = "mesh"
    mesh: MeshGeometry = field(default_factory=MeshGeometry)


@dataclass
class Link:
    name: str
    origin: Origin = field(default_factory=Origin)
    visual: Visual = field(default_factory=Visual)
    collision: Collision = field(default_factory=Collision)
    inertia: Inertia = field(default_factory=Inertia)
    mass: float = 0.0
    mesh = None
    transform: np.ndarray = field(default_factory=lambda: np.eye(4))
    center_of_mass: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    is_base: bool = False
    parent_joint: Optional['Joint'] = None
    child_joints: List['Joint'] = field(default_factory=list)