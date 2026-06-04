# src/algorithm/prioritized_planner.py

from typing import List, Tuple, Any, Optional, Dict, cast
from src.object.Connection import Connection
from src.object.Hub import Hub


class Planner:
    def __init__(self):
        pass

    @staticmethod
    def _is_connection(obj: object) -> bool:
        return hasattr(obj, "origin") and hasattr(obj, "destiny")

    @staticmethod
    def _is_hub(obj: object) -> bool:
        return hasattr(obj, "hub_name")

    def _explore_route(
        self,
        connection_actual: Connection,
        ruta_actual: List[Connection],
        list_connect: List[Connection],
        all_routes: List[List[Connection]]
    ) -> None:
        destination_rut = connection_actual.destiny

        if destination_rut.end:
            all_routes.append(ruta_actual)
            return

        conteo_hubs: Dict[str, int] = {}
        for c in ruta_actual:
            nombre = c.origin.hub_name
            conteo_hubs[nombre] = conteo_hubs.get(nombre, 0) + 1

        for con in list_connect:
            if con.origin.hub_name == destination_rut.hub_name:
                veces = conteo_hubs.get(con.destiny.hub_name, 0)
                if veces >= 2:
                    continue
                nueva_ruta = ruta_actual + [con]
                self._explore_route(con, nueva_ruta, list_connect, all_routes)

    def _find_routes_from_start(
        self,
        list_connect: List[Connection]
    ) -> List[List[Connection]]:
        all_routes: List[List[Connection]] = []
        home_connections: List[Connection] = []

        for con in list_connect:
            if con.origin.start:
                home_connections.append(con)

        for connection in home_connections:
            initial_path = [connection]
            self._explore_route(connection, initial_path, list_connect, all_routes)
        return all_routes

    def _count_repetitions(self, ruta: List[Connection]) -> int:
        counter: Dict[Tuple[str, str], int] = {}
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

    def _sort_all_routes(
        self,
        all_routes: List[List[Connection]]
    ) -> List[Tuple[int, Tuple[Connection, ...], int, int]]:
        def calculate_metadata(ruta: List[Connection]) -> Tuple[int, int, int]:
            turns = 0
            priority = 0
            for con in ruta:
                turns += 1
                if con.destiny.zone == 'restricted':
                    turns += 1
                elif con.origin.zone == 'priority':
                    priority += 1
            repetitions = self._count_repetitions(ruta)
            return turns, priority, repetitions

        metadata_list: List[Tuple[int, Tuple[Connection, ...], int, int]] = []
        for ruta in all_routes:
            turns, priority, repetitions = calculate_metadata(ruta)
            metadata_list.append((turns, tuple(ruta), priority, repetitions))

        def criterio_orden(item: Tuple[int, Tuple[Connection, ...], int, int]) -> Tuple[int, int, int]:
            turns, _, priority, repetitions = item
            return (repetitions, turns, -priority)

        metadata_list.sort(key=criterio_orden)
        return metadata_list

    def compute_routes(self, list_connect: List[Connection]) -> List[List[Connection]]:
        all_routes = self._find_routes_from_start(list_connect)
        ordered_paths = self._sort_all_routes(all_routes)
        end_paths: List[List[Connection]] = [list(ruta) for _, ruta, _, _ in ordered_paths]
        return end_paths

    def _route_by_turns(self, conns: List[Any]) -> List[List[List[Any]]]:
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

    def _expand_routes(self, rutas_input: List[Any]) -> List[List[List[List[Any]]]]:
        broken_out_routes: List[List[List[List[Any]]]] = []
        for ruta in rutas_input:
            route_conns = None
            if (
                isinstance(ruta, (list, tuple))
                and len(ruta) >= 2
                and isinstance(ruta[1], (list, tuple))
            ):
                route_conns = list(ruta[1])
            elif isinstance(ruta, list) and ruta and self._is_connection(ruta[0]):
                route_conns = ruta
            else:
                try:
                    maybe = list(ruta)
                    if maybe and self._is_connection(maybe[0]):
                        route_conns = maybe
                except Exception:
                    route_conns = None

            if not route_conns:
                continue

            broken_out_routes.append(self._route_by_turns(route_conns))

        return broken_out_routes

    def _extract_connection(self, paso1: Any) -> Optional[Connection]:
        if isinstance(paso1, (list, tuple)):
            for obj in paso1:
                if self._is_connection(obj):
                    return cast(Connection, obj)
        return None

    def _extract_destination(self, paso2: Any) -> Optional[Hub]:
        if isinstance(paso2, (list, tuple)) and paso2:
            for obj in paso2:
                if self._is_hub(obj):
                    return cast(Hub, obj)
        return None

    def _check_and_generate_plan(
        self,
        shift_route: List[List[List[Any]]],
        start_shift: int,
        uso_hubs: Dict[Tuple[str, int], int],
        connections_use: Dict[Tuple[Tuple[str, str], int], int],
        max_turns_search: int = 1000,
    ) -> Tuple[bool, List[Any]]:
        def get_val(d: Dict[Any, int], k: Any, default: int = 0) -> int:
            return d.get(k, default)

        plan: List[Any] = [None] * start_shift

        if start_shift + len(shift_route) > max_turns_search:
            return False, []

        for i, turno in enumerate(shift_route):
            if not (isinstance(turno, (list, tuple)) and len(turno) == 2):
                return False, []

            paso1, paso2 = turno
            real_shift = start_shift + i

            connection = self._extract_connection(paso1)
            if connection is not None:
                key_con = (connection.origin.hub_name, connection.destiny.hub_name)
                max_link = int(connection.max_link_capacity)
                if get_val(connections_use, (key_con, real_shift), 0) >= max_link:
                    return False, []

            destination = self._extract_destination(paso2)
            if destination is not None:
                dest_name = destination.hub_name
                if dest_name != "start":
                    max_drones = int(destination.max_drones)
                    if get_val(uso_hubs, (dest_name, real_shift), 0) >= max_drones:
                        return False, []

            plan.append(turno)

        return True, plan

    def _register_usage(
        self,
        shift_route: List[List[List[Any]]],
        start_shift: int,
        uso_hubs: Dict[Tuple[str, int], int],
        connections_use: Dict[Tuple[Tuple[str, str], int], int],
    ) -> None:
        for i, turno in enumerate(shift_route):
            paso1, paso2 = turno
            real_shift = start_shift + i

            connection = self._extract_connection(paso1)
            if connection is not None:
                key_con = (connection.origin.hub_name, connection.destiny.hub_name)
                connections_use[(key_con, real_shift)] = connections_use.get(
                    (key_con, real_shift), 0
                ) + 1

            destination = self._extract_destination(paso2)
            if destination is not None:
                dest_name = destination.hub_name
                if dest_name != "start":
                    uso_hubs[(dest_name, real_shift)] = uso_hubs.get(
                        (dest_name, real_shift), 0
                    ) + 1

    def assign_routes_to_drones(self, ordered_paths: List[Any], list_drones: List[Any]) -> List[Any]:
        max_search_turns = len(ordered_paths) * 55
        uso_hubs: Dict[Tuple[str, int], int] = {}
        connections_use: Dict[Tuple[Tuple[str, str], int], int] = {}

        broken_out_routes = self._expand_routes(ordered_paths)

        assigned_drones = []

        for dron in list_drones:
            assigned = False

            for start_shift in range(0, max_search_turns):
                for shift_route in broken_out_routes:
                    valido, plan = self._check_and_generate_plan(
                        shift_route, start_shift, uso_hubs, connections_use
                    )
                    if valido:
                        dron.route_positions = plan
                        self._register_usage(
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