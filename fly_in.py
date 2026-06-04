import sys
from src.parsing import Parse

if __name__ == '__main__':

    arguments = sys.argv[1:]
    parse = Parse(arguments)

    if parse.validate_args():
        parse.open_document()

        from src.start_program import Application

        from src.print_program import Printer

        app = Application(parser=parse)
        app.printer = Printer()
        app.run()

    else:
        print("\033[31m", '\nEND OF PROGRAM - SEE YOU SOON!\n', "\033[1;33m")
        sys.exit(1)
