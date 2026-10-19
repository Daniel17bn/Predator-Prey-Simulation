from mesa.discrete_space import CellAgent


class Animal(CellAgent):
    """The base animal class."""
    # Deafult parameters for all animals (can be overridden in subclasses)
    def __init__(
        self, 
        model, 
        energy=8, 
        p_reproduce=0.04, 
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
            self.energy,
            self.p_reproduce,
            self.cell,
        )

    def step(self):
        """Execute one step of the animal's behavior."""
        # Move to random neighboring cell
        self.move()

        # Allow animal subclasses to gain energy from food
        self.feed()

        # Decrease energy each step
        self.energy -= 1

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
        energy=100,
        p_reproduce=0.04,
        cell=None,
    ):
        super().__init__(model, energy, p_reproduce, cell)


class Wolf(Animal):
    """A wolf that walks around, reproduces (asexually) and eats sheep."""

    def __init__(
        self,
        model,
        energy=100,
        p_reproduce=0.04,
        cell=None,
    ):
        super().__init__(model, energy, p_reproduce,cell)
        self.initial_energy = energy 

    def feed(self):
        """If possible, eat a sheep at current location."""
        sheeps = [obj for obj in self.cell.agents if isinstance(obj, Sheep)]
        if sheeps:
            for sheep in sheeps:
                sheep.remove()
            # Reset energy to initial value after eating a sheep
            self.energy = self.initial_energy


