*This project has been created as part of the 42 curriculum by [aitorres].*


<svg width="600" viewBox="0 0 680 130" xmlns="http://www.w3.org/2000/svg">
  <text x="340" y="20"  text-anchor="middle" font-family="monospace" font-size="18" fill="#f5c400" xml:space="preserve">███████╗ ██╗      ██╗    ██╗      ██╗ ███╗   ██╗</text>
  <text x="340" y="36"  text-anchor="middle" font-family="monospace" font-size="18" fill="#f5c400" xml:space="preserve">██╔════╝ ██║       ██║  ██╔╝      ██║ ████╗  ██║</text>
  <text x="340" y="52"  text-anchor="middle" font-family="monospace" font-size="18" fill="#f5c400" xml:space="preserve">█████╗   ██║       ╚██╗██╔╝  ▄▄▄  ██║ ██╔██╗ ██║</text>
  <text x="340" y="68"  text-anchor="middle" font-family="monospace" font-size="18" fill="#f5c400" xml:space="preserve">██╔══╝   ██║         ╚██╔╝   ▀▀▀  ██║ ██║╚██╗██║</text>
  <text x="340" y="84"  text-anchor="middle" font-family="monospace" font-size="18" fill="#f5c400" xml:space="preserve">██║      ███████╗     ██║         ██║ ██║ ╚████║</text>
  <text x="340" y="100" text-anchor="middle" font-family="monospace" font-size="18" fill="#f5c400" xml:space="preserve">╚═╝      ╚══════╝     ╚═╝         ╚═╝ ╚═╝  ╚═══╝</text>
  <text x="340" y="120" text-anchor="middle" font-family="monospace" font-size="12" fill="#f5c400" opacity="0.7" xml:space="preserve">~╚¥╝~     ╠═▄▄═╣     ╠═¤¤═╣     ╠¤¤╣     ╠-¥-╣    ╠--▄▄--╣</text>
</svg>

## Description

**fly-in** is a multi-drone routing simulator built in Python. Given a map of interconnected hubs defined in a plain-text configuration file, the program computes optimized routes for a fleet of drones, schedules their departures to avoid collisions, and visualises the simulation in the terminal.

The goal is to design an efficient drone-routing system that navigates multiple drones through connected zones, minimising simulation turns and managing movement under capacity constraints. Each hub and connection can carry metadata such as a capacity limit, a zone type, or a display colour. The algorithm finds all valid paths from the start hub to the end hub, ranks them, and then assigns each drone to the best available path while respecting per-turn occupancy limits on both hubs and connections.

---

## Instructions

### Requirements

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) (dependency manager)

### Installation

Poetry handles all dependencies automatically. You do not need to install anything manually — the `run` target calls `install` first.

```bash
# Install dependencies only
make install
```

### Running the program

```bash
make run <file.txt>
```

`<file.txt>` must be a valid configuration file (see format below). The path can be relative or absolute.

```bash
# Examples
make run maps/simple.txt
make run /home/user/mymap.txt
```

### Other make targets

| Target | Description |
|---|---|
| `make run <file.txt>` | Clean, install, and run the simulator |
| `make install` | Install all Poetry dependencies |
| `make debug <file.txt>` | Run the simulator under `pdb` debugger |
| `make lint` | Run `flake8` + `mypy` (standard flags) |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, build artefacts |

### Input file format

The configuration file is a plain-text `.txt` file. Lines starting with `#` are comments; blank lines are ignored. The following keys are required exactly once each, except `hub` and `connection` which may appear multiple times.

```
nb_drones: <integer>
start_hub: <name> <x> <y> [<metadata>]
hub:       <name> <x> <y> [<metadata>]
end_hub:   <name> <x> <y> [<metadata>]
connection: <name1>-<name2> [<metadata>]
```

**Hub metadata** (optional, inside `[...]`, space-separated `key=value` pairs):

| Key | Values | Default |
|---|---|---|
| `color` | `green`, `blue`, `red`, `yellow`, `gray`, `gold`, `cyan`, `purple`, … | none |
| `zone` | `normal`, `blocked`, `restricted`, `priority` | `normal` |
| `max_drones` | integer | `1` |
| `max_link_capacity` | integer | `1` |

**Connection metadata**: only `max_link_capacity=<integer>` is accepted.

**Zone behaviour:**
- `normal` — standard traversal, one turn per hop
- `blocked` — hub is excluded from all routes
- `restricted` — hub costs **two turns** to traverse (drone waits one extra turn)
- `priority` — hub boosts the ranking of any route passing through it

**Minimal example:**

```
nb_drones: 3
start_hub: origin 0 0 [color=green zone=normal max_drones=2]
hub:       mid    5 3 [color=blue  zone=restricted max_drones=1]
hub:       cross 10 0 [zone=priority]
end_hub:   dest  15 0 [color=red]
connection: origin-mid   [max_link_capacity=2]
connection: mid-cross
connection: cross-dest
```

---

## Algorithm

The routing engine lives in `src/algorithm/prioritized_planner.py` and runs in five sequential steps.

### 1 — Route discovery (`find_routes_from_start`)

A recursive depth-first search explores all paths from every hub flagged `start=True` to the hub flagged `end=True`. To avoid infinite loops on cyclic maps, the function tracks how many times each hub has already appeared in the current path and skips any branch where a hub would be visited more than five times.

### 2 — Route ranking (`sort_all_routes`)

Every discovered route is scored along three dimensions:

1. **Repetitions** (ascending) — routes that traverse the same connection more than once are penalised.
2. **Turn count** (ascending) — shorter routes are preferred. Passing through a `restricted` hub adds one extra turn to the count.
3. **Priority score** (descending) — each `priority` hub on the route increments a bonus counter; routes with higher bonuses rank above equally-long alternatives.

The sort key is the tuple `(repetitions, turns, -priority)`, so the comparisons are applied in that exact order.

### 3 — Turn expansion (`expand_routes` / `_route_by_turns`)

Each ranked route (a list of `Connection` objects) is converted into a list of *turns*, where each turn is a two-element step `[paso1, paso2]`:

- **Normal hop**: one turn — `[origin + connection, destination]`
- **Restricted hop**: two turns — the drone spends an extra turn inside the restricted hub before moving on.

This expanded representation makes per-turn capacity checks straightforward.

### 4 — Drone assignment (`assign_map`)

For each drone, the scheduler iterates over increasing *start shifts* (0, 1, 2, …) and, for each shift, tries every route in ranked order. A route placement is accepted only if, at every turn it would occupy:

- a hub with fewer than `max_drones` drones already there at that turn, and
- a connection with fewer than `max_link_capacity` drones already using it at that turn.

The acceptance check is handled by `check_and_generate_plan`. Once a valid placement is found, `register_usage` records the new occupancy counts so subsequent drones see the updated state.

### 5 — Occupancy tracking (`register_usage`)

Two dictionaries maintain the global schedule:

- `uso_hubs`: keyed by `(hub_name, turn_index)` → drone count
- `connections_use`: keyed by `((origin_name, dest_name), turn_index)` → drone count

These are updated atomically for every accepted drone placement.

---

## Visual Representation

After the schedule is computed, the program presents an interactive menu offering two display modes. Both use ANSI escape codes and require a standard colour-capable terminal.

### Mode 1 — Text turn table (press `1`)

The simulation is printed as a structured table. Each row corresponds to one turn; each column corresponds to one drone. Hub names appear in their configured colour; in-transit connections are shown in italic yellow. A 0.5-second delay is inserted between turns so the output scrolls at a readable pace rather than flooding the screen instantly.

This mode is useful for auditing the exact schedule: which drone is where, at which turn, and whether any capacity constraints were tight.

### Mode 2 — Animated terminal map (press `2`)

The hubs are laid out on a character grid using their real `x` and `y` coordinates, scaled to fit the current terminal window. Each drone is represented by a small ASCII glyph (e.g. `╠═▄▄═╣`) rendered at its current position. Between turns the drone glyphs move smoothly across the grid using five interpolated frames at 0.08 s each, giving the impression of flight.

Hub symbols distinguish roles at a glance: `◉` marks the start hub, `✦` marks the end hub, and `·` marks ordinary intermediate hubs. Hub names (first three characters) are printed just above each symbol.

This mode conveys the spatial structure of the map and makes congestion, detours through restricted zones, and staggered departures immediately visible.

### Launch banner

Before either display mode runs, a decorative banner shows the total drone count and prints one randomly coloured ASCII glyph per drone, giving a quick visual sense of fleet size.

### Interactive menu

After the initial run the program loops, allowing the user to replay either mode without re-running the simulation:

- `1` — reprint the text table
- `2` — replay the animated map
- `q` — exit

---

## Resources

### Multi-agent pathfinding and graph search

- **Sharon, G., Stern, R., Felner, A., & Sturtevant, N.** (2015). Conflict-Based Search for Optimal Multi-Agent Pathfinding. *Artificial Intelligence*, 219, 40–66.
- **Silver, D.** (2005). Cooperative Pathfinding. *Proceedings of the AAAI Workshop on Multiagent Pathfinding*.
- **Hart, P. E., Nilsson, N. J., & Raphael, B.** (1968). A Formal Basis for the Heuristic Determination of Minimum Cost Paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2), 100–107. *(A\* algorithm)*
- **Russell, S., & Norvig, P.** — *Artificial Intelligence: A Modern Approach* — chapters on search algorithms and constraint satisfaction.

### Python documentation

- [Python `typing` module](https://docs.python.org/3/library/typing.html)
- [Python `dataclasses` module](https://docs.python.org/3/library/dataclasses.html)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Poetry documentation](https://python-poetry.org/docs/)

### AI assistance

**Claude** (Anthropic) was used in this project for the following tasks:

- **Translation**: all Spanish comments, docstrings, and inline notes in the source code were translated to English using the Claude API.
- **Linting adaptations**: Claude helped resolve `flake8` style issues (line length, unused imports, import placement) and `mypy` type annotation gaps (tightening `Any`-typed signatures, adding missing return types, resolving `Dict`/`Tuple` generics for Python 3.10 compatibility).
- **README writing**: this document was written with Claude as a drafting and editing aid, following the structure required by the 42 curriculum.

Claude was not used to write core algorithm logic or data-structure design; those were developed and debugged by the author.
