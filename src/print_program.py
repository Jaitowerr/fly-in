import time
from random import choice as rmc
from typing import List, Any
from src.algorithm.prioritized_planner import _is_connection, _is_hub
import os


# _ANSI: dict[str, str] = {
#     "green":   "\033[32m",
#     "yellow":  "\033[33m",
#     "red":     "\033[31m",
#     "blue":    "\033[34m",
#     "cyan":    "\033[36m",
#     "magenta": "\033[35m",
#     "white":   "\033[37m",
#     "purple":  "\033[35;1m",
#     "orange":  "\033[38;5;208m",
#     "brown":   "\033[38;5;130m",
#     "maroon":  "\033[38;5;88m",
#     "black":   "\033[90m",
#     "pink":    "\033[38;5;205m",
#     "grey":    "\033[90m",
# }


_ANSI: dict[str, str] = {
    "green":   "\033[32m",   "yellow":  "\033[33m",  "red":     "\033[31m",
    "blue":    "\033[34m",   "cyan":    "\033[36m",   "magenta": "\033[35m",
    "white":   "\033[37m",   "purple":  "\033[35;1m", "orange":  "\033[38;5;208m",
    "brown":   "\033[38;5;130m", "maroon": "\033[38;5;88m", "black": "\033[90m",
    "gold":    "\033[33;1m", "violet":  "\033[35;1m", "crimson": "\033[31;1m",
    "darkred": "\033[31m",   "rainbow": "\033[36;1m",
}

_RESET = "\033[0m"
_GREEN = "\033[32m"
_CYAN  = "\033[36m"
_BOLD  = "\033[1m"
 

def imprimir_drones_arranque(list_drones) -> None:
    drones_designs = [
        ' ~╚¥╝~  ',  '  ╠═▄▄═╣  ', '  ╠═¤¤═╣  ', '  ╠¤¤╣  ', '  ╠-¥-╣  ', '  ╠--▄▄--╣  ']
    colores = {
        "amarillo": "\033[1;33m", "azul": "\033[1;34m", "rojo": "\033[1;31m",
        "magenta": "\033[1;35m", "cyan": "\033[1;36m", "blanco": "\033[1;37m"}
# "reset": "\033[0m"

    print(f'\n Despegando...      {len(list_drones)} drones\n')
    for _ in range(len(list_drones)):
        selected_color = rmc(list(colores.values()))
        selected_design = selected_color + rmc(drones_designs)
        print(selected_design, end=' ')
    
    print('\033[1;32m\n')



def imprimir_por_turnos(list_drones: List[Any]) -> None:
    """Imprime la simulación turno a turno con colores ANSI y un sleep de 0.5s por turno.
 
    Formato subject §VII.5:
        D<ID>-<zone>        cuando el dron llega a un hub
        D<ID>-<connection>  cuando el dron está en vuelo hacia restricted
    """
 
    drones_ordenados = sorted(list_drones, key=lambda d: d.id_dron)
 
    max_turnos = max(
        (len(d.ruta_posiciones) for d in drones_ordenados if d.ruta_posiciones),
        default=0,
    )
 
    print(f"\n{_CYAN}{'═' * 52}{_RESET}")
    print(f"{_CYAN}{_BOLD}  SIMULACIÓN — {len(list_drones)} drones — {max_turnos} turnos{_RESET}")
    print(f"{_CYAN}{'═' * 52}{_RESET}\n")

    start_hub = list_drones[0].hub  # todos empiezan en el mismo
    drones_str = "  ".join(f"D{d.id_dron}" for d in drones_ordenados)
    print(f"{_CYAN}Start ({start_hub.hub_name}):{_RESET}  {drones_str}\n")

    for t in range(max_turnos):
        movs = []
 
        for dron in drones_ordenados:
            if not dron.ruta_posiciones or t >= len(dron.ruta_posiciones):
                continue
 
            turno = dron.ruta_posiciones[t]
            if turno is None:
                continue  # dron esperando, no aparece
 
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
                movs.append(f"\033[37;1mD{dron.id_dron}{_RESET}-{dest_str}")
 
        if movs:
            print(f"{_CYAN}Turno {t + 1:>3}:{_RESET}  {'    '.join(movs)}")
            time.sleep(0.5)
 
    print(f"\n{_CYAN}{'═' * 52}{_RESET}")
    print(f"{_GREEN}{_BOLD}  Completado en {max_turnos} turnos.{_RESET}")
    print(f"{_CYAN}{'═' * 52}{_RESET}\n")







_DESIGNS = [' ~╚¥╝~ ', ' ╠═▄▄═╣ ', ' ╠═¤¤═╣ ', ' ╠¤¤╣ ', ' ╠-¥-╣ ', ' ╠--▄▄--╣ ']
_design_cache: dict[int, str] = {}

def _design(id_dron: int) -> str:
    if id_dron not in _design_cache:
        _design_cache[id_dron] = rmc(_DESIGNS)
    return _design_cache[id_dron]


def imprimir_con_animacion(list_drones: List[Any], list_hubs: List[Any]) -> None:
    """Mapa animado turno a turno. Cada dron se mueve en su eje x,y."""

    drones = sorted(list_drones, key=lambda d: d.id_dron)
    max_turnos = max((len(d.ruta_posiciones) for d in drones if d.ruta_posiciones), default=0)

    # Calcular escala del mapa
    xs = [float(h.x) for h in list_hubs]
    ys = [float(h.y) for h in list_hubs]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    size  = os.get_terminal_size()
    ANCHO = size.columns - 2
    ALTO  = size.lines - 6

    def a_col(x: float) -> int:
        return int((x - x_min) / (x_max - x_min) * (ANCHO - 8)) + 4

    def a_fila(y: float) -> int:
        # y invertida: mayor y = más arriba
        return int((y_max - y) / (y_max - y_min) * (ALTO - 4)) + 2

    # Posición actual de cada dron en coordenadas del mapa (float para interpolar)
    pos: dict[int, tuple[float, float]] = {}
    for dron in drones:
        hub = next((h for h in list_hubs if h.hub_name == dron.posicion_actual), None)
        if hub:
            pos[dron.id_dron] = (float(hub.x), float(hub.y))

    def pintar(turno_num: int) -> None:
        # Grid vacío
        grid = [[' '] * ANCHO for _ in range(ALTO)]

        def write(f: int, c: int, txt: str) -> None:
            for i, ch in enumerate(txt):
                if 0 <= f < ALTO and 0 <= c + i < ANCHO:
                    grid[f][c + i] = ch

        # Hubs: símbolo + nombre corto encima
        for hub in list_hubs:
            c = a_col(float(hub.x))
            f = a_fila(float(hub.y))
            sym = '◉' if hub.start else ('✦' if hub.end else '·')
            write(f, c, sym)
            write(f - 1, c - 1, hub.hub_name[:3])

        # Drones: dibujito en su posición interpolada
        for dron in drones:
            if dron.id_dron not in pos:
                continue
            px, py = pos[dron.id_dron]
            c = a_col(px)
            f = a_fila(py)
            write(f, c - 1, _design(dron.id_dron))
            write(f - 1, c, f'D{dron.id_dron}')

        # Imprimir
        os.system('clear')
        print(f"{_CYAN}{_BOLD} Turno {turno_num}/{max_turnos}{_RESET}")
        for fila in grid:
            print(''.join(fila))

    # Frame inicial
    pintar(0)
    time.sleep(0.6)

    for t in range(max_turnos):
        # Recoger destinos de este turno
        destinos: dict[int, tuple[float, float]] = {}
        for dron in drones:
            if not dron.ruta_posiciones or t >= len(dron.ruta_posiciones):
                continue
            turno = dron.ruta_posiciones[t]
            if turno is None:
                continue
            _, paso2 = turno
            obj = next((o for o in paso2 if _is_hub(o) or _is_connection(o)), None)
            if obj is None:
                continue
            if _is_hub(obj):
                destinos[dron.id_dron] = (float(obj.x), float(obj.y))
            elif _is_connection(obj):
                # En vuelo sobre conexión: punto medio
                destinos[dron.id_dron] = (
                    (float(obj.origin.x) + float(obj.destiny.x)) / 2,
                    (float(obj.origin.y) + float(obj.destiny.y)) / 2,
                )

        # Interpolar en N pasos
        N = 5
        for frame in range(N + 1):
            alpha = frame / N
            for id_dron, dest in destinos.items():
                ox, oy = pos[id_dron]
                pos[id_dron] = (
                    ox + (dest[0] - ox) * alpha,
                    oy + (dest[1] - oy) * alpha,
                )
            pintar(t + 1)
            time.sleep(0.08)

        # Fijar en destino exacto
        for id_dron, dest in destinos.items():
            pos[id_dron] = dest

        time.sleep(0.3)

    pintar(max_turnos)
    print(f"\n{_CYAN}{'═' * 40}{_RESET}")
    print(f"\033[32m{_BOLD}  Completado en {max_turnos} turnos.{_RESET}")
    print(f"{_CYAN}{'═' * 40}{_RESET}\n")
