from src.object.Connection import Connection
from src.object.Hub import Hub
from src.object.Dron import Dron
from typing import List, Tuple, Dict, Any


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

def print_rutas_finales(rutas_finales: List[List]) -> None:
    print('Largo de rutas', len(rutas_finales))





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

    for conexion in conexiones_inicio:
        ruta_inicial = [conexion]
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
    # print_rutas_ordenadas(rutas_ordenadas)
    # print(type(rutas_ordenadas))
    rutas_finales = [list(ruta) for _, ruta, _, _ in rutas_ordenadas]
    # print_rutas_finales(rutas_finales)

    return rutas_finales


def desglosar_todas_las_rutas(rutas: List[List[Connection]]) -> List[List[List[List[Any]]]]:
    def convertir_ruta_a_turnos(ruta: List[Connection]) -> List[List[List[Any]]]:
        """
        Convierte una ruta (lista de conexiones) en una lista de turnos.
        Cada turno es una lista de dos pasos:
           - Paso 1: [hub_origen, conexion]
           - Paso 2: [hub_destino]

        Para zonas restringidas:
           - Turno 1:
               Paso 1: [hub_origen, conexion]
               Paso 2: [conexion]
           - Turno 2:
               Paso 1: [conexion, conexion]
               Paso 2: [hub_destino]
        """

        turnos = []

        for conexion in ruta:
            origen = conexion.origin
            destino = conexion.destiny
            if destino.zone == 'restricted':
                # Turno 1
                turno1 = [
                    [origen, conexion],
                    [conexion]]
                turnos.append(turno1)
              # Turno 2
                turno2 = [
                    [conexion, conexion],
                    [destino]]
                turnos.append(turno2)
            else:
                 # Turno normal
                turno = [
                    [origen, conexion],
                    [destino]]
                turnos.append(turno)
         # print(turnos, '\n\n')

        return turnos
    
    rutas_desglosadas = []

    for ruta in rutas:
        turnos = convertir_ruta_a_turnos(ruta)
        rutas_desglosadas.append(turnos)

    return rutas_desglosadas



def _is_connection(obj) -> bool:
    return hasattr(obj, "origin") and hasattr(obj, "destiny")

def _is_hub(obj) -> bool:
    return hasattr(obj, "hub_name")

def desglosar_todas_las_rutas(rutas_input: List[Any]) -> List[List[List[List[Any]]]]:
    """
    Acepta rutas en cualquiera de estos formatos:
      - List[List[Connection]]  (ruta = lista de Connection)
      - List[Tuple[int, Tuple[Connection,...], int, int]]  (ruta con metadata)
    Devuelve: List[ruta_turnos] donde ruta_turnos = [turno1, turno2, ...]
    y cada turno = [paso1, paso2] con paso1 y paso2 listas (según tu especificación).
    """
    def ruta_a_turnos(conns: List[Any]) -> List[List[List[Any]]]:
        turnos: List[List[List[Any]]] = []
        for conexion in conns:
            origen = conexion.origin
            destino = conexion.destiny
            if getattr(destino, "zone", None) == "restricted":
                # restricted -> dos turnos
                turno1 = [[origen, conexion], [conexion]]      # queda en la conexión
                turno2 = [[conexion, conexion], [destino]]     # termina en destino
                turnos.append(turno1)
                turnos.append(turno2)
            else:
                turno = [[origen, conexion], [destino]]       # un solo turno
                turnos.append(turno)
        return turnos

    rutas_desglosadas: List[List[List[List[Any]]]] = []
    for ruta in rutas_input:
        # manejar formato con metadata: (priority, route, ..., ...)
        route_conns = None
        if isinstance(ruta, (list, tuple)) and len(ruta) >= 2 and isinstance(ruta[1], (list, tuple)):
            # caso: (priority, (conn,conn,...), ..) o similar
            route_conns = list(ruta[1])
        elif isinstance(ruta, list) and ruta and _is_connection(ruta[0]):
            # caso: [conn, conn, ...]
            route_conns = ruta
        else:
            # último intento: si ruta itself es una tuple/iterable de Connection
            try:
                maybe = list(ruta)
                if maybe and _is_connection(maybe[0]):
                    route_conns = maybe
            except Exception:
                route_conns = None

        if not route_conns:
            # ignora rutas malformadas (o lanza error si prefieres)
            continue

        rutas_desglosadas.append(ruta_a_turnos(route_conns))

    return rutas_desglosadas


def comprobar_y_generar_plan(ruta_turnos: List[List[List[Any]]],
                             turno_inicio: int,
                             uso_hubs: dict,
                             uso_conexiones: dict,
                             max_turns_search: int = 1000) -> Tuple[bool, List[Any]]:
    """
    Comprueba si la ruta_turnos (lista de turnos) se puede colocar empezando en turno_inicio.
    Devuelve (valido, plan) donde plan es lista con Nones hasta turno_inicio y luego los turnos.
    """
    def get_val(d, k, default=0):
        return d.get(k, default)

    plan: List[Any] = [None] * turno_inicio

    if turno_inicio + len(ruta_turnos) > max_turns_search:
        return False, []

    for i, turno in enumerate(ruta_turnos):
        if not (isinstance(turno, (list, tuple)) and len(turno) == 2):
            return False, []

        paso1, paso2 = turno
        turno_real = turno_inicio + i

        # --- Detectar conexión ---
        conexion = None
        if isinstance(paso1, (list, tuple)):
            for obj in paso1:
                if _is_connection(obj):
                    conexion = obj
                    break

        # --- Comprobar conexión ocupada en este turno ---
        if conexion is not None:
            key_con = (
                getattr(conexion.origin, "hub_name", None),
                getattr(conexion.destiny, "hub_name", None)
            )
            max_link = int(getattr(conexion, "max_link_capacity", 1))
            if get_val(uso_conexiones, (key_con, turno_real), 0) >= max_link:
                return False, []

        # --- Comprobar hub destino ocupado en turno de llegada ---
        destino = None
        if isinstance(paso2, (list, tuple)) and paso2:
            for obj in paso2:
                if _is_hub(obj):
                    destino = obj
                    break

        if destino is not None:
            dest_name = getattr(destino, "hub_name", None)
            if dest_name != "start":
                max_drones = int(getattr(destino, "max_drones", 1))
                if get_val(uso_hubs, (dest_name, turno_real), 0) >= max_drones:
                    return False, []

        plan.append(turno)

    return True, plan


def registrar_uso(ruta_turnos: List[List[List[Any]]],
                  turno_inicio: int,
                  uso_hubs: dict,
                  uso_conexiones: dict) -> None:
    """
    Registra ocupaciones precisas por turno para permitir solapamiento correcto.
    """
    for i, turno in enumerate(ruta_turnos):
        paso1, paso2 = turno
        turno_real = turno_inicio + i

        # --- Detectar conexión ---
        conexion = None
        if isinstance(paso1, (list, tuple)):
            for obj in paso1:
                if _is_connection(obj):
                    conexion = obj
                    break

        # --- Registrar ocupación de conexión en este turno ---
        if conexion is not None:
            key_con = (
                getattr(conexion.origin, "hub_name", None),
                getattr(conexion.destiny, "hub_name", None)
            )
            uso_conexiones[(key_con, turno_real)] = uso_conexiones.get((key_con, turno_real), 0) + 1

        # --- Registrar ocupación de hub destino ---
        destino = None
        if isinstance(paso2, (list, tuple)) and paso2:
            for obj in paso2:
                if _is_hub(obj):
                    destino = obj
                    break

        if destino is not None:
            dest_name = getattr(destino, "hub_name", None)
            if dest_name != "start":
                uso_hubs[(dest_name, turno_real)] = uso_hubs.get((dest_name, turno_real), 0) + 1


def asignacion_mapa(rutas_ordenadas: List[Any], list_drones: List[Any]) -> List[Any]:
    """
    Asigna a cada dron la mejor ruta posible respetando ocupaciones por turnos.
    Prioriza probar todas las rutas en turno 0, luego en turno 1, etc.
    """
    MAX_SEARCH_TURNS = len(rutas_ordenadas) * 55
    uso_hubs = {}
    uso_conexiones = {}

    # Convertir rutas a turnos (una sola vez)
    rutas_desglosadas = desglosar_todas_las_rutas(rutas_ordenadas)

    drones_asignados = []

    for dron in list_drones:
        asignado = False

        # Probar todas las rutas en cada turno, en orden
        for turno_inicio in range(0, MAX_SEARCH_TURNS):
            for ruta_turnos in rutas_desglosadas:
                valido, plan = comprobar_y_generar_plan(
                    ruta_turnos, turno_inicio, uso_hubs, uso_conexiones
                )
                if valido:
                    dron.ruta_posiciones = plan
                    registrar_uso(ruta_turnos, turno_inicio, uso_hubs, uso_conexiones)
                    drones_asignados.append(dron)
                    asignado = True
                    break
            if asignado:
                break

        if not asignado:
            # Si no se pudo asignar ruta, dar plan vacío o con Nones
            dron.ruta_posiciones = [None] * 10  # ajustar según necesites

    return drones_asignados

