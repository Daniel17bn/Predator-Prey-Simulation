"""
Wolf-Sheep Predation Model
================================

Replication of the model found in NetLogo:
    Wilensky, U. (1997). NetLogo Wolf Sheep Predation model.
    http://ccl.northwestern.edu/netlogo/models/WolfSheepPredation.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import math

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.discrete_space import OrthogonalVonNeumannGrid
from agents import GrassPatch, Sheep, Wolf
from mesa.experimental.scenarios import Scenario
from parameters import (
    ENERGY_COST_PER_STEP,
    GRASS_ENABLED,
    GRID_HEIGHT,
    GRID_WIDTH,
    INITIAL_SHEEP,
    INITIAL_WOLVES,
    INITIAL_GRASS_PATCHES,
    GRASS_REGROWTH_TIME,
    MIN_ENERGY_TO_REPRODUCE,
    RANDOM_SEED,
    SHEEP_STARTING_ENERGY,
    WOLF_STARTING_ENERGY,
    ENERGY_FROM_FOOD_SHEEP,
    ENERGY_FROM_FOOD_WOLF,
    SHEEP_REPRODUCE,
    WOLF_REPRODUCE,
)

MOORE_DIRECTIONS = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def _average_energy(model, agent_type):
    animals = model.agents_by_type.get(agent_type, ())
    return sum(animal.energy for animal in animals) / len(animals) if animals else 0


class WolfSheepScenario(Scenario):
    """Scenario parameters for the Wolf-Sheep model.

    Args:
        height: Height of the grid
        width: Width of the grid
        initial_sheep: Number of sheep to start with
        initial_wolves: Number of wolves to start with
        sheep_reproduce: Probability of each sheep reproducing each step
        wolf_reproduce: Probability of each wolf reproducing each step
        energy_from_food_wolf: Energy a wolf gains from eating a sheep
        grass: Whether to have the sheep eat grass for energy
        grass_regrowth_time: How long it takes for a grass patch to regrow
                            once it is eaten
        energy_from_food_sheep: Energy sheep gain from grass, if enabled
        rng: Random rng
    """

    width: int = GRID_WIDTH
    height: int = GRID_HEIGHT
    initial_sheep: int = INITIAL_SHEEP
    initial_wolves: int = INITIAL_WOLVES
    sheep_reproduce: float = SHEEP_REPRODUCE
    wolf_reproduce: float = WOLF_REPRODUCE
    grass: bool = GRASS_ENABLED
    initial_grass_patches: int = INITIAL_GRASS_PATCHES
    grass_regrowth_time: int = GRASS_REGROWTH_TIME
    sheep_starting_energy: float = SHEEP_STARTING_ENERGY
    wolf_starting_energy: float = WOLF_STARTING_ENERGY
    energy_from_food_sheep: float = ENERGY_FROM_FOOD_SHEEP
    energy_from_food_wolf: float = ENERGY_FROM_FOOD_WOLF
    energy_cost_per_step: float = ENERGY_COST_PER_STEP
    min_energy_to_reproduce: float = MIN_ENERGY_TO_REPRODUCE
    rng: int = RANDOM_SEED


class WolfSheep(Model):
    """Wolf-Sheep Predation Model.

    A model for simulating wolf and sheep (predator-prey) ecosystem modelling.
    """

    description = (
        "A model for simulating wolf and sheep (predator-prey) ecosystem modelling."
    )

    def __init__(self, scenario=None):
        """Create a new Wolf-Sheep model with the given parameters.

        Args:
            scenario: WolfSheepScenario containing model parameters.
        """
        if scenario is None:
            scenario = WolfSheepScenario()

        if scenario.width <= 0 or scenario.height <= 0:
            raise ValueError("width and height must be positive.")
        if scenario.initial_sheep < 0 or scenario.initial_wolves < 0:
            raise ValueError("initial animal counts cannot be negative.")
        if not 0 <= scenario.initial_grass_patches:
            raise ValueError("initial_grass_patches cannot be negative.")
        if scenario.grass_regrowth_time <= 0:
            raise ValueError("grass_regrowth_time must be positive.")
        if not 0 <= scenario.sheep_reproduce <= 1:
            raise ValueError("sheep_reproduce must be between 0 and 1.")
        if not 0 <= scenario.wolf_reproduce <= 1:
            raise ValueError("wolf_reproduce must be between 0 and 1.")
        if scenario.sheep_starting_energy < 0 or scenario.wolf_starting_energy < 0:
            raise ValueError("starting energy values cannot be negative.")
        if scenario.energy_from_food_sheep < 0 or scenario.energy_from_food_wolf < 0:
            raise ValueError("food energy values cannot be negative.")
        if scenario.energy_cost_per_step < 0:
            raise ValueError("energy_cost_per_step cannot be negative.")
        if scenario.min_energy_to_reproduce < 0:
            raise ValueError("min_energy_to_reproduce cannot be negative.")

        if scenario.rng is None:
            scenario.rng = RANDOM_SEED
        if isinstance(scenario.rng, str):
            scenario.rng = int(scenario.rng)

        super().__init__(scenario=scenario)

        # Initialize model parameters
        self.height = scenario.height
        self.width = scenario.width
        self.grass = scenario.grass
        self.energy_cost_per_step = scenario.energy_cost_per_step
        self.min_energy_to_reproduce = scenario.min_energy_to_reproduce

        # Create grid using experimental cell space
        self.grid = OrthogonalVonNeumannGrid(
            [self.height, self.width],
            torus=True,
            capacity=math.inf,
            random=self.random,
        )

        # Set up data collection
        model_reporters = {
            "Wolves": lambda m: len(m.agents_by_type.get(Wolf, ())),
            "Sheep": lambda m: len(m.agents_by_type.get(Sheep, ())),
            "Wolves total energy": lambda m: sum(
                animal.energy for animal in m.agents_by_type.get(Wolf, ())
            ),
            "Sheep total energy": lambda m: sum(
                animal.energy for animal in m.agents_by_type.get(Sheep, ())
            ),
            "Wolves average energy": lambda m: _average_energy(m, Wolf),
            "Sheep average energy": lambda m: _average_energy(m, Sheep),
        }
        for species, agent_type in (("Sheep", Sheep), ("Wolves", Wolf)):
            for speed in (1, 2, 3):
                model_reporters[f"{species} speed {speed}"] = (
                    lambda m, agent_type=agent_type, speed=speed: sum(
                        animal.speed == speed
                        for animal in m.agents_by_type.get(agent_type, ())
                    )
                )

        model_reporters["Grass"] = lambda m: sum(
            patch.fully_grown
            for patch in m.agents_by_type.get(GrassPatch, ())
        )
        model_reporters["Grass energy"] = lambda m: sum(
            patch.energy for patch in m.agents_by_type.get(GrassPatch, ())
        )

        self.datacollector = DataCollector(model_reporters)

        # Create sheep:
        Sheep.create_agents(
            self,
            scenario.initial_sheep,
            energy=scenario.sheep_starting_energy,
            p_reproduce=scenario.sheep_reproduce,
            energy_from_food=scenario.energy_from_food_sheep,
            cell=self.random.choices(
                self.grid.all_cells.cells, k=scenario.initial_sheep
            ),
        )
        # Ensure a small initial wolf population includes every speed group.
        wolf_speeds = [1, 2, 3][: scenario.initial_wolves]
        if scenario.initial_wolves > 3:
            wolf_speeds.extend(
                self.random.choices(
                    (1, 2, 3), k=scenario.initial_wolves - 3
                )
            )
        self.random.shuffle(wolf_speeds)

        # Create Wolves:
        Wolf.create_agents(
            self,
            scenario.initial_wolves,
            energy=scenario.wolf_starting_energy,
            p_reproduce=scenario.wolf_reproduce,
            energy_from_food=scenario.energy_from_food_wolf,
            speed=wolf_speeds,
            cell=self.random.choices(
                self.grid.all_cells.cells, k=scenario.initial_wolves
            ),
        )

        # Create grass patches if enabled
        if self.grass:
            possibly_fully_grown = [True, False]
            cells = list(self.grid.all_cells.cells)
            if not 0 <= scenario.initial_grass_patches <= len(cells):
                raise ValueError(
                    "initial_grass_patches must be between 0 and the number "
                    "of grid cells."
                )

            # random.sample selects distinct cells, so no cell is repeated.
            grass_cells = self.random.sample(
                cells,
                scenario.initial_grass_patches,
            )
            for cell in grass_cells:
                fully_grown = self.random.choice(possibly_fully_grown)
                countdown = (
                    0
                    if fully_grown
                    else self.random.randrange(1, scenario.grass_regrowth_time + 1)
                )
                GrassPatch(
                    self,
                    countdown,
                    scenario.grass_regrowth_time,
                    cell,
                    scenario.energy_from_food_sheep,
                )

        # Collect initial data
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """Execute one step of the model."""
        animals = [
            *list(self.agents_by_type.get(Sheep, ())),
            *list(self.agents_by_type.get(Wolf, ())),
        ]

        for animal in animals:
            animal.has_eaten = False

        for round_number in (1, 2, 3):
            # Movement and interactions happen once for each round.
            self._move_round(animals, round_number)
            self._resolve_interactions()

        self._finish_timestep(animals)

        # Collect data
        self.datacollector.collect(self)

    def _move_round(self, animals, round_number):
        """Choose and apply all movement decisions for one round."""
        # Round 1 accepts speed 3, round 2 accepts speeds 2-3,
        # and round 3 accepts every speed.
        minimum_speed = 4 - round_number
        destinations = {}

        for animal in animals:
            if animal.cell is None or animal.speed < minimum_speed:
                continue

            # Decisions use the original positions until all are collected.
            row, column = animal.cell.coordinate
            row_offset, column_offset = self.random.choice(MOORE_DIRECTIONS)
            destination = (
                (row + row_offset) % self.height,
                (column + column_offset) % self.width,
            )
            destinations[animal] = self.grid[destination]

        # Applying destinations afterward makes movement simultaneous.
        for animal, destination in destinations.items():
            if animal.cell is not None:
                animal.cell = destination

    def _resolve_interactions(self):
        """Resolve grass consumption and predation after a movement round."""
        for cell in self.grid:
            sheep = sorted(
                (agent for agent in cell.agents if isinstance(agent, Sheep)),
                key=lambda agent: agent.unique_id,
            )
            wolves = sorted(
                (agent for agent in cell.agents if isinstance(agent, Wolf)),
                key=lambda agent: agent.unique_id,
            )
            grass = next(
                (
                    agent
                    for agent in cell.agents
                    if isinstance(agent, GrassPatch)
                ),
                None,
            )

            eligible_sheep = [
                animal for animal in sheep if not animal.has_eaten
            ]
            if grass is not None and grass.fully_grown and eligible_sheep:
                # One grass meal is shared equally by all eligible sheep.
                energy_share = grass.energy / len(eligible_sheep)
                for animal in eligible_sheep:
                    animal.energy += energy_share
                    animal.has_eaten = True
                grass.get_eaten()

            eligible_wolves = [
                animal for animal in wolves if not animal.has_eaten
            ]
            living_sheep = [
                animal for animal in sheep if animal.cell is not None
            ]
            if eligible_wolves and living_sheep:
                if len(living_sheep) < len(eligible_wolves):
                    # When prey is scarce, all available sheep are consumed
                    # and their configured food value is shared by the wolves.
                    n_sheep = len(living_sheep)
                    n_wolves = len(eligible_wolves)
                    energy_share = (
                        n_sheep * eligible_wolves[0].energy_from_food
                    ) / n_wolves
                    for wolf in eligible_wolves:
                        wolf.energy += energy_share
                        wolf.has_eaten = True
                    for prey in living_sheep:
                        prey.remove()
                else:
                    # When prey is plentiful, each wolf gets one distinct
                    # randomly selected sheep and one food share.
                    selected_sheep = self.random.sample(
                        living_sheep,
                        len(eligible_wolves),
                    )
                    for wolf, prey in zip(eligible_wolves, selected_sheep):
                        wolf.energy += wolf.energy_from_food
                        wolf.has_eaten = True
                        prey.remove()

    def _finish_timestep(self, animals):
        """Apply timestep energy costs, death, and reproduction."""
        for animal in animals:
            if animal.cell is None:
                continue

            # Movement rounds do not add extra energy costs.
            animal.energy -= self.energy_cost_per_step
            if animal.energy < 0:
                animal.remove()

        for animal in animals:
            if (
                animal.cell is not None
                and animal.energy >= self.min_energy_to_reproduce
                and self.random.random() < animal.p_reproduce
            ):
                # The snapshot excludes offspring from this timestep's rounds.
                animal.spawn_offspring()
