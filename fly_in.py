import sys
from src.parsing import Parse

if __name__ == '__main__':

    arguments = sys.argv[1:]
    parse = Parse(arguments)

    if parse.validate_args():
        parse.open_document()

        from src.start_program import Application
        # from src import start_program as start
        # from src import print_program as printp
        from src.print_program import Printer

        app = Application(parser=parse)
        app.printer = Printer()
        app.run()

        # list_drones, list_hub, list_connect = start.list_object(arguments[0])

        # printp.print_launch_drones(list_drones)

        # start.start_program(list_drones, list_hub, list_connect)

    else:
        print("\033[31m", '\nEND OF PROGRAM - SEE YOU SOON!\n', "\033[1;33m")
        sys.exit(1)
