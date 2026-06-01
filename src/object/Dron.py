
from dataclasses import dataclass
from .Hub import Hub
from typing import Optional, Any, List


@dataclass
class Dron:
    drone_id: int
    current_position: str = ''
    destination_position: str = ''
    remaining_turns: int = 0
    hub: Optional[Hub] = None
    route_positions: Optional[List[Any]] = None
