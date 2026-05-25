from src.object.Connection import Connection
from src.object.Hub import Hub
from src.object.Dron import Dron
from typing import List, Tuple, Dict


def print_rutas(rutas: List[List]):
    if not rutas:
        print("No se encontraron rutas.")
        return
    for i, ruta in enumerate(rutas, 1):
        nombres = [con.origin.hub_name for con in ruta]
        nombres.append(ruta[-1].destiny.hub_name)
        print(f"Ruta {i}: {' -> '.join(nombres)}")


def create_rut(list_ordenadas):
    """
    Devuelve todas las rutas posibles (listas de Connection) que:
    - comienzan en una conexión con origin.start == True (nivel 0)
    - encadenan origin.hub_name == prev.destiny.hub_name entre niveles
    - terminan en una conexión con destiny.end == True
    """
    def recursiva(listas, indice=0, actual=None):
        if actual is None:
            actual = []
        # Si hemos recorrido todos los niveles, aceptamos solo si la última conexión es end
        if indice == len(listas):
            if actual and actual[-1].destiny.end:
                return [actual]
            return []

        resultado = []
        for e in listas[indice]:
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
                resultado.extend(recursiva(listas, indice + 1, nueva))

        return resultado
    return recursiva(list_ordenadas)


def lista_de_lista(list_connect:list):
    list_ordenadas = []
    list_insert = []
    name_hilo = set()
    name_hilo_two = set()

    # Primer nivel: conexiones que empiezan en start
    for con in list_connect:
        if con.origin.start == True:
            list_insert.append(con)
            list_connect.remove(con)
            name_hilo.add(con.destiny.hub_name)
    list_ordenadas.append(list_insert.copy())
    list_insert.clear()
    
    # Niveles siguientes
    while list_connect:
        for con in list_connect[:]:
            if con.origin.hub_name in name_hilo:
                list_insert.append(con)
                name_hilo_two.add(con.destiny.hub_name)
                list_connect.remove(con)
            
        name_hilo = name_hilo_two.copy()
        name_hilo_two.clear()
        list_ordenadas.append(list_insert.copy())
        list_insert.clear()
    list_rut = create_rut(list_ordenadas)

    if not list_rut:
        print("No se encontraron rutas.")
    else:
        for i, ruta in enumerate(list_rut, 1):
            nombres = [con.origin.hub_name for con in ruta]
            # añadir el hub destino del último elemento para cerrar la ruta
            if ruta:
                nombres.append(ruta[-1].destiny.hub_name)
            print(f"Ruta {i}: {' -> '.join(nombres)}")

    # print(list_rut)
            




# def path(list_connect: List[Connection], dron: Dron, K: int = 3) -> List[Tuple[int, List[Hub], int]]:
def path(list_connect: List[Connection], dron: Dron) -> None:
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
    
    list_connect = lista_de_lista(list_connect)


