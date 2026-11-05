from agents import GrassPatch, Sheep, Wolf
from model import WolfSheep, WolfSheepScenario
from mesa.visualization import (
    CommandConsole,
    SolaraViz,
    SpaceRenderer,
    make_plot_component,
)
from mesa.visualization.components import AgentPortrayalStyle


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
    elif isinstance(agent, GrassPatch):
        if agent.fully_grown:
            portrayal.update(("color", "tab:green"))
        else:
            portrayal.update(("color", "tab:brown"))
        portrayal.update(("marker", "s"), ("size", 125), ("zorder", 1))

    return portrayal


model_params = {}


def post_process_space(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def post_process_lines(ax):
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.9))


lineplot_component = make_plot_component(
    {"Wolves": "tab:orange", "Sheep": "tab:cyan", "Grass": "tab:green"},
    post_process=post_process_lines,
)

energy_plot_component = make_plot_component(
    {
        "Wolves total energy": "tab:red",
        "Sheep total energy": "tab:blue",
        "Grass energy": "tab:green",
    },
    post_process=post_process_lines,
)

average_energy_plot_component = make_plot_component(
    {
        "Wolves average energy": "tab:red",
        "Sheep average energy": "tab:blue",
    },
    post_process=post_process_lines,
)

speed_plot_component = make_plot_component(
    {
        "Sheep speed 1": "lightblue",
        "Sheep speed 2": "deepskyblue",
        "Sheep speed 3": "darkblue",
        "Wolves speed 1": "lightcoral",
        "Wolves speed 2": "red",
        "Wolves speed 3": "darkred",
    },
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
    components=[
        lineplot_component,
        energy_plot_component,
        average_energy_plot_component,
        speed_plot_component,
        CommandConsole,
    ],
    model_params=model_params,
    play_interval=250,
    render_interval=5,
    name="Wolf Sheep",
)
page  # noqa