from dataclasses import dataclass
from .Hub import Hub


@dataclass
class Connection:
    origin: Hub = None
    destiny: Hub = None
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        pass
