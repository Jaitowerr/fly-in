from dataclasses import dataclass
from .Hub import Hub


@dataclass
class Connection:
    origin: Hub | None = None
    destiny: Hub | None = None
    max_link_capacity: int = 1
    drones_in_connection: int = 0
