from dataclasses import dataclass


@dataclass
class Connection:
    origin: str
    destiny: str
    max_link_capacity: int

    def __post_init__(self) -> None:
        pass
