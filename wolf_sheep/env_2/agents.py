from mesa.discrete_space import CellAgent, FixedAgent

from parameters import (
    ENERGY_COST_PER_STEP,
    SHEEP_REPRODUCE,
    SHEEP_STARTING_ENERGY,
    WOLF_REPRODUCE,
    WOLF_STARTING_ENERGY,
    GRASS_REGROWTH_TIME,
    ENERGY_FROM_FOOD_WOLF,
    ENERGY_FROM_FOOD_SHEEP,
    MIN_ENERGY_TO_REPRODUCE,
)


class Animal(CellAgent):
    """The base animal class."""
    def __init__(
        self, 
        model, 
        energy,
        p_reproduce,
        energy_from_food,
        cell=None
    ):
        """Initialize an animal.

        Args:
            model: Model instance
            energy: Starting amount of energy
            p_reproduce: Probability of reproduction (asexual)
            energy_from_food: Energy obtained from 1 unit of food
            cell: Cell in which the animal starts
        """
        super().__init__(model)
        self.energy = energy
        self.p_reproduce = p_reproduce
        self.cell = cell
        self.energy_from_food = energy_from_food
        
    def spawn_offspring(self):
        """Create offspring by splitting energy and creating new instance."""
        self.energy /= 2
        self.__class__(
            model=self.model,
            energy=self.energy,
            p_reproduce=self.p_reproduce,
            energy_from_food=self.energy_from_food,
            cell=self.cell,
        )

    def step(self):
        """Execute one step of the animal's behavior."""
        # Move to random neighboring cell
        self.move()

        # Allow animal subclasses to gain energy from food
        self.feed()

        # Decrease energy each step
        self.energy -= ENERGY_COST_PER_STEP

        # Handle death and reproduction
        if self.energy < 0: # If energy is below zero, the animal dies
            self.remove()
        elif self.random.random() < self.p_reproduce and self.energy >= MIN_ENERGY_TO_REPRODUCE: # If energy is above threshold and random chance, reproduce
            self.spawn_offspring()

    def feed(self):
        """Gain energy from food, if available."""
        pass

    def move(self):
            """Move to a random neighboring cell."""
            self.cell = self.cell.neighborhood.select_random_cell()


class Sheep(Animal):
    """A sheep that walks around, reproduces (asexually) and gets eaten."""

    def __init__(
        self,
        model,
        energy=SHEEP_STARTING_ENERGY,
        p_reproduce=SHEEP_REPRODUCE,
        energy_from_food=ENERGY_FROM_FOOD_SHEEP,
        cell=None,
    ):
        super().__init__(model, energy, p_reproduce, energy_from_food, cell)

    def feed(self):
        """If possible, eat grass at current location."""
        grass_patch = next(
            (obj for obj in self.cell.agents if isinstance(obj, GrassPatch)), None
        )
        if grass_patch is not None and grass_patch.fully_grown:
            self.energy += self.energy_from_food
            grass_patch.get_eaten()


class Wolf(Animal):
    """A wolf that walks around, reproduces (asexually) and eats sheep."""

    def __init__(
        self,
        model,
        energy=WOLF_STARTING_ENERGY,
        p_reproduce=WOLF_REPRODUCE,
        energy_from_food=ENERGY_FROM_FOOD_WOLF,
        cell=None,
    ):
        super().__init__(model, energy, p_reproduce, energy_from_food, cell)

    def feed(self):
        """If possible, eat a sheep at current location."""
        sheep = [obj for obj in self.cell.agents if isinstance(obj, Sheep)]
        if sheep:  # If there are any sheep present
            sheep_to_eat = self.random.choice(sheep)
            self.energy += self.energy_from_food
            sheep_to_eat.remove()

class GrassPatch(FixedAgent):
    """A patch of grass that grows at a fixed rate and can be eaten by sheep."""

    def __init__(self, 
                 model, 
                 countdown, 
                 grass_regrowth_time=GRASS_REGROWTH_TIME, 
                 cell=None):
        """Create a new patch of grass.

        Args:
            model: Model instance
            countdown: Time until grass is fully grown again
            grass_regrowth_time: Time needed to regrow after being eaten
            cell: Cell to which this grass patch belongs
        """
        super().__init__(model)
        self.fully_grown = countdown == 0
        self.grass_regrowth_time = grass_regrowth_time
        self.cell = cell

        # Schedule initial growth if not fully grown
        if not self.fully_grown:
            self.model.schedule_event(self.regrow, after=countdown)

    def regrow(self):
        """Regrow the grass."""
        self.fully_grown = True

    def get_eaten(self):
        """Mark grass as eaten and schedule regrowth."""
        self.fully_grown = False
        self.model.schedule_event(self.regrow, after=self.grass_regrowth_time)