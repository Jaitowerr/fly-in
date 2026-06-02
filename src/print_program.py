import time
from random import choice as rmc
from typing import List, Any, Sequence, Dict
from src.algorithm.prioritized_planner import _is_connection, _is_hub
import os


_ANSI: dict[str, str] = {
    "green": "\033[32m", "yellow": "\033[33m", "red": "\033[31m",
    "blue": "\033[34m", "cyan": "\033[36m", "magenta": "\033[35m",
    "white": "\033[37m", "purple": "\033[35;1m", "orange": "\033[38;5;208m",
    "brown": "\033[38;5;130m", "maroon": "\033[38;5;88m", "black": "\033[90m",
    "gold": "\033[33;1m", "violet":  "\033[35;1m", "crimson": "\033[31;1m",
    "darkred": "\033[31m", "rainbow": "\033[36;1m", "lime": "\033[38;5;118m",
    "gray": "\033[38;5;244m", "marron": "\033[38;5;88m",
    "darked": "\033[38;5;52m",
}

_RESET = "\033[0m"
_GREEN = "\033[32m"
_CYAN = "\033[36m"
_BOLD = "\033[1m"
_RED = "\033[31m"

_DESIGNS: List[str] = [
    ' ~╚¥╝~ ',
    ' ╠═▄▄═╣ ',
    ' ╠═¤¤═╣ ',
    ' ╠¤¤╣ ',
    ' ╠-¥-╣ ',
    ' ╠--▄▄--╣ '
]
_design_cache: Dict[int, str] = {}


def print_launch_drones(list_drones: Sequence[Any]) -> None:
    """
    Show a decorative launch banner for the given drones.

    This is purely visual: it prints colored ASCII designs representing the
    fleet about to start.

    Args:
        list_drones (Sequence): Collection of drone objects.
    """

    print(f"\n Launching...      {len(list_drones)} drones\n")
    for _ in range(len(list_drones)):
        selected_color = rmc(list(_ANSI.values()))
        selected_design = selected_color + rmc(_DESIGNS)
        print(selected_design, end=' ')

    print('\033[1;32m\n')


def print_by_turns(list_drones: List[Any]) -> None:
    """
    Print the simulation turn-by-turn in text mode using ANSI colors.

    The function iterates over planned turns and prints where each drone is
    (hub name or connection). It sleeps briefly between turns.

    Args:
        list_drones (List[Any]): List of drone objects with a route_positions
        attribute.
    """

    drones_ordenados = sorted(list_drones, key=lambda d: d.drone_id)

    max_turnos = max(
        (len(d.route_positions) for d in drones_ordenados if
         d.route_positions),
        default=0,
    )

    print(f"\n{_CYAN}{'═' * 52}{_RESET}")
    print(f"{_CYAN}{_BOLD}  SIMULATION — {len(list_drones)} drones — "
          f"{max_turnos} turns{_RESET}")
    print(f"{_CYAN}{'═' * 52}{_RESET}\n")

    start_hub = list_drones[0].hub  # all start at the same hub
    drones_str = "  ".join(f"D{d.drone_id}" for d in drones_ordenados)
    print(f"{_CYAN}Start ({start_hub.hub_name}):{_RESET}  {drones_str}\n")

    for t in range(max_turnos):
        movs = []

        for dron in drones_ordenados:
            if not dron.route_positions or t >= len(dron.route_positions):
                continue

            turno = dron.route_positions[t]
            if turno is None:
                continue

            _paso1, paso2 = turno

            dest_str = ""
            for obj in paso2:

                if _is_hub(obj):
                    color_code = _ANSI.get(obj.color or "", "\033[37m")
                    dest_str = f"{color_code}{_BOLD}{obj.hub_name}{_RESET}"
                    break

                if _is_connection(obj):
                    nombre = f"{obj.origin.hub_name}-{obj.destiny.hub_name}"
                    dest_str = f"\033[33m\033[3m{nombre}{_RESET}"
                    break

            if dest_str:
                movs.append(f"\033[37;1mD{dron.drone_id}{_RESET}-{dest_str}")

        if movs:
            print(f"{_CYAN}Turn {t + 1:>3}:{_RESET}  {'    '.join(movs)}")
            time.sleep(0.5)

    print(f"\n{_CYAN}{'═' * 52}{_RESET}")
    print(f"{_GREEN}{_BOLD}  Completed in {max_turnos} turns.{_RESET}")
    print(f"{_CYAN}{'═' * 52}{_RESET}\n")


def _design(drone_id: int) -> str:
    """Return a cached small ASCII design for a given drone id."""
    if drone_id not in _design_cache:
        _design_cache[drone_id] = rmc(_DESIGNS)
    return _design_cache[drone_id]


def print_with_animation(list_drones: List[Any], list_hubs: List[Any]) -> None:
    """Mapa animado turno a turno. Cada dron se mueve en su eje x,y."""

    drones = sorted(list_drones, key=lambda d: d.drone_id)
    max_turnos = max((len(d.route_positions) for d in drones if
                      d.route_positions), default=0)

    xs = [float(h.x) for h in list_hubs]
    ys = [float(h.y) for h in list_hubs]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    size = os.get_terminal_size()
    WIDTH = size.columns - 2
    HIGH = size.lines - 6

    def a_col(x: float) -> int:
        return int((x - x_min) / (x_max - x_min) * (WIDTH - 8)) + 4

    def a_fila(y: float) -> int:
        # y invertida: mayor y = más arriba
        rango_y = y_max - y_min if y_max != y_min else 1
        return int((y_max - y) / rango_y * (HIGH - 4)) + 2

    pos: dict[int, tuple[float, float]] = {}
    for dron in drones:
        hub = next((h for h in list_hubs if
                    h.hub_name == dron.current_position), None)
        if hub:
            pos[dron.drone_id] = (float(hub.x), float(hub.y))

    def paint(turno_num: int) -> None:
        grid = [[' '] * WIDTH for _ in range(HIGH)]

        def write(f: int, c: int, txt: str) -> None:
            for i, ch in enumerate(txt):
                if 0 <= f < HIGH and 0 <= c + i < WIDTH:
                    grid[f][c + i] = ch

        for hub in list_hubs:
            c = a_col(float(hub.x))
            f = a_fila(float(hub.y))
            sym = '◉' if hub.start else ('✦' if hub.end else '·')
            write(f, c, sym)
            write(f - 1, c - 1, hub.hub_name[:3])

        for dron in drones:
            if dron.drone_id not in pos:
                continue
            px, py = pos[dron.drone_id]
            c = a_col(px)
            f = a_fila(py)
            write(f, c - 1, _design(dron.drone_id))
            write(f - 1, c, f'D{dron.drone_id}')

        os.system('clear')
        print(f"{_CYAN}{_BOLD} Turno {turno_num}/{max_turnos}{_RESET}")
        for fila in grid:
            print(''.join(fila))

    paint(0)
    time.sleep(0.6)

    for t in range(max_turnos):
        # Recoger destinations de este turno
        destinations: dict[int, tuple[float, float]] = {}
        for dron in drones:
            if not dron.route_positions or t >= len(dron.route_positions):
                continue
            turno = dron.route_positions[t]
            if turno is None:
                continue
            _, paso2 = turno
            obj = next((o for o in paso2 if _is_hub(o) or _is_connection(o)),
                       None)
            if obj is None:
                continue
            if _is_hub(obj):
                destinations[dron.drone_id] = (float(obj.x), float(obj.y))
            elif _is_connection(obj):
                destinations[dron.drone_id] = (
                    (float(obj.origin.x) + float(obj.destiny.x)) / 2,
                    (float(obj.origin.y) + float(obj.destiny.y)) / 2,
                )

        N = 5
        for frame in range(N + 1):
            alpha = frame / N
            for id_dron, dest in destinations.items():
                ox, oy = pos[id_dron]
                pos[id_dron] = (
                    ox + (dest[0] - ox) * alpha,
                    oy + (dest[1] - oy) * alpha,
                )
            paint(t + 1)
            time.sleep(0.08)

        for id_dron, dest in destinations.items():
            pos[id_dron] = dest

        time.sleep(0.3)

    paint(max_turnos)
    print(f"\n{_CYAN}{'═' * 40}{_RESET}")
    print(f"\033[32m{_BOLD}  Completed in {max_turnos} turns.{_RESET}")
    print(f"{_CYAN}{'═' * 40}{_RESET}\n")
