from typing import Any


def validate_args(args: Any) -> bool:

    errors = []

    if len(args) > 1:
        errors.append('Hay mas de un argumento, por favor, <fly_in.py> <archivo.txt>')

    if len(args) < 1:
        errors.append('Falta el archivo de configuración, por favor, <fly_in.py> <archivo.txt>')

    if len(args) and not args[0].endswith('.txt'):
        errors.append('Asegurate que el archivo que acompaña al nombre del archivo sea .txt <achivo.txt>') 

    if errors:
        print('Errors:')
        for error in errors:
            print(f'    - {error}')
        return False
    
    return True
        

def open_document(args: str) ->object:
    with open(args) as file:
        for line in file:
            if line[0] == '#' or line[0] == '\n':
                continue
            

        

