
from dataclasses import dataclass
from .Hub import Hub
from typing import Optional

@dataclass
class Dron:
    id_dron: int
    turnos_restantes: int = 0
    # hub: Optional[Hub] = None
    hub: Optional[Hub] = None
    posicion_actual: str = None
    posicion_destino: str = None

    def __post_init__(self) -> None:
        pass
    
    # def print_dron(self):
    #     print('  - ', self.id_dron, self.posicion_actual, self.posicion_destino, self.turnos_restantes)
