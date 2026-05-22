from src.object.Connection import Connection
from src.object.Hub import Hub
from src.object.Dron import Dron
from typing import List, Tuple, Dict
from collections import defaultdict

# def path(list_connect: List[Connection], dron: Dron, K: int = 3) -> List[Tuple[int, List[Hub], int]]:
def path(list_connect: List[Connection], dron: Dron) -> None:

    start = dron.posicion_actual
    star_hub = dron.hub
    end = ''
    end_hub = None

    for con in list_connect:
        if con.destiny.end == True:
            end = con.destiny.hub_name
            end_hub = con.destiny
            break

    if not start or not end:
        return []    
    if start == end:
        return[]
    

    adjacency: Dict[str, List[str]] = {}   # mapa: hub_name -> lista de vecinos (nombres)
    hubs: Dict[str, object] = {}           # mapa: hub_name -> Hub (objeto)


    for con in list_connect:
        origin = con.origin        # objeto Hub de origen (parseo ya lo aseguró)
        destiny = con.destiny      # objeto Hub de destino
        o_name = origin.hub_name
        d_name = destiny.hub_name

        hubs[o_name] = origin
        hubs[d_name] = destiny

        if o_name not in adjacency:
            adjacency[o_name] = []
        if d_name not in adjacency[o_name]:
            adjacency[o_name].append(d_name)

        # si la conexión no es dirigida, añadir la inversa también
        if not getattr(con, "directed", False):
            if d_name not in adjacency:
                adjacency[d_name] = []
            if o_name not in adjacency[d_name]:
                adjacency[d_name].append(o_name)