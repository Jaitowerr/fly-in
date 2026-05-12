from dataclasses import dataclass


@dataclass
class stage_dron:
    nb_dron: int

    def __post_init__(self) -> None:
        self.mi_funcion_ejecutable
