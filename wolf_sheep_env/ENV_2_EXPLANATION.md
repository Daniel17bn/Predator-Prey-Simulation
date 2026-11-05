# Wolf-Sheep Simulation

This document explains the rules and structure of the simulation in this
directory. The implementation is in the `wolf_sheep_env` package.

## Files

- `parameters.py` contains the values used to configure the simulation.
- `agents.py` defines sheep, wolves, and grass patches.
- `model.py` creates the grid and controls each simulation timestep.
- `app.py` creates the Solara visualization.
- `test_model.py` contains automated tests for the main rules.

## Parameters

The current values in `parameters.py` are:

| Parameter                 |  Value | Meaning                              |
| ------------------------- | -----: | ------------------------------------ |
| `GRID_WIDTH`              |     20 | Grid width                           |
| `GRID_HEIGHT`             |     20 | Grid height                          |
| `INITIAL_SHEEP`           |    300 | Sheep at the beginning               |
| `INITIAL_WOLVES`          |      3 | Wolves at the beginning              |
| `GRASS_ENABLED`           | `True` | Whether grass is created and eaten   |
| `INITIAL_GRASS_PATCHES`   |    300 | Grass patches at the beginning       |
| `GRASS_REGROWTH_TIME`     |     20 | Timesteps before eaten grass regrows |
| `RANDOM_SEED`             |     40 | Default random seed                  |
| `SHEEP_REPRODUCE`         |   0.08 | Sheep reproduction probability       |
| `WOLF_REPRODUCE`          |  0.003 | Wolf reproduction probability        |
| `SHEEP_STARTING_ENERGY`   |     45 | Initial sheep energy                 |
| `WOLF_STARTING_ENERGY`    |     35 | Initial wolf energy                  |
| `ENERGY_COST_PER_STEP`    |      2 | Energy lost once per timestep        |
| `ENERGY_FROM_FOOD_SHEEP`  |     40 | Energy contained in one grass patch  |
| `ENERGY_FROM_FOOD_WOLF`   |      6 | Energy gained from a consumed sheep  |
| `MIN_ENERGY_TO_REPRODUCE` |     90 | Minimum energy required to reproduce |

You can change these values manually in `parameters.py`.

## Grid and initial setup

The model creates a `20 x 20` toroidal grid. A toroidal grid wraps around:
an animal leaving one edge appears on the opposite edge.

There are 400 available cells. The model creates exactly
`INITIAL_GRASS_PATCHES` grass patches by selecting cells with
`random.sample()`. Sampling without replacement means that the initial grass
patches are placed in different cells. With the current configuration, 350
different cells receive grass.

Sheep and wolves are initially placed using random choices. Multiple animals
may occupy the same cell.

When at least three wolves are initially created, the model assigns speeds so
that speed 1, speed 2, and speed 3 are each represented at least once. Any
additional wolves receive a random speed. Offspring inherit their parent's
speed.

## Animals

`Animal` is the shared base class for `Sheep` and `Wolf`. Every animal has:

- `energy`
- `p_reproduce`
- `energy_from_food`
- `cell`
- `speed`
- `has_eaten`

### Speed

Each newly created animal receives a random speed of 1, 2, or 3 with equal
probability. Speed remains constant throughout its lifetime.

Offspring inherit the exact speed of their parent. Speed affects how many
movement rounds an animal receives, but does not change its energy cost.

### Eating state

`has_eaten` records whether an animal has successfully eaten during the
current timestep. It is reset at the beginning of the next timestep.

Eating does not stop the animal from moving in later rounds. It only prevents
that animal from eating again during the same timestep.

## Grass patches

Each `GrassPatch` is a fixed Mesa agent attached to one cell. A patch stores:

- `fully_grown`: whether sheep can eat it
- `grass_regrowth_time`: time required to regrow after being eaten
- `food_energy`: the patch's available energy
- `energy`: its current available energy

A fully grown patch is shown in green. A patch that exists but is regrowing is
shown in brown. A cell without a patch has no grass marker.

When a patch is eaten:

1. `fully_grown` becomes `False`.
2. Its energy becomes zero.
3. A regrowth event is scheduled.

After the configured regrowth time:

1. `fully_grown` becomes `True`.
2. Its energy is restored to `food_energy`.

The number of grass patches does not change during the simulation. Only their
growth state and available energy change.

## Timestep structure

`WolfSheep.step()` controls one complete timestep. It uses a snapshot of the
animals that existed at the beginning of the timestep.

The timestep has these phases:

1. Reset `has_eaten` for all animals.
2. Run movement Round 1.
3. Resolve grass consumption and predation.
4. Run movement Round 2.
5. Resolve grass consumption and predation.
6. Run movement Round 3.
7. Resolve grass consumption and predation.
8. Apply energy costs, death, and reproduction.
9. Collect data.

## Three movement rounds

The movement schedule is:

| Round | Animals that move             |
| ----- | ----------------------------- |
| 1     | Speed 3                       |
| 2     | Speed 2 and speed 3           |
| 3     | Speed 1, speed 2, and speed 3 |

Consequently:

- Speed 1 moves once.
- Speed 2 moves twice.
- Speed 3 moves three times.

Every eligible animal independently chooses one of the eight Moore-neighborhood
directions:

- north
- south
- east
- west
- northeast
- northwest
- southeast
- southwest

Diagonal movement counts as one movement. Both coordinates are wrapped
independently at the grid boundaries.

## Simultaneous movement

Movement is implemented in two phases:

1. `_move_round()` calculates every eligible animal's destination.
2. The destinations are applied after all choices have been collected.

This prevents an animal processed later from seeing another animal's new
position during the same round. Animals with different speeds are treated
together whenever they are eligible for the same round.

Animals that die or are removed have `cell is None` and are skipped in later
rounds.

## Grass consumption

After each movement round, every cell is inspected. All living sheep in the
cell are considered, including sheep that did not move in that round.

Only sheep with `has_eaten == False` can participate. If a grown grass patch
has eligible sheep:

1. The patch energy is divided equally among all eligible sheep.
2. Each sheep receives its share.
3. Each sheep is marked as having eaten.
4. The patch is consumed once and starts regrowing.

The total energy distributed cannot exceed the patch's stored energy.

For example, a 50-energy patch shared by two sheep gives each sheep 25 energy.
The sheep may still move in later rounds, but neither can eat again during that
timestep.

## Predation

After each movement round, wolves and sheep in the same cell are considered.
Wolves that already ate during the timestep are excluded, but wolves that did
not move during the current round are still eligible.

If several sheep share a cell with wolves, each eligible wolf can eat at most
one sheep during the timestep. When there are at least as many sheep as wolves,
distinct sheep are selected randomly and each wolf receives the configured
`ENERGY_FROM_FOOD_WOLF` value. When sheep are outnumbered, all available sheep
are consumed and each wolf receives
`number_of_sheep * ENERGY_FROM_FOOD_WOLF / number_of_wolves`. Each sheep is
removed at most once.

## Energy, death, and reproduction

Energy cost is applied once after all three movement rounds. Movement speed
does not create additional energy costs.

Animals with energy below zero are removed. Dead animals do not participate in
later rounds.

Living animals reproduce after energy costs are applied when:

1. Their energy is at least `MIN_ENERGY_TO_REPRODUCE`.
2. A random reproduction check succeeds.

Reproduction splits the parent's current energy equally:

- The parent keeps half.
- The offspring receives the other half.

The offspring inherits the parent's reproduction probability, food-energy
value, cell, and speed. Because the timestep uses an initial animal snapshot,
new offspring do not move or interact until the next timestep.

## Data collection

Mesa's `DataCollector` records:

- total wolves
- total sheep
- total wolf energy
- total sheep energy
- average wolf energy
- average sheep energy
- speed-1 sheep
- speed-2 sheep
- speed-3 sheep
- speed-1 wolves
- speed-2 wolves
- speed-3 wolves
- fully grown grass patches
- available grass energy

The six speed measurements show how the speed distribution changes as animals
die and reproduce.

## Visualization

`app.py` displays:

- wolves as red circles
- sheep as cyan circles
- fully grown grass as green squares
- regrowing grass as brown squares

The Solara page also displays the collected population data and retains the
standard simulation controls. Rendering adds overhead; running the model
directly without `app.py` is faster for performance experiments.

## Tests

`test_model.py` uses `pytest` to verify the main rules:

- offspring inherit speed
- movement follows the three-round schedule
- diagonal toroidal wrapping works
- shared grass energy is divided equally
- a grass patch is consumed once
- shared predation divides prey energy equally
- a prey is removed once
- energy cost is applied once per timestep
- all six speed reporters exist
- the configured number of grass patches uses distinct cells

Run the tests from the `wolf_sheep_env` directory with:

```powershell
..\.venv\Scripts\python.exe -m pytest .\test_model.py -q
```

The exact path may need to be adjusted depending on the terminal's current
directory and virtual-environment location.

## Running the model

From the `wolf_sheep_env` directory:

```powershell
solara run app.py
```

For a non-visual run from the `wolf_sheep_env` directory:

```powershell
..\.venv\Scripts\python.exe .\run_simulation.py
```

`run_simulation.py` advances the model for 1,000 timesteps and prints the
latest collected population statistics. It also saves population, total energy,
average energy, and speed-distribution graphs in `simulation_output/`. It
avoids browser and rendering overhead while preserving the simulation rules.
