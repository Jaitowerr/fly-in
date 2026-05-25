from src.object.Connection import Connection
from src.object.Hub import Hub
from src.object.Dron import Dron
from typing import List, Tuple, Dict


def print_rutas(rutas: List[List[Connection]]) -> None:
    """
    Imprime las rutas de forma legible.
    """
    print(f"\nTotal de rutas encontradas: {len(rutas)}")
    for i, ruta in enumerate(rutas, 1):
        nombres = [con.origin.hub_name for con in ruta] + [ruta[-1].destiny.hub_name]
        ruta_str = " -> ".join(nombres)
        print(f"Ruta {i}: {ruta_str}")

def print_rutas_ordenadas(rutas_ordenadas: List[tuple]) -> None:

    print(f"\nTotal de rutas ordenadas: {len(rutas_ordenadas)}")
    for i, (turnos, ruta, prioridad, repe) in enumerate(rutas_ordenadas, 1):
        nombres = [con.origin.hub_name for con in ruta] + [ruta[-1].destiny.hub_name]
        ruta_str = " -> ".join(nombres)
        print(f"Ruta {i}: {turnos} turnos, prioridad {prioridad}, repeticiones: {repe}\n  {ruta_str}\n")




def explorar_ruta(conexion_actual: Connection, ruta_actual: List[Connection], list_connect: List[Connection], todas_las_rutas: List[List[Connection]]):
    """
    Explora recursivamente una ruta desde la conexión actual.
    """
    destino_rut = conexion_actual.destiny

    if destino_rut.end:
        todas_las_rutas.append(ruta_actual)
        return
    
    conteo_hubs = {}
    for c in ruta_actual:
        nombre = c.origin.hub_name
        conteo_hubs[nombre] = conteo_hubs.get(nombre, 0) + 1
    
    # Si no, seguimos buscando conexiones que salgan de 'destino_rut'
    for con in list_connect:
        if con.origin.hub_name == destino_rut.hub_name:
            # Añadir esta conexión a la ruta y seguir explorando
            veces = conteo_hubs.get(con.destiny.hub_name, 0)
            if veces >= 5:
                continue
            nueva_ruta = ruta_actual + [con]
            explorar_ruta(con, nueva_ruta, list_connect, todas_las_rutas)



def buscar_rutas_desde_inicio(list_connect: List[Connection]) -> List[List[Connection]]:
    """
    A partir de una lista de conexiones iniciales, explora todas las rutas posibles
    sin ciclos y terminando en un hub con end == True.
    """
    todas_las_rutas = []
    conexiones_inicio = []

    for con in list_connect:
        if con.origin.start == True:
            conexiones_inicio.append(con)

    print(f"Hay {len(conexiones_inicio)} conexiones que parten de 'start'")

    # Para cada conexión inicial, comenzamos una ruta nueva
    for conexion in conexiones_inicio:
        ruta_inicial = [conexion]
        # Llamamos a la función recursiva que sigue explorando
        explorar_ruta(conexion, ruta_inicial, list_connect, todas_las_rutas)
    return todas_las_rutas


def contar_repeticiones(ruta: List[Connection]) -> int:
    contador = {}
    for con in ruta:
        clave = (con.origin.hub_name, con.destiny.hub_name)
        if clave in contador:
            contador[clave] += 1
        else:
            contador[clave] = 1
    repeticiones = 0
    for veces in contador.values():
        if veces > 1:
            repeticiones += veces - 1

    return repeticiones


def ordenar_todas_rutas(todas_las_rutas: List[List[Connection]]) -> List[Tuple[int, Tuple[Connection, ...], int, int]]:
    '''
    Agrega un int que es la cantidad de turnos para ese mapa
    Convierte la lista de pasos a tupla o dict con key el turno
        - Quizás añadir una conexion simple o doble entre hub
    Agrega un int que es la cantidad de casillas prioritarias,
    Devuelve la lista ordenada por:
      1) turns_totales ascendente
      2) prioridad_total descendente (dentro del mismo turns)
    '''
    lista_completa = []
    for ruta in todas_las_rutas:
        turns = 0
        priority = 0
        for con in ruta:
            turns += 1
            if con.origin.zone == 'restricted':
                turns += 1
            elif con.origin.zone == 'priority':
                priority += 1
        repeticiones = contar_repeticiones(ruta)
        lista_completa.append((turns, tuple(ruta), priority, repeticiones))

    grupos = {}
    for ruta_datos in lista_completa:
        _, _, _, repeticiones = ruta_datos
        if repeticiones not in grupos:
            grupos[repeticiones] = []
        grupos[repeticiones].append(ruta_datos)

    for repe in grupos:
        grupos[repe].sort(key=lambda x: (-x[2], x[0]))
    
    resultado = []
    for num_rep in sorted(grupos.keys()):
        resultado.extend(grupos[num_rep])

    return resultado
    



def path(list_connect: List[Connection])-> List[List[Connection]]:
    """
    Busca todas las rutas posibles desde hubs marcados como start hasta hubs end.

    Args:
        list_connect (List[Connection]): Lista completa de conexiones entre hubs.
        dron (Dron): Objeto dron para obtener su posición inicial.

    Returns:
        List[List[Connection]]: Lista de rutas, donde cada ruta es una lista de conexiones.
    """
    
    todas_las_rutas = buscar_rutas_desde_inicio(list_connect)
    # print_rutas(todas_las_rutas)
    rutas_ordenadas = ordenar_todas_rutas(todas_las_rutas)
    print_rutas_ordenadas(rutas_ordenadas)
