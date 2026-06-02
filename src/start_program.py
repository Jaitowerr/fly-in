from src.object.Dron import Dron
from src.object.Hub import Hub
from src.object.Connection import Connection
from src.algorithm import prioritized_planner as algorith
from src import print_program as printp
import os
from typing import (
    List,
    Tuple,
    Dict,
    Any,
    Optional,
)


def return_hub(
    hub: List[str], zone_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Parse a hub token list and return a dictionary suitable for Hub(**dict).

    Args:
        hub (list): List of tokens for the hub (name, x, y, [metadata]).
        zone_type (str, optional): 'start' or 'end' to mark hub type.

    Returns:
        dict: Mapping with hub fields for Hub constructor.
    """
    dict_hub: Dict[str, Any] = {}
    name = hub.pop(0)
    dict_hub['hub_name'] = name
    x = hub.pop(0)
    dict_hub['x'] = x
    y = hub.pop(0)
    dict_hub['y'] = y

    if hub:
        metadata: Any = hub.pop()
        metadata = metadata[1:-1]
        metadata = metadata.split()
        for data in metadata:
            key, value = data.split('=')
            # convert numeric metadata when appropriate
            if key in ('max_drones', 'max_link_capacity'):
                try:
                    dict_hub[key] = int(value)
                except Exception:
                    dict_hub[key] = value
            else:
                dict_hub[key] = value
    if zone_type == 'start':
        dict_hub['start'] = True
    if zone_type == 'end':
        dict_hub['end'] = True

    return dict_hub


def list_object(args: str) -> Tuple[List[Dron], List[Hub], List[Connection]]:
    """
    Parse a configuration file and build model objects for the simulation.

    Reads `args` line by line and handles these directives:
      - 'nb_drones: N'        -> create N Dron objects (ids 1..N)
      - 'start_hub: ...'      -> parse hub tokens,
      create a Hub and mark as start
      - 'hub: ...'            -> parse hub tokens and create a Hub
      - 'end_hub: ...'        -> parse hub tokens, create a Hub and mark as end
      - 'connection: name1-name2 [max_link_capacity=...]'
                              -> create Connection between existing hubs

    Returns:
        tuple: (list_drones, list_hub, list_connect)

    Side effects:
        - Prints totals of created objects.
        - Assigns the start Hub to each Dron
        (dron.hub and dron.current_position).

    Notes:
        - Expects well-formed input; malformed lines may raise or produce
          incomplete objects. Validation is delegated to higher-level code.
    """
    list_drones: List[Dron] = []
    dict_hub: Dict[str, Any] = {}
    list_hub: List[Hub] = []
    dict_connect: Dict[str, Any] = {}
    list_connect: List[Connection] = []

    with open(args) as file:
        for line in file:

            if line.startswith('#') or line[0] == '\n':
                continue

            elif line.startswith('nb_drones: '):
                nb = int(line.split(': ', 1)[1])
                for i in range(1, nb + 1):
                    list_drones.append(Dron(i))

            elif line.startswith('start_hub: '):
                hub_line = line.split(': ', 1)[1].rstrip('\n')
                tokens = hub_line.split(' ', 3)
                dict_hub = return_hub(tokens, 'start')
                list_hub.append(Hub(**dict_hub))
                for dron in list_drones:
                    for hb in list_hub:
                        dron.hub = hb
                        dron.current_position = hb.hub_name

            elif line.startswith('hub: '):
                hub_line = line.split(': ', 1)[1].rstrip('\n')
                tokens = hub_line.split(' ', 3)
                dict_hub = return_hub(tokens)
                list_hub.append(Hub(**dict_hub))

            elif line.startswith('end_hub: '):
                hub_line = line.split(': ', 1)[1].rstrip('\n')
                tokens = hub_line.split(' ', 3)
                dict_hub = return_hub(tokens, 'end')
                list_hub.append(Hub(**dict_hub))

            elif line.startswith('connection: '):
                conn_line = line.split(': ', 1)[1].rstrip('\n')
                parts = conn_line.split(' ', 1)
                names = parts[0]
                names1, names2 = names.split('-')
                dict_connect = {}
                for hb in list_hub:
                    if names1 == hb.hub_name:
                        dict_connect['origin'] = hb
                    if names2 == hb.hub_name:
                        dict_connect['destiny'] = hb
                if len(parts) == 2:
                    metadata = parts[1].split('=')[1]
                    dict_connect['max_link_capacity'] = metadata.rstrip(']')
                # make a shallow copy to avoid overwriting dict_connect keys
                list_connect.append(Connection(**dict_connect.copy()))

    print(f"\nTotal DRONES created: {len(list_drones)}")

    print(f'\nTotal HUBS created: {len(list_hub)}')

    print(f'\nTotal CONNECTIONS created: {len(list_connect)}')

    return list_drones, list_hub, list_connect


def all_arrived(list_drones: List[Dron], list_hubs: List[Hub]) -> bool:
    """
    Check whether all drones have reached an end hub.

    Args:
        list_drones (list): List of drone objects.
        list_hubs (List[Hub]): List of hub objects.

    Returns:
        bool: True if every drone is at a hub with end == True.
    """

    statuses = [getattr(d.hub, 'end', False) for d in list_drones]
    return all(statuses)


def start_program(list_drones: List[Dron],
                  list_hubs: List[Hub],
                  list_connect: List[Connection]) -> None:
    """
    Main interactive routine that filters blocked connections, computes routes
    and allows the user to print the simulation in different modes.

    Args:
        list_drones (List[Dron]): Pre-created drone objects.
        list_hubs (List[Hub]): Pre-created hub objects.
        list_connect (List[Connection]): Pre-created connections.
    """
    list_con_limpia, list_con_blocked = [], []

    for i, con in enumerate(list_connect):
        if con.origin.zone == 'blocked' or con.destiny.zone == 'blocked':
            list_con_blocked.append(list_connect.pop(i))
        else:
            list_con_limpia.append(con)
    list_connect = list_con_limpia

    rutas = algorith.path(list_connect)

    assigned_drones = algorith.assign_map(rutas, list_drones)

    printp.print_by_turns(assigned_drones)

    while True:
        print(f"\n{printp._CYAN}{'─' * 40}{printp._RESET}")
        print(f"{printp._BOLD}  1{printp._RESET} — Print without animation")
        print(f"{printp._BOLD}  2{printp._RESET} — Print with animation")
        print(f"{printp._BOLD}  q{printp._RESET} — Salir")
        print(f"{printp._CYAN}{'─' * 40}{printp._RESET}")

        tecla = input(f"{printp._GREEN}>{printp._RESET} ").strip().lower()

        if tecla == '1':
            os.system('clear')
            printp.print_by_turns(assigned_drones)

        elif tecla == '2':
            os.system('clear')
            printp.print_with_animation(assigned_drones, list_hubs)

        elif tecla == 'q':
            print(f"\n{printp._GREEN}See you later.{printp._RESET}\n")
            break

        else:
            print(f"{printp._RED}Invalid option. Press 1, 2 or q."
                  f"{printp._RESET}")
