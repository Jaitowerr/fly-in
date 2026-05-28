import sys
from src import parsing

if __name__ == '__main__':
    arguments = sys.argv[1:]
    if parsing.validate_args(arguments):
        parsing.open_document(arguments[0])
        # print('Si impime esto es que va bien el parseo')
        # print(arguments[0])
        from src import start_program as start
        from src import print_program as print
        # drones, hubs, conexion = start.program(arguments[0])
        list_drones, list_hub, list_connect = start.list_object(arguments[0])

        print.imprimir_drones_arranque(list_drones)
        # print(list_drones)
        # print(list_hub)
        # print(list_connect)

        start.start_program(list_drones, list_hub, list_connect)

    else:
        print('\nfuera ostiaaaaa\n')
        sys.exit(1)






        '''
        para el proyecto con el tema de colores utilizaremos:
        from termcolor import colored
        
        print(colored("Este texto es rojo", "red"))
        print(colored("Este texto es verde", "green"))
        
        '''
