from typing import Any
import sys


def validate_hubs(list_parts: list, line_num: int, zone_type: str, blocked_list: set) -> tuple:
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
    colors = ['green', 'yellow', 'red', 'blue', 'gray', 'darked', 'gold', 'black', 'marron',
              'orange', 'brown', 'purple', 'maroon', 'darkred', 'violet', 'crimson', 'rainbow',
              'cyan', 'lime', 'magenta']

    if len(list_parts) < 3:
        errors.append(f"Faltan datos en {zone_type}, linea {line_num}")
        return name, x, y, errors, blocked_list

    name = list_parts[0]
    if not isinstance(name, str):
        errors.append(f"Nombre debe ser texto, linea {line_num}")
    else:
        if '-' in name:
            errors.append(
                f"El nombre de la zona no puede contener guiones '-': {name}, linea {line_num}")

    try:
        x = int(list_parts[1])
        y = int(list_parts[2])
    except:
        errors.append(f"Coordenadas deben ser enteros, linea {line_num}")

    # print(len(list_parts))
    if len(list_parts) == 4:
        metadata = list_parts[3]
        if not (metadata.startswith('[') and metadata.endswith(']')):
            errors.append(
                f"Metadata debe ir entre corchetes [], linea {line_num}")
        else:
            metadata = metadata[1:-1]
            metadata = metadata.split()
            # print(metadata)
            for data in metadata:
                if '=' not in data:
                    errors.append(
                        f"Metadata inválida: {data}, no contiene '=' linea {line_num}")
                    continue

                key, val = data.split('=', 1)

                if key == 'color':
                    if val not in colors:
                        errors.append(
                            f"Color no permitido: {val}, linea {line_num}")

                elif key == 'max_drones':
                    try:
                        int(val)
                    except:
                        errors.append(
                            f"max_drones debe ser número entero: {val}, linea {line_num}")

                elif key == 'max_link_capacity':
                    try:
                        int(val)
                    except:
                        errors.append(
                            f"max_link_capacity debe ser número: {val}, linea {line_num}")

                elif key == 'zone':
                    if val not in zone_types:
                        errors.append(
                            f"Tipo de zona no válido: {val}, linea {line_num}")
                    elif val == 'blocked':
                        blocked_list.add(name)
                else:
                    errors.append(
                        f'Comrpueba los metadatos, no es correcto el metadato introducido {data} en la linea {line_num}')

    return name, x, y, errors, blocked_list


def validate_args(args: Any) -> bool:

    errors = []

    if len(args) > 1:
        errors.append(
            'Hay mas de un argumento, por favor, <fly_in.py> <archivo.txt>')

    if len(args) < 1:
        errors.append(
            'Falta el archivo de configuración, por favor, <fly_in.py> <archivo.txt>')

    if len(args) and not args[0].endswith('.txt'):
        errors.append(
            'Asegurate que el archivo que acompaña al nombre del archivo sea .txt <achivo.txt>')

    if errors:
        print('Errors:')
        for error in errors:
            print(f'    - {error}')
        return False

    return True


def sin_salida(conexions: list, start: str, end: str, blocked_list: set) -> bool:
    """
    Comprueba si existe un camino entre inicio y fin evitando zonas bloqueadas.
    Devuelve:
        True: si NO hay salida (no se puede llegar)
        False: si SÍ hay salida (se puede llegar)
    """
    if start in blocked_list or end in blocked_list:
        return True
    grafo = {}
    for a, b in conexions:
        if a not in grafo:
            grafo[a] = []
        if b not in grafo:
            grafo[b] = []
        grafo[a].append(b)
        grafo[b].append(a)

    por_visitar = [start]
    visitadas = set()

    while por_visitar:
        zona = por_visitar.pop(0)

        if zona in visitadas or zona in blocked_list:
            continue

        visitadas.add(zona)

        if zona == end:
            return False

        for vecino in grafo.get(zona, []):
            if vecino not in visitadas and vecino not in blocked_list:
                por_visitar.append(vecino)
    return True


def open_document(args: str) -> None:
    errores = []
    required = {'nb_drones': False, 'start_hub': False,
                'hub': False, 'end_hub': False, 'connection': False}
    line_docu = 0
    zones_names = []
    posiciones_xy = []
    conexion = []
    start_hub = str()
    end_hub = str()
    blocked_zones = set()
    with open(args) as file:
        nb = 0
        for line in file:
            line_docu += 1

            if line.startswith('#') or line[0] == '\n':
                continue

            elif line.startswith('nb_drones: '):
                if required['nb_drones']:
                    errores.append(
                        f'nb_drones aparece más de una vez, linea {line_docu}')

                try:
                    nb = int(line.split(': ', 1)[1])
                    required['nb_drones'] = True
                    # print(f"Número de drones: {nb}")
                except:
                    errores.append('Comprueba que sea <nb_drones: 5')

            elif line.startswith('start_hub: '):
                if required['start_hub']:
                    errores.append(
                        f'start_hub aparece más de una vez, linea {line_docu}')

                else:
                    try:
                        line_clean = line.split(': ', 1)[1].rstrip('\n')
                        parts = line_clean.split(' ', 3)
                        # print(parts)
                        name, x, y, errs, blocked_zones = validate_hubs(
                            parts, line_docu, 'start_hub', blocked_zones)
                        if errs:
                            errores.extend(errs)
                        if name in zones_names:
                            errores.append(
                                f"Nombre de zona repetido: {name}, linea {line_docu}")
                        else:
                            zones_names.append(name)
                            start_hub = name

                        if (x, y) in posiciones_xy:
                            errores.append(
                                f"Posición repetida: ({x},{y}), linea {line_docu}")
                        else:
                            posiciones_xy.append((x, y))

                        required['start_hub'] = True
                        # print(f"Start hub válido, linea {line_docu}", parts)

                    except:
                        errores.append(
                            f'start_hub no tiene formato válido (ej: start_hub: start 0 0 [color=green]), linea {line_docu}')

            elif line.startswith('hub: '):
                try:
                    required['hub'] = True
                    line_clean = line.split(': ', 1)[1].rstrip('\n')
                    parts = line_clean.split(' ', 3)
                    # print(parts)
                    name, x, y, errs, blocked_zones = validate_hubs(
                        parts, line_docu, 'hub', blocked_zones)
                    if errs:
                        errores.extend(errs)
                    if name in zones_names:
                        errores.append(
                            f"Nombre de zona repetido: {name}, linea {line_docu}")
                    else:
                        zones_names.append(name)
                    if (x, y) in posiciones_xy:
                        errores.append(
                            f"Posición repetida: ({x},{y}), linea {line_docu}")
                    else:
                        posiciones_xy.append((x, y))

                    # required['hub'] = True
                    # print(f"Hub válido, linea {line_docu}", parts)

                except:
                    errores.append(
                        f'hub no tiene formato válido (ej: hub: start 0 0 [color=green]), linea {line_docu}')

            elif line.startswith('end_hub: '):
                if required['end_hub']:
                    errores.append(
                        f'end_hub aparece más de una vez, linea {line_docu}')

                else:
                    try:
                        line_clean = line.split(': ', 1)[1].rstrip('\n')
                        parts = line_clean.split(' ', 3)
                        # print(parts)
                        name, x, y, errs, blocked_zones = validate_hubs(
                            parts, line_docu, 'end_hub', blocked_zones)
                        if errs:
                            errores.extend(errs)
                        if name in zones_names:
                            errores.append(
                                f"Nombre de zona repetido: {name}, linea {line_docu}")
                        else:
                            zones_names.append(name)
                            end_hub = name
                        if (x, y) in posiciones_xy:
                            errores.append(
                                f"Posición repetida: ({x},{y}), linea {line_docu}")
                        else:
                            posiciones_xy.append((x, y))

                        required['end_hub'] = True
                        # print(f"End hub válido, linea {line_docu}", parts)

                    except:
                        errores.append(
                            f'end_hub no tiene formato válido (ej: end_hub: start 0 0 [color=green]), linea {line_docu}')

            elif line.startswith('connection: '):
                try:
                    required['connection'] = True
                    line_clean = line.split(': ', 1)[1].rstrip('\n')
                    parts = line_clean.split(' ', 1)
                    zone_pair = parts[0]

                    if '-' not in zone_pair:
                        errores.append(
                            "Formato de conexión inválido, debe ser: nombre1-nombre2")
                    else:
                        name1, name2 = zone_pair.split('-', 1)
                    if name1 not in zones_names or name2 not in zones_names:
                        errores.append(
                            f"Conexión inválida: uno o ambos nombres no existen ({name1}-{name2})")
                    elif (name1, name2) in conexion or (name2, name1) in conexion:
                        errores.append(
                            f"Conexión inválida: No se peden repetir conexiones igualles ({name1}-{name2})")
                    else:
                        conexion.append((name1, name2))
                        conexion.append((name2, name1))

                    if len(parts) == 2:
                        meta_str = parts[1]
                        if not (meta_str.startswith('[') and meta_str.endswith(']')):
                            errores.append(
                                f"Metadata debe ir entre corchetes [], linea {line_docu}")
                        else:
                            meta_content = meta_str[1:-1]
                            if '=' not in meta_content:
                                errores.append(
                                    f"Metadata inválida: {meta_content}, no contiene '=', linea {line_docu}")
                            else:
                                if meta_content:
                                    meta_content = meta_content.split()
                                    for item in meta_content:
                                        if '=' not in item:
                                            errores.append(
                                                f"Metadata inválida: {item}, no contiene '=', linea {line_docu}")
                                        else:
                                            key, val = item.split('=', 1)
                                            if key == 'max_link_capacity':
                                                try:
                                                    int(val)  # Debe ser entero
                                                except:
                                                    errores.append(
                                                        f"max_link_capacity debe ser número entero: {val}, linea {line_docu}")
                                            else:
                                                errores.append(
                                                    f"Clave no permitida en metadatos: {key}, linea {line_docu}")

                    elif len(parts) > 2:
                        errores.append(
                            f'Hay mcuhos datos en esa linea {line_docu}')

                except Exception as e:
                    errores.append(
                        f'Error al procesar conexión, linea {line_docu}: {str(e)}')

            else:
                errores.append(f'Línea no válida: {line_docu}')

    if not all(required.values()):
        errores.append('Faltan lineas con claves obligatorias')
        for key, value in required.items():
            if not value:
                errores.append(f'--> Clave no declarada: {key}')

    if sin_salida(conexion, start_hub, end_hub, blocked_zones):
        errores.append(
            'Mapa sin salida: no se puede llegar desde start_hub hasta end_hub')
    else:
        print('El mapa tiene camino a la Salida, preparando drones, hubs y conexiones...')

    if errores:
        print('Errores:')
        for error in errores:
            print(f'  - {error}')
        sys.exit(1)
