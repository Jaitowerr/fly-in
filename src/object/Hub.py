from dataclasses import dataclass, field
from typing import List


@dataclass
class Hub:
    hub_name: str
    x: int
    y: int
    color: str = None
    zone: str = 'normal'
    max_drones: int = 1
    start: bool = False
    end: bool = False
    # names_dron: list
    # names_dron: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        pass
