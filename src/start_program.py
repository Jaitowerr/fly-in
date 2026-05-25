from src.object.Dron import Dron
from src.object.Hub import Hub
from src.object.Connection import Connection
from src.algorithm import prioritized_planner as algorith


def return_hub(hub: list, zone_type: str = None) -> None:
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

    # print(dict_hub)
    #     line = line.split()

    return dict_hub


def list_object(args: str) -> tuple:
    # def program(args: str) -> None:
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
                        dron.posicion_actual = hub.hub_name
                        # dron.posicion_actual = hub.hub_name
                    # dron.print_dron()  # printea los drones y su contenido eliminar tras fin programa

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
                    metadata = parts[1].split('=')[1][:1]
                    dict_connect['max_link_capacity'] = metadata
                list_connect.append(Connection(**dict_connect))

    print(f"\nTotal de DRONES creados: {len(list_drones)}")
    for drone in list_drones:
        print(f'  - Drone ID: DR-{drone.id_dron}')

    print(f'\nTotal HUBS creado: {len(list_hub)}')
    for hub in list_hub:
        print(
            f'  - Name: {hub.hub_name}, {hub.x}, {hub.y}, {hub.color}, {hub.zone}')
    # return list_drones, list_hub

    print(f'\nTotal CONEXIONES creadas: {len(list_connect)}')
    for conx in list_connect:
        print(f'  - ', conx.origin.hub_name,
              conx.destiny.hub_name, conx.max_link_capacity)

    return list_drones, list_hub, list_connect

def todos_llegan(list_drones: list, list_hubs: Hub)-> bool:
    '''COmpruebo que todos estén en end'''
    
    bool_end = []
    
    for dron in list_drones:
        bool_end.append(dron.hub.end)
    
    return all(bool_end)

def start_program(list_drones: Dron, list_hubs: Hub, list_connect:Connection)-> None :
    list_con_limpia, list_con_blocked = [], []

    for i, con in enumerate(list_connect):
        if con.origin.zone == 'blocked' or con.destiny.zone == 'blocked':
            list_con_blocked.append(list_connect.pop(i))
        else:
            list_con_limpia.append(con)
    list_connect = list_con_limpia
    # print('Blocked = ', list_con_blocked)
    # print('List connect limpio = ', list_connect)
    # print(list_drones)
    turnos = 0
    while not todos_llegan(list_drones, list_hubs):
        turnos += 1
        print('Turno ::::  ', turnos)
        algorith.path(list_connect)
        break

