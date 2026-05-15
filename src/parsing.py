from typing import Any
import sys


def validate_hubs(list_parts: list, line_num: int, zone_type: str) -> tuple:
    """
    Valida los datos de una zona: nombre (str), x (int), y (int), [metadata] (opcional)
    Devuelve: (nombre, x, y, metadata_str, errores)
    """
    errors = []
    name = None
    x = None
    y = None
    metadata = None
    zone_types = ['normal', 'blocked', 'restricted', 'priority']
    colors = ['green', 'yellow', 'red', 'blue', 'gray']

    if len(list_parts) < 3:
        errors.append(f"Faltan datos en {zone_type}, linea {line_num}")
        return name, x, y, errors
    
    name = list_parts[0]
    if not isinstance(name, str):
        errors.append(f"Nombre debe ser texto, linea {line_num}")

    try:
        x = int(list_parts[1])
        y = int(list_parts[2])
    except:
        errors.append(f"Coordenadas deben ser enteros, linea {line_num}")

    # print(len(list_parts))
    if len(list_parts) == 4:
        metadata = list_parts[3]
        if not (metadata.startswith('[') and metadata.endswith(']')):
            errors.append(f"Metadata debe ir entre corchetes [], linea {line_num}")
        else:
            metadata = metadata[1:-1]
            metadata = metadata.split()
            print(metadata)
            for data in metadata:
                if '=' not in data:
                    errors.append(f"Metadata inválida: {data}, no contiene '=' linea {line_num}")
                    continue

                key, val = data.split('=', 1)

                if key == 'color':
                    if val not in colors:
                        errors.append(f"Color no permitido: {val}, linea {line_num}")

                elif key == 'max_drones':
                    try:
                        int(val)
                    except:
                        errors.append(f"max_drones debe ser número entero: {val}, linea {line_num}")
                
                elif key == 'max_link_capacity':
                    try:
                        int(val)
                    except:
                        errors.append(f"max_link_capacity debe ser número: {val}, linea {line_num}")

                elif key == 'zone':
                    if val not in zone_types:
                        errors.append(f"Tipo de zona no válido: {val}, linea {line_num}")
                else:
                    errors.append(f'Comrpueba los metadatos, no es correcto el metadato introducido {data} en la linea {line_num}')
    

    return name, x, y, errors



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
      

def open_document(args: str) -> None:
    errores = []
    required = {'nb_drones': False, 'start_hub': False, 'hub': False, 'end_hub': False, 'connection': False}
    line_docu = 0
    zones_names = []
    posiciones_xy = []
    with open(args) as file:
        for line in file:
            line_docu += 1

            if line.startswith('#') or line[0] == '\n':
                continue
          
            if line.startswith('nb_drones: '):
                if required['nb_drones']:
                    errores.append(f'nb_drones aparece más de una vez, linea {line_docu}')
              
                try:
                    nb = int(line.split(': ', 1)[1])
                    required['nb_drones'] = True
                    print(f"Número de drones: {nb}")
                except:
                    errores.append('Comprueba que sea <nb_drones: 5')


                  
            if line.startswith('start_hub: '):
                if required['start_hub']:
                    errores.append(f'start_hub aparece más de una vez, linea {line_docu}')

                else:
                    try:
                        line_clean = line.split(': ', 1)[1].rstrip('\n')
                        parts = line_clean.split(' ', 3)
                        # print(parts)
                        name, x, y, errs = validate_hubs(parts, line_docu, 'start_hub')
                        if errs:
                            errores.extend(errs)
                        if name in zones_names:
                            errores.append(f"Nombre de zona repetido: {name}, linea {line_docu}")
                        else:
                            zones_names.append(name)
                        if (x, y) in posiciones_xy:
                            errores.append(f"Posición repetida: ({x},{y}), linea {line_docu}")
                        else:
                            posiciones_xy.append((x, y))

                        required['start_hub'] = True
                        print(f"Start hub válido, linea {line_docu}", parts)

                    except:
                        errores.append(f'start_hub no tiene formato válido (ej: start_hub: start 0 0 [color=green]), linea {line_docu}')






            if line.startswith('hub'):
                    try:
                        required['hub'] = True
                    except:
                        pass




            if line.startswith('end_hub:'):
                if required['end_hub']:
                    errores.append(f'end_hub aparece más de una vez, linea {line_docu}')

                else:
                    try:
                        required['end_hub'] = True
                    except:
                        pass



            if line.startswith('connection'):
                    try:
                        required['connection'] = True
                    except:
                        pass

    if not all(required.values()):
        errores.append('Faltan lineas con claves obligatorias')
    if errores:
        print('Errores:')
        for error in errores:
            print(f'  - {error}')
        sys.exit(1)