from src.object.Dron import Dron
from src.object.Hub import Hub
from src.object.Connection import Connection



# def program(args: str) -> tuple:
def program(args: str) -> None:
    with open(args) as file:
        list_drones = []
        for line in file:

            if line.startswith('#') or line[0] == '\n':
                continue

            if line.startswith('nb_drones: '):
                nb = int(line.split(': ', 1)[1])
                for i in range(nb):
                    list_drones.append(Dron(i))
    
    print(f"Total de drones creados: {len(list_drones)}")
    for drone in list_drones:
        print(f'Drone ID: {drone.id_dron}')



