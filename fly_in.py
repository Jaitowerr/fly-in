import sys
from src import parsing

if __name__ == '__main__':
	arguments = sys.argv[1:]
	if parsing.validate_args(arguments):
		parsing.open_document(arguments[0])
		print('Si impime esto es que va bien el parseo')
		print(arguments[0])
		from src import start
		# drones, hubs, conexion = start.program(arguments[0])
		start.program(arguments[0])

		#importar objeto
		#objeto = parsing.open_document(arguments[0])
		pass
	
	else:
		print('\nfuera ostiaaaaa\n')
		sys.exit(1)