from mesa.discrete_space import CellAgent, FixedAgent

from parameters import (
    SHEEP_REPRODUCE,
    SHEEP_STARTING_ENERGY,
    WOLF_REPRODUCE,
    WOLF_STARTING_ENERGY,
    GRASS_REGROWTH_TIME,
    ENERGY_FROM_FOOD_WOLF,
    ENERGY_FROM_FOOD_SHEEP,
)


class Animal(CellAgent):
    """The base animal class."""
    def __init__(
        self, 
        model, 
        energy,
        p_reproduce,
        energy_from_food,
        cell=None,
        speed=None,
    ):
        """Initialize an animal.

        Args:
            model: Model instance
            energy: Starting amount of energy
            p_reproduce: Probability of reproduction (asexual)
            energy_from_food: Energy obtained from 1 unit of food
            cell: Cell in which the animal starts
            speed: Number of movement opportunities per timestep
        """
        super().__init__(model)
        self.energy = energy
        self.p_reproduce = p_reproduce
        self.cell = cell
        self.energy_from_food = energy_from_food
        # A missing speed means this is a newly created animal.
        self.speed = model.random.choice((1, 2, 3)) if speed is None else speed
        # Reset at the start of every model timestep.
        self.has_eaten = False
        
    def spawn_offspring(self):
        """Create offspring by splitting energy and creating new instance."""
        # Parent and offspring divide the parent's current energy equally.
        self.energy /= 2
        self.__class__(
            model=self.model,
            energy=self.energy,
            p_reproduce=self.p_reproduce,
            energy_from_food=self.energy_from_food,
            cell=self.cell,
            speed=self.speed,
        )

class Sheep(Animal):
    """A sheep that walks around, reproduces (asexually) and gets eaten."""

    def __init__(
        self,
        model,
        energy=SHEEP_STARTING_ENERGY,
        p_reproduce=SHEEP_REPRODUCE,
        energy_from_food=ENERGY_FROM_FOOD_SHEEP,
        cell=None,
        speed=None,
    ):
        super().__init__(
            model, energy, p_reproduce, energy_from_food, cell, speed
        )

class Wolf(Animal):
    """A wolf that walks around, reproduces (asexually) and eats sheep."""

    def __init__(
        self,
        model,
        energy=WOLF_STARTING_ENERGY,
        p_reproduce=WOLF_REPRODUCE,
        energy_from_food=ENERGY_FROM_FOOD_WOLF,
        cell=None,
        speed=None,
    ):
        super().__init__(
            model, energy, p_reproduce, energy_from_food, cell, speed
        )

class GrassPatch(FixedAgent):
    """A patch of grass that grows at a fixed rate and can be eaten by sheep."""

    def __init__(self, 
                 model, 
                 countdown, 
                 grass_regrowth_time=GRASS_REGROWTH_TIME, 
                 cell=None,
                 food_energy=ENERGY_FROM_FOOD_SHEEP):
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
        self.food_energy = food_energy
        # Regrown grass restores its full food value.
        self.energy = food_energy if self.fully_grown else 0
        self.cell = cell

        # Schedule initial growth if not fully grown
        if not self.fully_grown:
            self.model.schedule_event(self.regrow, after=countdown)

    def regrow(self):
        """Regrow the grass."""
        self.fully_grown = True
        self.energy = self.food_energy

    def get_eaten(self):
        """Mark grass as eaten and schedule regrowth."""
        self.fully_grown = False
        self.energy = 0
        self.model.schedule_event(self.regrow, after=self.grass_regrowth_time)