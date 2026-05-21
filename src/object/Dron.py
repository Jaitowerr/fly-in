
from dataclasses import dataclass
from .Hub import Hub
# from typing import Optional

@dataclass
class Dron:
    id_dron: int
    turnos_restantes: int = 0
    # hub: Optional[Hub] = None
    hub: Hub = None
    if hub:
        hub: Hub = Hub
        posicion_actual: str = hub.hub_name
    else:
        posicion_actual: str = None
    posición_destino: str = None

    def __post_init__(self) -> None:
        pass
    
    def print_dron(self):
        print('  - ', self.id_dron, self.posicion_actual, self.posición_destino, self.turnos_restantes)
