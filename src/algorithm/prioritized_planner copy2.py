from src.object.Connection import Connection
from src.object.Hub import Hub
from src.object.Dron import Dron
from typing import List, Tuple, Dict




def _print_rutas(rutas: List[List])-> None:
    print(f"\nTotal de rutas encontradas: {len(rutas)}")
    if not rutas:
        print("No se encontraron rutas.")
        return
    for i, ruta in enumerate(rutas, 1):
        nombres = [con.origin.hub_name for con in ruta]
        nombres.append(ruta[-1].destiny.hub_name)
        print(f"Ruta {i}: {' -> '.join(nombres)}")

def print_rutas_detalle(rutas: List[List[Connection]]) -> None:
    print(f"\nTotal de rutas encontradas: {len(rutas)}")
    for i, ruta in enumerate(rutas, 1):
        print(f"\n--- Ruta {i} ---")
        for conn in ruta:
            print(f"  {conn.origin.hub_name} --> {conn.destiny.hub_name}")



from collections import defaultdict

def find_all_routes_dfs_style(list_connect: List[Connection]) -> List[List[Connection]]:
    # Grafo: origen -> lista de conexiones salientes
    graph = defaultdict(list)
    start_hubs = set()

    for con in list_connect:
        graph[con.origin.hub_name].append(con)
        if con.origin.start:
            start_hubs.add(con.origin.hub_name)

    all_routes = []

    def dfs(hub_name: str, path: List[Connection], visited: set):
        for con in graph.get(hub_name, []):
            next_hub = con.destiny.hub_name
            if next_hub in visited:
                continue  # Evitar ciclos
            new_path = path + [con]
            if con.destiny.end:
                all_routes.append(new_path)
            else:
                dfs(next_hub, new_path, visited | {next_hub})

    for start in start_hubs:
        dfs(start, [], {start})

    return all_routes


            




# def path(list_connect: List[Connection], dron: Dron, K: int = 3) -> List[Tuple[int, List[Hub], int]]:
def path(list_connect: List[Connection], dron: Dron) -> List[List[Connection]]:

    # Buscar rutas completas con DFS
    rutas = find_all_routes_dfs_style(list_connect)

    _print_rutas(rutas)
    return rutas


