# Env 1

- continuous time environment, no generations to update, update at each time_step (more realistic)

## Ideas

- simplest model possible
- no grass
- no energy
- random movement
- if wolf and sheep on the same square --> sheep die
- fixed probability of reproduction, at each step

## Agents

- Wolf
- Sheep

## Traits

**Wolf**

- movement: random
- lifespan: fixed max with no food (eat sheep --> reset lifespan)
- eating: eat sheep when on same square
- reproduction: random chance each time step

**Sheep**

- movement: random
- lifespan: fixed number of stepss
- eating: /
- reproduction: random chance each time step

## Initial Parameters

- Grid layout : ? x ?
- Wolf population: ?
- Sheep population: ?
