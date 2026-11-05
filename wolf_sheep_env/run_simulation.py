"""Run the wolf-sheep model without starting the visualization."""

from pathlib import Path

import matplotlib.pyplot as plt

from model import WolfSheep


def main():
    model = WolfSheep()
    for _ in range(10000):
        model.step()

    data = model.datacollector.get_model_vars_dataframe()
    output_dir = Path(__file__).with_name("simulation_output")
    output_dir.mkdir(exist_ok=True)

    plots = {
        "population": {
            "columns": ["Wolves", "Sheep", "Grass"],
            "colors": ["tab:orange", "tab:cyan", "tab:green"],
            "title": "Population",
        },
        "energy": {
            "columns": [
                "Wolves total energy",
                "Sheep total energy",
                "Grass energy",
            ],
            "colors": ["tab:red", "tab:blue", "tab:green"],
            "title": "Total Energy",
        },
        "average_energy": {
            "columns": ["Wolves average energy", "Sheep average energy"],
            "colors": ["tab:red", "tab:blue"],
            "title": "Average Animal Energy",
        },
        "speed_distribution": {
            "columns": [
                "Sheep speed 1",
                "Sheep speed 2",
                "Sheep speed 3",
                "Wolves speed 1",
                "Wolves speed 2",
                "Wolves speed 3",
            ],
            "colors": [
                "lightblue",
                "deepskyblue",
                "darkblue",
                "lightcoral",
                "red",
                "darkred",
            ],
            "title": "Speed Distribution",
        },
    }

    for name, plot in plots.items():
        figure, axis = plt.subplots()
        data[plot["columns"]].plot(ax=axis, color=plot["colors"])
        axis.set_title(plot["title"])
        axis.set_xlabel("Timestep")
        axis.legend(loc="center left", bbox_to_anchor=(1, 0.9))
        figure.tight_layout()
        figure.savefig(output_dir / f"{name}.png")
        plt.close(figure)

    print(data.tail())
    print(f"Graphs saved to {output_dir}")


if __name__ == "__main__":
    main()
