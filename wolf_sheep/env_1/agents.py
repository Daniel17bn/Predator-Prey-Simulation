from mesa.discrete_space import CellAgent

from parameters import (
    ENERGY_COST_PER_STEP,
    SHEEP_REPRODUCE,
    SHEEP_STARTING_ENERGY,
    WOLF_REPRODUCE,
    WOLF_STARTING_ENERGY,
)


class Animal(CellAgent):
    """The base animal class."""
    def __init__(
        self, 
        model, 
        energy,
        p_reproduce,
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

    def spawn_offspring(self):
        """Create offspring. """
        self.__class__(
            self.model,
            p_reproduce=self.p_reproduce,
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
        if self.energy < 0:
            self.remove()
        elif self.random.random() < self.p_reproduce:
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
        cell=None,
    ):
        super().__init__(model, energy, p_reproduce, cell)


class Wolf(Animal):
    """A wolf that walks around, reproduces (asexually) and eats sheep."""

    def __init__(
        self,
        model,
        energy=WOLF_STARTING_ENERGY,
        p_reproduce=WOLF_REPRODUCE,
        cell=None,
    ):
        super().__init__(model, energy, p_reproduce,cell)
        self.initial_energy = WOLF_STARTING_ENERGY

    def feed(self):
        """If possible, eat a sheep at current location."""
        sheeps = [obj for obj in self.cell.agents if isinstance(obj, Sheep)]
        if sheeps:
            for sheep in sheeps:
                sheep.remove()
            # Reset energy to initial value after eating a sheep
            self.energy = self.initial_energy
