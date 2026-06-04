from typing import Any
import sys


class Parse:
    def __init__(self, list_argument: list[Any]) -> None:
        self.list_argument: list[Any] = list_argument or []
        self.argument = ""

    def validate_hubs(
        self,
        list_parts: list[str],
        line_num: int,
        zone_type: str,
        blocked_list: set[str],
    ) -> tuple[None | str, None | int, None | int, list[str], set[str]]:
        """
        Validate hub/token data parsed from a config line.

        Checks name, integer coordinates and optional metadata. Returns a tuple
        (name, x, y, errors, blocked_list) where errors is a list of human
        readable error messages and blocked_list is updated if the zone is
        marked blocked.
        """
        errors = []
        name = None
        x = None
        y = None
        metadata = None
        colors = [
            'green', 'yellow', 'red', 'blue', 'gray', 'darked', 'gold',
            'black', 'marron', 'orange', 'brown', 'purple', 'maroon',
            'darkred', 'violet', 'crimson', 'rainbow', 'cyan', 'lime',
            'magenta']

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

        if len(list_parts) == 4:
            metadata = list_parts[3]
            if not (metadata.startswith('[') and metadata.endswith(']')):
                errors.append(
                    f"Metadata must be enclosed in [] brackets, "
                    f"line {line_num}"
                )
            else:
                metadata_body = metadata[1:-1].strip()
                if metadata_body:
                    metadata_items = metadata_body.split()
                    for data in metadata_items:

                        if '=' in data:
                            key, val = data.split('=', 1)
                        else:
                            key, val = data, None

                        if key == 'color':
                            if val is None or val not in colors:
                                errors.append(f"Color not allowed: {val},"
                                              f" line {line_num}")
                        elif key == 'max_drones':
                            if val is None:
                                errors.append(f"max_drones missing value, "
                                              f"line {line_num}")
                            else:
                                try:
                                    int(val)
                                except Exception:
                                    errors.append(f"max_drones must be an "
                                                  f"integer: {val}, "
                                                  f"line {line_num}")
                        elif key == 'max_link_capacity':
                            if val is None:
                                errors.append(f"max_link_capacity missing "
                                              f"value, line {line_num}")
                            else:
                                try:
                                    int(val)
                                except Exception:
                                    errors.append(
                                        f"max_link_capacity must be an "
                                        f"integer: {val}, line {line_num}"
                                    )
                        elif key == 'blocked':
                            # blocked as flag (either "blocked" or "blocked=1")
                            blocked_list.add(name)
                        elif key == 'zone':
                            allowed = {'restricted', 'priority', 'normal',
                                       'blocked'}
                            if val is None or val not in allowed:
                                errors.append(
                                    f"Invalid zone value: {val}, allowed: "
                                    f"{sorted(allowed)}, line {line_num}"
                                )
                            if val == 'blocked':
                                blocked_list.add(name)
                        else:
                            errors.append(f'Check metadata, invalid metadata '
                                          f'item {data} on line {line_num}')

        return name, x, y, errors, blocked_list

    def validate_args(self) -> bool:
        self.capacity_info = False
        errors = []
        if "--capacity-info" in self.list_argument:
            self.capacity_info = True
            self.list_argument.remove("--capacity-info")
        if len(self.list_argument) > 1:
            errors.append(
                'More than one argument provided; run: make run <file.txt>')

        if len(self.list_argument) < 1:
            errors.append(
                'Missing configuration file; run: make run <file.txt>')

        if len(self.list_argument) and not self.list_argument[0].endswith(
                '.txt'):
            errors.append(
                'Ensure the provided file has a .txt extension')

        if errors:
            print('Errors:')
            for error in errors:
                print(f'    - {error}')
            return False

        argument = self.list_argument[0]

        try:
            with open(argument):
                pass
        except FileNotFoundError:
            errors.append(
                f"File '{argument}' does not exist")

        except PermissionError:
            errors.append(
                f"No permission to read '{argument}'")

        except Exception:
            errors.append(
                "Unknown error opening file; run: make run <file.txt>")

        if errors:
            print('Errors:')
            for error in errors:
                print(f'    - {error}')
            return False
        self.argument = argument
        return True

    def not_exit(
        self,
        connections: list[tuple[str, str]],
        start: str,
        end: str,
        blocked_list: set[str],
    ) -> bool:
        """
        Check whether there is a path from start to end avoiding blocked
        zones.

        Returns True if there is NO path (i.e. map has no exit),
        False if a path exists.
        """
        if start in blocked_list or end in blocked_list:
            return True
        grafo: dict[str, list[str]] = {}
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

    def open_document(self) -> None:
        """
        Parse and validate the entire configuration document.

        This function collects errors and exits the program with a summary if
        the file has invalid lines or missing required keys.
        """
        errors = []
        required = {'nb_drones': False, 'start_hub': False,
                    'hub': False, 'end_hub': False, 'connection': False}
        line_num = 0
        zones_names: list[str] = []
        positions_xy: list[tuple[int, int]] = []
        connections: list[tuple[str, str]] = []
        start_hub: str = ''
        end_hub: str = ''
        blocked_zones: set[str] = set()

        with open(self.argument) as file:
            for line in file:
                line_num += 1

                if line.startswith('#') or line[0] == '\n':
                    continue

                elif line.startswith('nb_drones: '):
                    if required['nb_drones']:
                        errors.append(
                            f'nb_drones appears more than once, '
                            f'line {line_num}'
                        )

                    try:
                        int(line.split(': ', 1)[1])
                        required['nb_drones'] = True
                    except Exception:
                        errors.append('Check format: nb_drones: 5')

                elif line.startswith('start_hub: '):
                    if required['start_hub']:
                        errors.append(
                            f'start_hub appears more than once, '
                            f'line {line_num}'
                        )
                    else:
                        try:
                            line_clean = line.split(': ', 1)[1].rstrip('\n')
                            parts = line_clean.split(' ', 3)
                            name, x, y, errs, blocked_zones = (
                                self.validate_hubs(
                                    parts, line_num, 'start_hub',
                                    blocked_zones
                                )
                            )
                            if errs:
                                errors.extend(errs)
                            if name is not None:
                                if name in zones_names:
                                    errors.append(
                                        f"Duplicate zone name: {name}, line "
                                        f"{line_num}")
                                else:
                                    zones_names.append(name)
                                    start_hub = name

                            if x is not None and y is not None:
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
                        name, x, y, errs, blocked_zones = self.validate_hubs(
                            parts, line_num, 'hub', blocked_zones)
                        if errs:
                            errors.extend(errs)
                        if name is not None:
                            if name in zones_names:
                                errors.append(
                                    f"Duplicate zone name: {name}, "
                                    f"line {line_num}"
                                )
                            else:
                                zones_names.append(name)
                        if x is not None and y is not None:
                            if (x, y) in positions_xy:
                                errors.append(
                                    f"Duplicate position: ({x},{y}), "
                                    f"line {line_num}"
                                )
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

                            name, x, y, errs, blocked_zones = (
                                self.validate_hubs(
                                    parts, line_num, 'end_hub',
                                    blocked_zones
                                )
                            )
                            if errs:
                                errors.extend(errs)
                            if name is not None:
                                if name in zones_names:
                                    errors.append(
                                        f"Duplicate zone name: {name}, line "
                                        f"{line_num}")
                                else:
                                    zones_names.append(name)
                                    end_hub = name
                            if x is not None and y is not None:
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
                                "Invalid connection format, expected: "
                                "name1-name2"
                            )
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
                                    "Invalid connection: duplicate "
                                    f"connection ({name1}-{name2})"
                                )
                            else:
                                connections.append((name1, name2))
                                connections.append((name2, name1))

                        if len(parts) == 2:
                            meta_str = parts[1]
                            if not (meta_str.startswith('[')
                                    and meta_str.endswith(']')):
                                errors.append(
                                    "Metadata must be enclosed in [] "
                                    "brackets, "
                                    f"line {line_num}"
                                )
                            else:
                                meta_content = meta_str[1:-1]
                                if '=' not in meta_content:
                                    errors.append(
                                        "Invalid metadata: "
                                        f"{meta_content}, missing '=', "
                                        f"line {line_num}"
                                    )
                                else:
                                    if meta_content:
                                        meta_items = meta_content.split()
                                        for item in meta_items:
                                            if '=' not in item:
                                                errors.append(
                                                    "Invalid metadata: "
                                                    f"{item}, missing '=', "
                                                    f"line {line_num}"
                                                )
                                            else:
                                                key, val = item.split('=', 1)
                                                if key == 'max_link_capacity':
                                                    try:
                                                        int(val)
                                                    except Exception:
                                                        errors.append(
                                                            "max_link_capacity"
                                                            " must be "
                                                            "integer: "
                                                            f"{val}, "
                                                            f"line {line_num}"
                                                        )
                                                else:
                                                    errors.append(
                                                        "Metadata key not "
                                                        f"allowed: {key}, "
                                                        f"line {line_num}"
                                                    )

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

        if self.not_exit(connections, start_hub, end_hub, blocked_zones):
            errors.append(
                'Map has no exit: cannot reach end_hub from start_hub')
        else:
            print('Map validated: preparing drones, hubs and connections...')

        if errors:
            print('Errors:')
            for error in errors:
                print(f'  - {error}')
            sys.exit(1)
