from typing import Any
import sys


def validate_hubs(list_parts: list, line_num: int, zone_type: str,
                  blocked_list: set) -> tuple:
    """
    Validate hub/token data parsed from a config line.

    Checks name, integer coordinates and optional metadata. Returns a tuple
    (name, x, y, errors, blocked_list) where errors is a list of human readable
    error messages and blocked_list is updated if the zone is marked blocked.
    """
    errors = []
    name = None
    x = None
    y = None
    metadata = None
    zone_types = ['normal', 'blocked', 'restricted', 'priority']
    colors = [
        'green', 'yellow', 'red', 'blue', 'gray', 'darked', 'gold', 'black',
        'marron', 'orange', 'brown', 'purple', 'maroon', 'darkred', 'violet',
        'crimson', 'rainbow', 'cyan', 'lime', 'magenta'
    ]

    if len(list_parts) < 3:
        errors.append(f"Missing data for {zone_type}, line {line_num}")
        return name, x, y, errors, blocked_list

    name = list_parts[0]
    if not isinstance(name, str):
        errors.append(f"Name must be text, line {line_num}")
    else:
        if '-' in name:
            errors.append(
                f"Zone name must not contain hyphen '-': {name}, line "
                f"{line_num}")

    try:
        x = int(list_parts[1])
        y = int(list_parts[2])
    except Exception:
        errors.append(f"Coordinates must be integers, line {line_num}")

    # print(len(list_parts))
    if len(list_parts) == 4:
        metadata = list_parts[3]
        if not (metadata.startswith('[') and metadata.endswith(']')):
            errors.append(
                f"Metadata must be enclosed in [] brackets, line {line_num}")
        else:
            metadata = metadata[1:-1]
            metadata = metadata.split()
            # print(metadata)
            for data in metadata:
                if '=' not in data:
                    errors.append(
                        f"Invalid metadata: {data}, missing '=' line "
                        f"{line_num}")
                    continue

                key, val = data.split('=', 1)

                if key == 'color':
                    if val not in colors:
                        errors.append(
                            f"Color not allowed: {val}, line {line_num}")

                elif key == 'max_drones':
                    try:
                        int(val)
                    except Exception:
                        errors.append(
                            f"max_drones must be an integer: {val}, "
                            f"line {line_num}")

                elif key == 'max_link_capacity':
                    try:
                        int(val)
                    except Exception:
                        errors.append(
                            f"max_link_capacity must be an integer: {val}, "
                            f"line {line_num}")

                elif key == 'zone':
                    if val not in zone_types:
                        errors.append(
                            f"Invalid zone type: {val}, line {line_num}")
                    elif val == 'blocked':
                        blocked_list.add(name)
                else:
                    errors.append(
                        f'Check metadata, invalid metadata item {data} '
                        f'on line {line_num}')

    return name, x, y, errors, blocked_list


def validate_args(args: Any) -> bool:

    errors = []

    if len(args) > 1:
        errors.append(
            'More than one argument provided; run: make run <file.txt>')

    if len(args) < 1:
        errors.append(
            'Missing configuration file; run: make run <file.txt>')

    if len(args) and not args[0].endswith('.txt'):
        errors.append(
            'Ensure the provided file has a .txt extension')

    if errors:
        print('Errors:')
        for error in errors:
            print(f'    - {error}')
        return False

    args = args[0]

    try:
        with open(args):
            pass
    except FileNotFoundError:
        errors.append(
            f"File '{args}' does not exist")

    except PermissionError:
        errors.append(
            f"No permission to read '{args}'")

    except Exception:
        errors.append(
            "Unknown error opening file; run: make run <file.txt>")

    if errors:
        print('Errors:')
        for error in errors:
            print(f'    - {error}')
        return False

    return True


def sin_salida(connections: list, start: str, end: str,
               blocked_list: set) -> bool:
    """
    Check whether there is a path from start to end avoiding blocked zones.

    Returns True if there is NO path (i.e. map has no exit), False if a path
    exists.
    """
    if start in blocked_list or end in blocked_list:
        return True
    grafo = {}
    for a, b in connections:
        if a not in grafo:
            grafo[a] = []
        if b not in grafo:
            grafo[b] = []
        grafo[a].append(b)
        grafo[b].append(a)

    to_visit = [start]
    visited = set()

    while to_visit:
        node = to_visit.pop(0)

        if node in visited or node in blocked_list:
            continue

        visited.add(node)

        if node == end:
            return False

        for neighbor in grafo.get(node, []):
            if (neighbor not in visited and
                    neighbor not in blocked_list):
                to_visit.append(neighbor)
    return True


def open_document(args: str) -> None:
    """
    Parse and validate the entire configuration document.

    This function collects errors and exits the program with a summary if the
    file has invalid lines or missing required keys.
    """
    errors = []
    required = {'nb_drones': False, 'start_hub': False,
                'hub': False, 'end_hub': False, 'connection': False}
    line_num = 0
    zones_names = []
    positions_xy = []
    connections = []
    start_hub = str()
    end_hub = str()
    blocked_zones = set()

    with open(args) as file:
        for line in file:
            line_num += 1

            if line.startswith('#') or line[0] == '\n':
                continue

            elif line.startswith('nb_drones: '):
                if required['nb_drones']:
                    errors.append(
                        f'nb_drones appears more than once, line {line_num}')

                try:
                    int(line.split(': ', 1)[1])
                    required['nb_drones'] = True
                except Exception:
                    errors.append('Check format: nb_drones: 5')

            elif line.startswith('start_hub: '):
                if required['start_hub']:
                    errors.append(
                        f'start_hub appears more than once, line {line_num}')

                else:
                    try:
                        line_clean = line.split(': ', 1)[1].rstrip('\n')
                        parts = line_clean.split(' ', 3)
                        name, x, y, errs, blocked_zones = validate_hubs(
                            parts, line_num, 'start_hub', blocked_zones)
                        if errs:
                            errors.extend(errs)
                        if name in zones_names:
                            errors.append(
                                f"Duplicate zone name: {name}, line "
                                f"{line_num}")
                        else:
                            zones_names.append(name)
                            start_hub = name

                        if (x, y) in positions_xy:
                            errors.append(
                                f"Duplicate position: ({x},{y}), line "
                                f"{line_num}")
                        else:
                            positions_xy.append((x, y))

                        required['start_hub'] = True

                    except Exception:
                        errors.append(
                            f'start_hub has invalid format '
                            f'(e.g. start_hub: start 0 0 [color=green]), '
                            f'line {line_num}')

            elif line.startswith('hub: '):
                try:
                    required['hub'] = True
                    line_clean = line.split(': ', 1)[1].rstrip('\n')
                    parts = line_clean.split(' ', 3)
                    name, x, y, errs, blocked_zones = validate_hubs(
                        parts, line_num, 'hub', blocked_zones)
                    if errs:
                        errors.extend(errs)
                    if name in zones_names:
                        errors.append(
                            f"Duplicate zone name: {name}, line {line_num}")
                    else:
                        zones_names.append(name)
                    if (x, y) in positions_xy:
                        errors.append(
                            f"Duplicate position: ({x},{y}), line {line_num}")
                    else:
                        positions_xy.append((x, y))

                except Exception:
                    errors.append(
                        f'hub has invalid format '
                        f'(e.g. hub: start 0 0 [color=green]), line '
                        f'{line_num}')

            elif line.startswith('end_hub: '):
                if required['end_hub']:
                    errors.append(
                        f'end_hub appears more than once, line {line_num}')

                else:
                    try:
                        line_clean = line.split(': ', 1)[1].rstrip('\n')
                        parts = line_clean.split(' ', 3)

                        name, x, y, errs, blocked_zones = validate_hubs(
                            parts, line_num, 'end_hub', blocked_zones)
                        if errs:
                            errors.extend(errs)
                        if name in zones_names:
                            errors.append(
                                f"Duplicate zone name: {name}, line "
                                f"{line_num}")
                        else:
                            zones_names.append(name)
                            end_hub = name
                        if (x, y) in positions_xy:
                            errors.append(
                                f"Duplicate position: ({x},{y}), line "
                                f"{line_num}")
                        else:
                            positions_xy.append((x, y))

                        required['end_hub'] = True

                    except Exception:
                        errors.append(
                            f'end_hub has invalid format '
                            f'(e.g. end_hub: start 0 0 [color=green]), '
                            f'line {line_num}')

            elif line.startswith('connection: '):
                try:
                    required['connection'] = True
                    line_clean = line.split(': ', 1)[1].rstrip('\n')
                    parts = line_clean.split(' ', 1)
                    zone_pair = parts[0]

                    if '-' not in zone_pair:
                        errors.append(
                            "Invalid connection format, expected: name1-name2")
                    else:
                        name1, name2 = zone_pair.split('-', 1)
                        if (name1 not in zones_names or
                                name2 not in zones_names):
                            errors.append(
                                f"Invalid connection: one or both names "
                                f"do not exist ({name1}-{name2})")
                        elif ((name1, name2) in connections or
                              (name2, name1) in connections):
                            errors.append(
                                f"Invalid connection: duplicate connection "
                                f"({name1}-{name2})")
                        else:
                            connections.append((name1, name2))
                            connections.append((name2, name1))

                    if len(parts) == 2:
                        meta_str = parts[1]
                        if not (meta_str.startswith('[') and
                                meta_str.endswith(']')):
                            errors.append(
                                f"Metadata must be enclosed in [] brackets, "
                                f"line {line_num}")
                        else:
                            meta_content = meta_str[1:-1]
                            if '=' not in meta_content:
                                errors.append(
                                    f"Invalid metadata: {meta_content}, "
                                    f"missing '=', line {line_num}")
                            else:
                                if meta_content:
                                    meta_content = meta_content.split()
                                    for item in meta_content:
                                        if '=' not in item:
                                            errors.append(
                                                f"Invalid metadata: {item}, "
                                                f"missing '=', line "
                                                f"{line_num}")
                                        else:
                                            key, val = item.split('=', 1)
                                            if key == 'max_link_capacity':
                                                try:
                                                    int(val)
                                                except Exception:
                                                    errors.append(
                                                        f"max_link_capacity "
                                                        f"must be integer: "
                                                        f"{val}, "
                                                        f"line {line_num}")
                                            else:
                                                errors.append(
                                                    f"Metadata key not "
                                                    f"allowed: {key}, "
                                                    f"line {line_num}")

                    elif len(parts) > 2:
                        errors.append(
                            f'Too many items on line {line_num}')

                except Exception as e:
                    errors.append(
                        f'Error processing connection, line {line_num}: '
                        f'{str(e)}')

            else:
                errors.append(f'Invalid line: {line_num}')

    if not all(required.values()):
        errors.append('Missing required keys in file')
        for key, value in required.items():
            if not value:
                errors.append(f'--> Missing key: {key}')

    if sin_salida(connections, start_hub, end_hub, blocked_zones):
        errors.append(
            'Map has no exit: cannot reach end_hub from start_hub')
    else:
        print('Map validated: preparing drones, hubs and connections...')

    if errors:
        print('Errors:')
        for error in errors:
            print(f'  - {error}')
        sys.exit(1)
