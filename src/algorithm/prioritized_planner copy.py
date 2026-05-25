from src.object.Connection import Connection
from src.object.Hub import Hub
from src.object.Dron import Dron
from typing import List, Tuple, Dict


def print_rutas(rutas: List[List])-> None:
    if not rutas:
        print("No se encontraron rutas.")
        return
    for i, ruta in enumerate(rutas, 1):
        nombres = [con.origin.hub_name for con in ruta]
        nombres.append(ruta[-1].destiny.hub_name)
        print(f"Ruta {i}: {' -> '.join(nombres)}")


def create_rut(list_ordenadas: List[List[Connection]])-> List[List[Connection]]:
    """
    Genera todas las combinaciones posibles de conexiones por nivel,
    respetando el encadenamiento (origin.hub_name == prev.destiny.hub_name),
    y filtrando solo las rutas que terminan en destino con end=True.
    """
    def recursiva(indice=0, actual=None):
        if actual is None:
            actual = []
        # Si hemos recorrido todos los niveles, aceptamos solo si la última conexión es end
        if indice == len(list_ordenadas):
            if actual and actual[-1].destiny.end:
                return [actual]
            return []

        resultado = []
        for e in list_ordenadas[indice]:
            # en el primer nivel exigimos origin.start
            if indice == 0:
                if not e.origin.start:
                    continue
            else:
                # comprobar encadenamiento con la última conexión elegida
                prev = actual[-1]
                if e.origin.hub_name != prev.destiny.hub_name:
                    continue

            nueva = actual + [e]
            # si alcanza end guardamos la ruta (no profundizamos más desde aquí)
            if nueva[-1].destiny.end:
                resultado.append(nueva)
            else:
                resultado.extend(recursiva(indice + 1, nueva))

        return resultado
    return recursiva()


def lista_de_lista(list_connect:List[Connection]) -> List[List[Connection]]:
    """
    Agrupa las conexiones en niveles según origen -> destino.
    Devuelve una lista de listas donde cada sublista representa un nivel.
    """

    pool = list_connect[:]  # trabajamos sobre una copia para no mutar la original

    list_ordenadas = []
    list_insert = []
    name_hilo = set()
    name_hilo_two = set()

    # Primer nivel: conexiones que empiezan en start=True
    for con in list_connect:
        if con.origin.start == True:
            list_insert.append(con)
            pool.remove(con)
            name_hilo.add(con.destiny.hub_name)
    if list_insert:
        list_ordenadas.append(list_insert[:])
        list_insert.clear()
    
    # Niveles siguientes
    while pool:
        progressed = False
        for con in pool[:]:
            if con.origin.hub_name in name_hilo:
                list_insert.append(con)
                name_hilo_two.add(con.destiny.hub_name)
                pool.remove(con)
                progressed = True
        if not list_insert:
            break
        list_ordenadas.append(list_insert[:])
        list_insert.clear()
        name_hilo = name_hilo_two.copy()
        name_hilo_two.clear()
            
        # Quedan conexiones que no encajan en ningún nivel: rompemos para evitar bucle
        if not progressed:
            break
    
    return list_ordenadas


            




# def path(list_connect: List[Connection], dron: Dron, K: int = 3) -> List[Tuple[int, List[Hub], int]]:
def path(list_connect: List[Connection], dron: Dron) -> List[List[Connection]]:
    '''
    En principio devuelve una lista con todas las posibles combinaciones a end ordenadas por menores movimientos posibles y ordenadas mas prioritarias primero
    '''

    start_name = dron.posicion_actual
    star_hub = dron.hub
    end_name = ''
    end_hub = None

    for con in list_connect:
        if con.destiny.end == True:
            end_name = con.destiny.hub_name
            end_hub = con.destiny

    if not start_name or not end_name:
        return []    
    if start_name == end_name:
        return[]
    
    # Agrupar conexiones por niveles
    list_ordenadas = lista_de_lista(list_connect)
    print("\n=== NIVELES AGRUPADOS ===")
    for i, nivel in enumerate(list_ordenadas):
        print(f"Nivel {i}:")
        for c in nivel:
            print(f"  {c.origin.hub_name} -> {c.destiny.hub_name}")

    # Generar todas las rutas válidas
    rutas = create_rut(list_ordenadas)

    # Mostrar rutas legibles
    print_rutas(rutas)

    return rutas



