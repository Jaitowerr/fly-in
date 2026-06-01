
from dataclasses import dataclass
from .Hub import Hub
from typing import Optional, Any


@dataclass
class Dron:

    drone_id: int
    current_position: str
    destination_position: str
    remaining_turns: int = 0
    hub: Optional[Hub] = None
    route_positions: Any = None
