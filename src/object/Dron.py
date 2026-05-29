
from dataclasses import dataclass
from .Hub import Hub
from typing import Optional, Any


@dataclass
class Dron:

    drone_id: int
    remaining_turns: int = 0
    hub: Optional[Hub] = None
    current_position: str = None
    destination_position: str = None
    route_positions: Any = None
