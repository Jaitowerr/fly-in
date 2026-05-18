
from dataclasses import dataclass


@dataclass
class Dron:
    id_dron: int

    def __post_init__(self) -> None:
        pass
