# Environment 1: Basic Wolf-Sheep Predation

Environment 1 is the first minimal version of the predator-prey simulation. It
contains only wolves and sheep: there is no grass, weather, terrain, or other
food source. The model advances in discrete time steps, and every living animal
acts once during each step.

All environment and agent defaults are centralized. The model,
agents, and visualization import their values from that file so a parameter
only needs to be changed in one place.

## Model Rules

- The environment uses a two-dimensional `50 x 50` grid by default.
- The grid is a torus: an animal that moves across one edge reappears on the
  opposite edge.
- Each cell can contain any number of animals.
- Movement is random and uses the orthogonal Von Neumann neighborhood. An animal
  chooses one neighboring cell at random rather than moving diagonally.
- Animals may begin in the same cell. Initial positions are selected randomly,
  with replacement, so multiple animals can occupy one cell.
- There is no grass and sheep do not gain energy from eating.
- The model records the number of living wolves and sheep after initialization
  and after every completed time step.

## Agents

### Sheep

- Initial energy: `100`
- Reproduction probability: `0.012` per time step
- Movement: one random orthogonal neighboring cell per step
- Feeding: none
- Death: energy decreases by one each step. A sheep is removed when its energy
  becomes less than `0`.
- Reproduction: if it survives the step, it has a `1.2%` chance of producing one
  offspring.

### Wolves

- Initial energy: `100`
- Reproduction probability: `0.008` per time step
- Movement: one random orthogonal neighboring cell per step
- Feeding: eats every sheep in its destination cell
- Food effect: eating resets the wolf's energy to its initial energy (`100`).
- Death: energy decreases by one each step. A wolf is removed when its energy
  becomes less than `0`.
- Reproduction: if it survives the step, it has a `0.8%` chance of producing one
  offspring.

## Time-Step Order

Each model step follows this order:

1. All sheep act once, in a random order.
2. All wolves act once, in a random order.
3. The population data is collected.

Each animal's individual action follows this order:

1. Move to a random neighboring cell.
2. Feed, if the animal has a food rule.
3. Decrease energy by `1`.
4. If energy is less than `0`, remove the animal from the model.
5. Otherwise, test the reproduction probability and create an offspring if the
   reproduction test succeeds.

Because sheep act before wolves, sheep get their movement and reproduction
opportunity before wolves hunt during the same model step. A wolf can eat sheep
that are already in its destination cell, including sheep that moved there
earlier in that step.

## Wolf-Sheep Interaction

When a wolf finishes moving, it checks its current cell for sheep. If one or
more sheep are present:

1. The wolf removes all sheep in that cell.
2. The wolf's energy is reset to `100`.
3. The wolf loses `1` energy at the normal end-of-step energy update.

Therefore, a wolf that arrives with `0` energy on a cell containing sheep eats
before its energy is reduced and survives the step with `99` energy. A wolf
that arrives with `0` energy on an empty cell becomes `-1` and dies.

## Reproduction

Reproduction is asexual. A successful reproduction creates one offspring of the
same type in the parent's current cell. The offspring starts with its species'
configured starting energy and inherits the parent's reproduction probability;
no energy is transferred from the parent. The parent must survive its energy
check before it can reproduce.

## Initial Parameters

The default `WolfSheepScenario` values are:

| Parameter                      | Default value | Description                          |
| ------------------------------ | ------------: | ------------------------------------ |
| Grid width                     |          `50` | Number of columns                    |
| Grid height                    |          `50` | Number of rows                       |
| Initial sheep                  |         `150` | Sheep created at initialization      |
| Initial wolves                 |          `20` | Wolves created at initialization     |
| Sheep reproduction probability |       `0.012` | Probability per sheep per step       |
| Wolf reproduction probability  |       `0.008` | Probability per wolf per step        |
| Sheep starting energy          |         `100` | Also the sheep energy default        |
| Wolf starting energy           |         `100` | Also the wolf's food-reset energy    |
| Energy cost per step           |           `1` | Paid after movement and feeding      |
| Grass                          |      Disabled | No grass agents or grass energy      |
| Random seed                    |          `42` | Default random-number-generator seed |

The visualization can override the initial sheep population, sheep reproduction
rate, initial wolf population, wolf reproduction rate, and random seed. The
slider starting values match the corresponding `WolfSheepScenario` defaults.
The active value is the value supplied when the model is created.

Visualization control ranges are:

| Control                  | Minimum | Maximum |   Step |
| ------------------------ | ------: | ------: | -----: |
| Initial sheep population |    `10` |   `300` |    `1` |
| Initial wolf population  |     `5` |   `100` |    `1` |
| Sheep reproduction rate  |  `0.01` |   `1.0` | `0.01` |
| Wolf reproduction rate   |  `0.01` |   `1.0` | `0.01` |
