from typing import Optional
from dataclasses import dataclass, field

from urdf_exporter.core.link_model import Origin, Link


@dataclass
class Limit:
    lower: float = 0.0
    upper: float = 0.0
    effort: float = 0.0
    velocity: float = 0.0


@dataclass
class Dynamics:
    damping: float = 0.0
    friction: float = 0.0


@dataclass
class Joint:
    name: str
    joint_type: str = "revolute"
    parent: Optional[Link] = None
    child: Optional[Link] = None
    origin: Origin = field(default_factory=Origin)
    axis: list = field(default_factory=lambda: [0.0, 0.0, 1.0])
    limit: Limit = field(default_factory=Limit)
    dynamics: Dynamics = field(default_factory=Dynamics)
    safety_controller = None
    mimic = None

    JOINT_TYPES = ["revolute", "continuous", "prismatic", "planar", "floating", "fixed"]

    def is_valid(self) -> bool:
        if self.joint_type not in self.JOINT_TYPES:
            return False
        if self.parent is None or self.child is None:
            return False
        return True