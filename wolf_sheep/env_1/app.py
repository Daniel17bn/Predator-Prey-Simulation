from agents import Sheep, Wolf
from model import WolfSheep, WolfSheepScenario
from mesa.visualization import (
    CommandConsole,
    Slider,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle
from parameters import (
    INITIAL_SHEEP,
    INITIAL_WOLVES,
    RANDOM_SEED,
    REPRODUCE_MAX,
    REPRODUCE_MIN,
    REPRODUCE_STEP,
    SHEEP_POPULATION_MAX,
    SHEEP_POPULATION_MIN,
    SHEEP_REPRODUCE,
    WOLF_POPULATION_MAX,
    WOLF_POPULATION_MIN,
    WOLF_REPRODUCE,
)


def wolf_sheep_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(
        size=50,
        marker="o",
        zorder=2,
    )

    if isinstance(agent, Wolf):
        portrayal.update(("color", "red"))
    elif isinstance(agent, Sheep):
        portrayal.update(("color", "cyan"))

    return portrayal


model_params = {
    "rng": {
        "type": "InputText",
        "value": RANDOM_SEED,
        "label": "Random Seed",
    },
    "initial_sheep": Slider(
        "Initial Sheep Population",
        INITIAL_SHEEP,
        SHEEP_POPULATION_MIN,
        SHEEP_POPULATION_MAX,
    ),
    "sheep_reproduce": Slider(
        "Sheep Reproduction Rate",
        SHEEP_REPRODUCE,
        REPRODUCE_MIN,
        REPRODUCE_MAX,
        REPRODUCE_STEP,
    ),
    "initial_wolves": Slider(
        "Initial Wolf Population",
        INITIAL_WOLVES,
        WOLF_POPULATION_MIN,
        WOLF_POPULATION_MAX,
    ),
    "wolf_reproduce": Slider(
        "Wolf Reproduction Rate",
        WOLF_REPRODUCE,
        REPRODUCE_MIN,
        REPRODUCE_MAX,
        REPRODUCE_STEP,
    )
}


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))


lineplot_component = make_plot_component(
    {"Wolves": "tab:orange", "Sheep": "tab:cyan"},
    post_process=post_process_lines,
)

model = WolfSheep(scenario=WolfSheepScenario())

renderer = SpaceRenderer(
    model,
    backend="matplotlib",
).setup_agents(wolf_sheep_portrayal)
renderer.post_process = post_process_space
renderer.draw_agents()

page = SolaraViz(
    model,
    renderer,
    components=[lineplot_component, CommandConsole],
    model_params=model_params,
    name="Wolf Sheep",
)
page  # noqa
