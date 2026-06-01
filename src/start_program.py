from src.object.Dron import Dron
from src.object.Hub import Hub
from src.object.Connection import Connection
from src.algorithm import prioritized_planner as algorith
from src import print_program as printp
import os


def return_hub(hub: list, zone_type: str = None) -> None:
    """
    Parse a hub token list and return a dictionary suitable for Hub(**dict).

    Args:
        hub (list): List of tokens for the hub (name, x, y, [metadata]).
        zone_type (str, optional): 'start' or 'end' to mark hub type.

    Returns:
        dict: Mapping with hub fields for Hub constructor.
    """
    dict_hub = dict()
    name = hub.pop(0)
    dict_hub['hub_name'] = name
    x = hub.pop(0)
    dict_hub['x'] = x
    y = hub.pop(0)
    dict_hub['y'] = y

    if hub:
        metadata = hub.pop()
        metadata = metadata[1:-1]
        metadata = metadata.split()
        for data in metadata:
            key, value = data.split('=')
            dict_hub[key] = value
    if zone_type == 'start':
        dict_hub['start'] = True
    if zone_type == 'end':
        dict_hub['end'] = True

    return dict_hub


def list_object(args: str) -> tuple:

    with open(args) as file:
        list_drones = []
        dict_hub = dict()
        list_hub = []
        dict_connect = dict()
        list_connect = []
        for line in file:

            if line.startswith('#') or line[0] == '\n':
                continue

            elif line.startswith('nb_drones: '):
                nb = int(line.split(': ', 1)[1])
                for i in range(1, nb + 1):
                    list_drones.append(Dron(i))

            elif line.startswith('start_hub: '):
                hub = line.split(': ', 1)[1].rstrip('\n')
                hub = hub.split(' ', 3)
                dict_hub = return_hub(hub, 'start')
                list_hub.append(Hub(**dict_hub))
                for dron in list_drones:
                    for hub in list_hub:
                        dron.hub = hub
                        dron.current_position = hub.hub_name

            elif line.startswith('hub: '):
                hub = line.split(': ', 1)[1].rstrip('\n')
                hub = hub.split(' ', 3)
                dict_hub = return_hub(hub)
                list_hub.append(Hub(**dict_hub))

            elif line.startswith('end_hub: '):
                hub = line.split(': ', 1)[1].rstrip('\n')
                hub = hub.split(' ', 3)
                dict_hub = return_hub(hub, 'end')
                list_hub.append(Hub(**dict_hub))

            elif line.startswith('connection: '):
                hub = line.split(': ', 1)[1].rstrip('\n')
                parts = hub.split(' ', 1)
                names = parts[0]
                names1, names2 = names.split('-')
                for hub in list_hub:
                    if names1 == hub.hub_name:
                        dict_connect['origin'] = hub
                    if names2 == hub.hub_name:
                        dict_connect['destiny'] = hub
                if len(parts) == 2:
                    metadata = parts[1].split('=')[1]
                    dict_connect['max_link_capacity'] = metadata.rstrip(']')
                list_connect.append(Connection(**dict_connect))

    print(f"\nTotal DRONES created: {len(list_drones)}")

    print(f'\nTotal HUBS created: {len(list_hub)}')

    print(f'\nTotal CONNECTIONS created: {len(list_connect)}')

    return list_drones, list_hub, list_connect


def all_arrived(list_drones: list, list_hubs: Hub) -> bool:
    """
    Check whether all drones have reached an end hub.

    Args:
        list_drones (list): List of drone objects.
        list_hubs (List[Hub]): List of hub objects.

    Returns:
        bool: True if every drone is at a hub with end == True.
    """

    statuses = [d.hub.end for d in list_drones]
    return all(statuses)


def start_program(list_drones: Dron, list_hubs: Hub, list_connect: Connection) -> None:
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
            print(f"{printp._RED}Invalid option. Press 1, 2 or q.{printp._RESET}")
