from dataclasses import dataclass


@dataclass
class Hub:
    hub_name: int
    x: int
    y: int
    type: str
    max_drones: int
    names_dron: list

    def __post_init__(self) -> None:
        pass
