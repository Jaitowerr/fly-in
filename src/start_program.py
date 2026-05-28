from src.object.Dron import Dron
from src.object.Hub import Hub
from src.object.Connection import Connection
from src.algorithm import prioritized_planner as algorith
from typing import List
from src import print_program as printp
import os


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

    print(f'\nTotal HUBS creado: {len(list_hub)}')

    print(f'\nTotal CONEXIONES creadas: {len(list_connect)}')

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
    rutas = algorith.path(list_connect)
    # nb_drn = len(list_drones)

    # print('el largo de la lista es', len(list_drones))
    lista_dron_con_ruta = algorith.asignacion_mapa(rutas, list_drones)
    
    # print('el largo de la nueva lista es', len(lista_dron_con_ruta))
    # print('---------------------')
    # for dron in lista_dron_con_ruta:
    #     print(dron.ruta_posiciones, '\n\n')
    #     break
    
    # print(lista_dron_con_ruta[0].ruta_posiciones)
    # print(lista_dron_con_ruta[1].ruta_posiciones)

    # imprimir_movimientos_drones(lista_dron_con_ruta)
    printp.imprimir_por_turnos(lista_dron_con_ruta)

    # while not todos_llegan(list_drones, list_hubs):
    #     turnos += 1
    #     print('Turno ::::  ', turnos)
    #     break
    # teclado = input()
    while True:
        print(f"\n{printp._CYAN}{'─' * 40}{printp._RESET}")
        print(f"{printp._BOLD}  1{printp._RESET} — Imprimir sin animación")
        print(f"{printp._BOLD}  2{printp._RESET} — Imprimir con animación")
        print(f"{printp._BOLD}  q{printp._RESET} — Salir")
        print(f"{printp._CYAN}{'─' * 40}{printp._RESET}")
 
        tecla = input(f"{printp._GREEN}>{printp._RESET} ").strip().lower()
 
        if tecla == '1':
            os.system('clear')
            printp.imprimir_por_turnos(lista_dron_con_ruta)
 
        elif tecla == '2':
            os.system('clear')
            printp.imprimir_con_animacion(lista_dron_con_ruta, list_hubs)
 
        elif tecla == 'q':
            print(f"\n{printp._GREEN}Hasta luego.{printp._RESET}\n")
            break
 
        else:
            print(f"{printp._RED}Opción no válida. Pulsa 1, 2 o q.{printp._RESET}")




# def imprimir_movimientos_drones(lista_drones: List[Dron]):
#     """
#     Imprime los movimientos de cada dron por turno.
#     Asegura que todos los drones que se mueven aparezcan en pantalla.
#     """
#     if not lista_drones:
#         print("No hay drones.")
#         return

#     # 1. Encontrar la duración máxima
#     max_turnos = 0
#     for d in lista_drones:
#         if hasattr(d, 'ruta_posiciones') and d.ruta_posiciones:
#             max_turnos = max(max_turnos, len(d.ruta_posiciones))

#     print(f"\nSimulación de movimientos ({len(lista_drones)} drones):")

#     for t in range(max_turnos):
#         movs_del_turno = []
#         for dron in lista_drones:
#             # Si el dron tiene un plan y estamos en ese turno
#             if hasattr(dron, 'ruta_posiciones') and t < len(dron.ruta_posiciones):
#                 paso = dron.ruta_posiciones[t]
                
#                 if paso is None:
#                     continue  # El dron está esperando (None)
                
#                 # Desglosar paso: [ [hub_org, conn], [hub_dest] ]
#                 try:
#                     paso1, paso2 = paso
#                     # Obtener nombres de forma segura
#                     org_name = getattr(paso1[0], 'hub_name', 'vuelo')
#                     dest_name = getattr(paso2[0], 'hub_name', 'vuelo')
                    
#                     movs_del_turno.append(f"{dron.id_dron}-{org_name}->{dest_name}")
#                 except:
#                     continue

#         if movs_del_turno:
#             # Imprimir todos los movimientos del turno separados por espacio
#             print(f"Turno {t + 1}: {'  '.join(movs_del_turno)}")

#     print(f"\nTotal de turnos: {max_turnos}")











# def start_program(list_drones: Dron, list_hubs: Hub, list_connect:Connection)-> None :
#     list_con_limpia, list_con_blocked = [], []

#     for i, con in enumerate(list_connect):
#         if con.origin.zone == 'blocked' or con.destiny.zone == 'blocked':
#             list_con_blocked.append(list_connect.pop(i))
#         else:
#             list_con_limpia.append(con)
#     list_connect = list_con_limpia
    
    
#     # print('Blocked = ', list_con_blocked)
#     # print('List connect limpio = ', list_connect)
#     # print(list_drones)
#     rutas = algorith.path(list_connect)
#     nb_drn = len(list_drones)


#     turnos = 0
#     lista_dron_con_ruta = algorith.asignacion_mapa(rutas, list_drones)
#     # Determinar el número máximo de turnos
#     max_turnos = 0
#     for dron in list_drones:
#         if dron.ruta_posiciones and len(dron.ruta_posiciones) > max_turnos:
#             max_turnos = len(dron.ruta_posiciones)

#     # Recorrer cada turno
#     for t in range(max_turnos):
#         movimientos = []
#         for dron in list_drones:
#             if dron.ruta_posiciones and t < len(dron.ruta_posiciones):
#                 accion = dron.ruta_posiciones[t]
#                 if accion is not None:
#                     if accion[0] == "mover":
#                         movimientos.append(f"D{dron.id_dron}-{accion[1]}->{accion[2]}")
#                     elif accion[0] == "restricted_1":
#                         movimientos.append(f"D{dron.id_dron}-{accion[1]}->{accion[2]}(restricted)")
#                     elif accion[0] == "restricted_2":
#                         movimientos.append(f"D{dron.id_dron}-{accion[1]}(llega)")
#         if movimientos:
#             print(f"Turno {t + 1}: {' '.join(movimientos)}")
#         # aqui vamos a devolver la lsita de drones, cada regresará con su ruta de conexiones guardada en Dron
#     while not todos_llegan(list_drones, list_hubs):
#         turnos += 1
#         print('Turno ::::  ', turnos)
#         break

