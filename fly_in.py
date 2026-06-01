import sys
from src import parsing

if __name__ == '__main__':
    arguments = sys.argv[1:]

    if parsing.validate_args(arguments):
        parsing.open_document(arguments[0])

        from src import start_program as start
        from src import print_program as printp

        list_drones, list_hub, list_connect = start.list_object(arguments[0])

        printp.print_launch_drones(list_drones)

        start.start_program(list_drones, list_hub, list_connect)

    else:
        print("\033[31m", '\nEND OF PROGRAM - SEE YOU SOON!\n', "\033[1;33m")
        sys.exit(1)
