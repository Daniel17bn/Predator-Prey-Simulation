# Env 2

- adds movement speed

## Agents

- Wolf
- Sheep

## Traits

**Wolf**

- movement: random
- speed: number of moves during each time step (agent chooses random direction at each move) (at each move check if wolf+sheep on same square)
- lifespan: fixed max with no food (eat sheep --> reset lifespan)
- eating: eat sheep when on same square
- reproduction: random chance each time step

**Sheep**

- movement: random
- speed: number of moves during each time step (agent chooses random direction at each move) (at each move check if wolf+sheep on same square)
- lifespan: infinite
- eating: /
- reproduction: random chance each time step

## Initial Parameters

- Grid layout : ? x ?
- Wolf population: ?
- Sheep population: ?
