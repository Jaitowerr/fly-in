from src.object.Connection import Connection
from typing import List, Tuple, Any


def print_routes(rutas: List[List[Connection]]) -> None:
    """Print routes in a human-readable format.
    Args:
     rutas: A list of routes, where each route is a list of Connection objects.
    """
    print(f"\nTotal routes found: {len(rutas)}")
    for i, ruta in enumerate(rutas, 1):
        nombres = [con.origin.hub_name for con in ruta] + \
            [ruta[-1].destiny.hub_name]
        ruta_str = " -> ".join(nombres)
        print(f"Route {i}: {ruta_str}")


def print_ordered_routes(ordered_paths: List[tuple]) -> None:
    """Print ordered routes with metadata.

    Args:
        ordered_paths: List of tuples containing route metadata and the route.
    """
    print(f"\nTotal ordered routes: {len(ordered_paths)}")
    for i, (turnos, ruta, prioridad, repe) in enumerate(ordered_paths, 1):
        nombres = [con.origin.hub_name for con in ruta] + \
            [ruta[-1].destiny.hub_name]
        ruta_str = " -> ".join(nombres)
        print(
            f'Route {i}: {turnos} turns, '
            f'priority {prioridad}, '
            f'repetitions: {repe}\n  {ruta_str}\n')


def print_routes_finales(end_paths: List[List]) -> None:
    print('Routes length', len(end_paths))


def explore_route(
    connection_actual: Connection,
    ruta_actual: List[Connection],
    list_connect: List[Connection],
    all_routes: List[List[Connection]]
):
    """Recursively explore a route starting from the current connection.

    This function collects all acyclic routes that end at a hub with the
    ``end`` flag set. It limits repeated visits to the same hub to avoid
    excessive cycles.

    Args:
        connection_actual: The current Connection being explored.
        ruta_actual: The route accumulated so far (list of Connection).
        list_connect: The full list of available connections.
        all_routes: Accumulator list to which completed routes are appended.
    """
    destination_rut = connection_actual.destiny

    if destination_rut.end:
        all_routes.append(ruta_actual)
        return

    conteo_hubs = {}
    for c in ruta_actual:
        nombre = c.origin.hub_name
        conteo_hubs[nombre] = conteo_hubs.get(nombre, 0) + 1

    for con in list_connect:
        if con.origin.hub_name == destination_rut.hub_name:
            veces = conteo_hubs.get(con.destiny.hub_name, 0)
            if veces >= 5:
                continue
            nueva_ruta = ruta_actual + [con]
            explore_route(con, nueva_ruta, list_connect, all_routes)


def find_routes_from_start(
    list_connect: List[Connection]
) -> List[List[Connection]]:
    """Find all acyclic routes starting at hubs marked as start.

    Args:
        list_connect: Full list of Connection objects in the map.

    Returns:
        A list of routes where each route is a list of Connection objects and
        ends at a hub where ``end`` is True.
    """
    all_routes = []
    home_connections = []

    for con in list_connect:
        if con.origin.start:
            home_connections.append(con)

    for connection in home_connections:
        initial_path = [connection]
        explore_route(connection, initial_path, list_connect, all_routes)
    return all_routes


def count_repetitions(ruta: List[Connection]) -> int:
    """Count repeated connection usages within a route.

    Args:
        ruta: A list of Connection objects forming the route.

    Returns:
        The number of repeated traversals (connections visited more than once).
    """
    counter = {}
    for con in ruta:
        clave = (con.origin.hub_name, con.destiny.hub_name)
        if clave in counter:
            counter[clave] += 1
        else:
            counter[clave] = 1
    repetitions = 0
    for veces in counter.values():
        if veces > 1:
            repetitions += veces - 1

    return repetitions


def sort_all_routes(
    all_routes: List[List[Connection]]
) -> List[Tuple[int, Tuple[Connection, ...], int, int]]:
    """Ordena rutas por:
       1. Menos repeticiones
       2. Luego por longitud (menor primero)
       3. Luego por prioridad (mayor primero)
    """

    def calcular_metadata(ruta: List[Connection]) -> Tuple[int, int, int]:
        turns = 0
        priority = 0
        for con in ruta:
            turns += 1
            if con.origin.zone == 'restricted':
                turns += 1
            elif con.origin.zone == 'priority':
                priority += 1
        repetitions = count_repetitions(ruta)
        return turns, priority, repetitions

    # Calcular metadata
    metadata_list = []
    for ruta in all_routes:
        turns, priority, repetitions = calcular_metadata(ruta)
        metadata_list.append((turns, tuple(ruta), priority, repetitions))

    # Función de ordenación
    def criterio_orden(item):
        turns, _, priority, repetitions = item
        # Orden: (repeticiones ASC, largo ASC, prioridad DESC)
        return (repetitions, turns, -priority)

    # Ordenar todo junto
    metadata_list.sort(key=criterio_orden)

    return metadata_list


def path(list_connect: List[Connection]) -> List[List[Connection]]:
    """Find all possible routes from hubs marked as start to hubs marked
    as end.


    Args:
        list_connect: Full list of Connection objects between hubs.

    Returns:
        A list of routes, where each route is a list of Connection objects.
    """

    all_routes = find_routes_from_start(list_connect)
    ordered_paths = sort_all_routes(all_routes)
    end_paths = [list(ruta) for _, ruta, _, _ in ordered_paths]

    return end_paths


def _is_connection(obj) -> bool:
    return hasattr(obj, "origin") and hasattr(obj, "destiny")


def _is_hub(obj) -> bool:
    return hasattr(obj, "hub_name")


def _route_by_turns(conns: List[Any]) -> List[List[List[Any]]]:
    """Convert a list of connections into per-turn steps."""
    turnos: List[List[List[Any]]] = []
    for connection in conns:
        origin = connection.origin
        destination = connection.destiny
        if getattr(destination, "zone", None) == "restricted":
            turno1 = [[origin, connection], [connection]]
            turno2 = [[connection, connection], [destination]]
            turnos.append(turno1)
            turnos.append(turno2)
        else:
            turno = [[origin, connection], [destination]]
            turnos.append(turno)
    return turnos


def expand_routes(rutas_input: List[Any]) -> List[List[List[List[Any]]]]:
    """Expand routes into per-turn steps.

    Accepts routes in either of the following formats:
      - List[List[Connection]]  (route as a list of Connection)
      - List[Tuple[int, Tuple[Connection,...], int, int]]  (route with
        metadata)

    Returns:
        A list of route_turns where each route_turns = [turn1, turn2, ...] and
        each turn = [step1, step2] with step1 and step2 lists as specified.
    """
    broken_out_routes: List[List[List[List[Any]]]] = []
    for ruta in rutas_input:
        route_conns = None
        if (
            isinstance(ruta, (list, tuple))
            and len(ruta) >= 2
            and isinstance(ruta[1], (list, tuple))
        ):
            route_conns = list(ruta[1])
        elif isinstance(ruta, list) and ruta and _is_connection(ruta[0]):
            route_conns = ruta
        else:
            try:
                maybe = list(ruta)
                if maybe and _is_connection(maybe[0]):
                    route_conns = maybe
            except Exception:
                route_conns = None

        if not route_conns:
            continue

        broken_out_routes.append(_route_by_turns(route_conns))

    return broken_out_routes


def _extract_connection(paso1):
    """Extract the first Connection object from a step list."""
    if isinstance(paso1, (list, tuple)):
        for obj in paso1:
            if _is_connection(obj):
                return obj
    return None


def _extract_destination(paso2):
    """Extract the first hub object from a step list."""
    if isinstance(paso2, (list, tuple)) and paso2:
        for obj in paso2:
            if _is_hub(obj):
                return obj
    return None


def check_and_generate_plan(shift_route: List[List[List[Any]]],
                            start_shift: int,
                            uso_hubs: dict,
                            connections_use: dict,
                            max_turns_search: int = 1000
                            ) -> Tuple[bool, List[Any]]:
    """Check whether a route (in per-turn form) can be placed starting at
    a given turn.

    Args:
        shift_route: Route represented as a list of turns.
        start_shift: The earliest turn index to try placing the route.
        uso_hubs: Dictionary tracking hub occupancy per (hub_name, turn).
        connections_use: Dictionary tracking connection occupancy per
            ((origin,dest), turn).
        max_turns_search: Maximum allowed timeline length for search.

    Returns:
        A tuple (valid, plan) where valid is True if placement is possible
        and plan is the list containing None placeholders up to start_shift
        followed by the turns.
    """
    def get_val(d, k, default=0):
        return d.get(k, default)

    plan: List[Any] = [None] * start_shift

    if start_shift + len(shift_route) > max_turns_search:
        return False, []

    for i, turno in enumerate(shift_route):
        if not (isinstance(turno, (list, tuple)) and len(turno) == 2):
            return False, []

        paso1, paso2 = turno
        real_shift = start_shift + i

        connection = _extract_connection(paso1)
        if connection is not None:
            key_con = (
                getattr(connection.origin, "hub_name", None),
                getattr(connection.destiny, "hub_name", None)
            )
            max_link = int(getattr(connection, "max_link_capacity", 1))
            if get_val(connections_use, (key_con, real_shift), 0) >= max_link:
                return False, []

        destination = _extract_destination(paso2)
        if destination is not None:
            dest_name = getattr(destination, "hub_name", None)
            if dest_name != "start":
                max_drones = int(getattr(destination, "max_drones", 1))
                if get_val(uso_hubs, (dest_name, real_shift), 0) >= max_drones:
                    return False, []

        plan.append(turno)

    return True, plan


def register_usage(shift_route: List[List[List[Any]]],
                   start_shift: int,
                   uso_hubs: dict,
                   connections_use: dict) -> None:
    """Register precise per-turn occupancies so overlaps are tracked correctly.

    This function increments counters in `uso_hubs` and `connections_use`
    for each occupied hub or connection at the corresponding turn.
    """
    for i, turno in enumerate(shift_route):
        paso1, paso2 = turno
        real_shift = start_shift + i

        connection = _extract_connection(paso1)
        if connection is not None:
            key_con = (
                getattr(connection.origin, "hub_name", None),
                getattr(connection.destiny, "hub_name", None)
            )
            connections_use[(key_con, real_shift)] = connections_use.get(
                (key_con, real_shift), 0) + 1

        destination = _extract_destination(paso2)
        if destination is not None:
            dest_name = getattr(destination, "hub_name", None)
            if dest_name != "start":
                uso_hubs[(dest_name, real_shift)] = uso_hubs.get(
                    (dest_name, real_shift), 0) + 1


def assign_map(ordered_paths: List[Any], list_drones: List[Any]) -> List[Any]:
    """Assign the best possible route to each drone respecting per-turn
    occupancies.

    The algorithm tries all routes for each drone starting at turn 0,
    then 1, etc.

    Args:
        ordered_paths: Ordered list of routes (or routes with metadata).
        list_drones: List of drone objects to assign routes to.

    Returns:
        List of drones that were successfully assigned a plan (with their plan
        stored on the drone object as ``route_positions``).
    """
    max_search_turns = len(ordered_paths) * 55
    uso_hubs = {}
    connections_use = {}

    broken_out_routes = expand_routes(ordered_paths)

    assigned_drones = []

    for dron in list_drones:
        assigned = False

        for start_shift in range(0, max_search_turns):
            for shift_route in broken_out_routes:
                valido, plan = check_and_generate_plan(
                    shift_route, start_shift, uso_hubs, connections_use
                )
                if valido:
                    dron.route_positions = plan
                    register_usage(
                        shift_route, start_shift, uso_hubs, connections_use
                    )
                    assigned_drones.append(dron)
                    assigned = True
                    break

            if assigned:
                break

        if not assigned:
            dron.route_positions = [None] * 10

    return assigned_drones
