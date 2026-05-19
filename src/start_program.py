from src.object.Dron import Dron
from src.object.Hub import Hub
from src.object.Connection import Connection

def return_hub(hub: list, zone_type: str = '') -> None:
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
    elif zone_type == 'end':
        dict_hub['end'] == True
    
    print(dict_hub)
    #     line = line.split()


    return dict_hub

# def program(args: str) -> tuple:
def program(args: str) -> None:
    with open(args) as file:
        list_drones = []
        dict_hub = dict()
        list_hub = []
        for line in file:

            if line.startswith('#') or line[0] == '\n':
                continue

            elif line.startswith('nb_drones: '):
                nb = int(line.split(': ', 1)[1])
                for i in range(nb):
                    list_drones.append(Dron(i))
    
            elif line.startswith('start_hub: '):
                hub = line.split(': ', 1)[1].rstrip('\n')
                hub = hub.split(' ', 3)
                dict_hub = return_hub(hub, 'start_hub')
                list_hub.append(Hub(**dict_hub))


            elif line.startswith('hub: '):
                hub = line.split(': ', 1)[1].rstrip('\n')
                hub = hub.split(' ', 3)
                dict_hub = return_hub(hub)
                list_hub.append(Hub(**dict_hub))

            elif line.startswith('end_hub: '):
                pass



    print(f"Total de drones creados: {len(list_drones)}")
    for drone in list_drones:
        print(f'Drone ID: {drone.id_dron}')

    print(f'Total Hub start creado: {len(list_hub)}')
    print(f'Name: {list_hub[0].hub_name}, {list_hub[0].x}, {list_hub[0].y}, {list_hub[0].color}, {list_hub[0].zone}')
    # return list_drones, list_hub

