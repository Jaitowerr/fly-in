from dataclasses import dataclass


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
    drones_in_hub = 0
