from unittest.mock import patch

import pytest

from agents import GrassPatch, Sheep, Wolf
from model import WolfSheep, WolfSheepScenario
from parameters import ENERGY_COST_PER_STEP


def make_model(**overrides):
    scenario = WolfSheepScenario()
    for name, value in overrides.items():
        setattr(scenario, name, value)
    return WolfSheep(scenario)


def test_speed_is_inherited_by_offspring():
    model = make_model(
        width=3,
        height=3,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    parent = Sheep(model, energy=240, speed=3, cell=model.grid[(1, 1)])

    parent.spawn_offspring()

    offspring = [
        animal
        for animal in model.agents_by_type[Sheep]
        if animal is not parent
    ][0]
    assert offspring.speed == 3


def test_speed_schedule_and_moore_wrapping():
    model = make_model(
        width=3,
        height=3,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    animals = [
        Sheep(model, speed=speed, cell=model.grid[(0, 0)])
        for speed in (1, 2, 3)
    ]

    with patch.object(model.random, "choice", return_value=(1, 1)):
        model._move_round(animals, 1)
    assert [animal.cell.coordinate for animal in animals] == [
        (0, 0),
        (0, 0),
        (1, 1),
    ]

    with patch.object(model.random, "choice", return_value=(1, 1)):
        model._move_round(animals, 2)
    assert [animal.cell.coordinate for animal in animals] == [
        (0, 0),
        (1, 1),
        (2, 2),
    ]

    with patch.object(model.random, "choice", return_value=(1, 1)):
        model._move_round(animals, 3)
    assert [animal.cell.coordinate for animal in animals] == [
        (1, 1),
        (2, 2),
        (0, 0),
    ]


def test_shared_grass_is_consumed_once():
    model = make_model(
        width=1,
        height=1,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    cell = model.grid[(0, 0)]
    grass = GrassPatch(model, 0, cell=cell, food_energy=30)
    sheep = [
        Sheep(model, energy=100, cell=cell, speed=1),
        Sheep(model, energy=100, cell=cell, speed=3),
    ]

    model._resolve_interactions()

    assert [animal.energy for animal in sheep] == [115, 115]
    assert not grass.fully_grown
    assert all(animal.has_eaten for animal in sheep)


def test_initial_grass_patches_use_distinct_random_cells():
    model = make_model(
        width=4,
        height=4,
        initial_sheep=0,
        initial_wolves=0,
        initial_grass_patches=7,
        grass=True,
    )
    grass_cells = [
        patch.cell.coordinate
        for patch in model.agents_by_type[GrassPatch]
    ]

    assert len(grass_cells) == 7
    assert len(set(grass_cells)) == 7


def test_random_seed_is_used_by_default():
    first = make_model(initial_sheep=5, initial_wolves=2, grass=False)
    second = make_model(initial_sheep=5, initial_wolves=2, grass=False)

    assert [
        animal.cell.coordinate
        for animal in first.agents
        if isinstance(animal, (Sheep, Wolf))
    ] == [
        animal.cell.coordinate
        for animal in second.agents
        if isinstance(animal, (Sheep, Wolf))
    ]


def test_invalid_scenario_timing_is_rejected():
    with pytest.raises(ValueError, match="grass_regrowth_time"):
        make_model(grass_regrowth_time=0)
    with pytest.raises(ValueError, match="initial_grass_patches"):
        make_model(grass=False, initial_grass_patches=-1)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("sheep_reproduce", -0.1),
        ("wolf_reproduce", 1.1),
        ("sheep_starting_energy", -1),
        ("energy_from_food_wolf", -1),
        ("energy_cost_per_step", -1),
        ("min_energy_to_reproduce", -1),
    ],
)
def test_invalid_energy_and_reproduction_values_are_rejected(name, value):
    with pytest.raises(ValueError):
        make_model(**{name: value})


def test_grass_reporters_exist_when_grass_is_disabled():
    model = make_model(grass=False)
    data = model.datacollector.get_model_vars_dataframe().iloc[0]

    assert data["Grass"] == 0
    assert data["Grass energy"] == 0


def test_scenario_controls_agent_energy_parameters():
    model = make_model(
        initial_sheep=1,
        initial_wolves=1,
        sheep_starting_energy=12,
        wolf_starting_energy=34,
        energy_from_food_sheep=56,
        energy_from_food_wolf=7,
        energy_cost_per_step=3,
        min_energy_to_reproduce=88,
        grass=False,
    )

    sheep = next(iter(model.agents_by_type[Sheep]))
    wolf = next(iter(model.agents_by_type[Wolf]))
    assert sheep.energy == 12
    assert wolf.energy == 34
    assert sheep.energy_from_food == 56
    assert wolf.energy_from_food == 7
    assert model.energy_cost_per_step == 3
    assert model.min_energy_to_reproduce == 88


def test_shared_predation_consumes_one_sheep_once():
    model = make_model(
        width=1,
        height=1,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    cell = model.grid[(0, 0)]
    sheep = Sheep(model, energy=60, cell=cell, speed=1)
    wolves = [
        Wolf(model, energy=100, energy_from_food=20, cell=cell, speed=1),
        Wolf(model, energy=100, energy_from_food=20, cell=cell, speed=3),
        Wolf(model, energy=100, energy_from_food=20, cell=cell, speed=2),
    ]

    model._resolve_interactions()

    assert sheep.cell is None
    assert [animal.energy for animal in wolves] == pytest.approx(
        [106.66666666666667] * 3
    )
    assert all(animal.has_eaten for animal in wolves)


def test_predation_assigns_distinct_sheep_to_each_wolf():
    model = make_model(
        width=1,
        height=1,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    cell = model.grid[(0, 0)]
    sheep = [
        Sheep(model, energy=60, cell=cell, speed=1),
        Sheep(model, energy=80, cell=cell, speed=1),
    ]
    wolves = [
        Wolf(model, energy=100, energy_from_food=20, cell=cell, speed=1),
        Wolf(model, energy=100, energy_from_food=20, cell=cell, speed=1),
    ]

    model._resolve_interactions()

    assert sheep[0].cell is None
    assert sheep[1].cell is None
    assert sorted(animal.energy for animal in wolves) == [120, 120]
    assert all(animal.has_eaten for animal in wolves)


def test_scarce_predation_shares_all_sheep_energy():
    model = make_model(
        width=1,
        height=1,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    cell = model.grid[(0, 0)]
    sheep = [
        Sheep(model, energy=60, cell=cell, speed=1),
        Sheep(model, energy=80, cell=cell, speed=1),
    ]
    wolves = [
        Wolf(model, energy=100, energy_from_food=20, cell=cell, speed=1)
        for _ in range(3)
    ]

    model._resolve_interactions()

    assert all(animal.cell is None for animal in sheep)
    assert [animal.energy for animal in wolves] == pytest.approx(
        [113.33333333333333] * 3
    )
    assert all(animal.has_eaten for animal in wolves)


def test_scarce_predation_uses_sheep_to_wolf_ratio():
    model = make_model(
        width=1,
        height=1,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    cell = model.grid[(0, 0)]
    sheep = Sheep(model, energy=60, cell=cell, speed=1)
    wolves = [
        Wolf(model, energy=100, energy_from_food=30, cell=cell, speed=1)
        for _ in range(4)
    ]

    model._resolve_interactions()

    expected_energy = 100 + (1 * 30 / 4)
    assert [animal.energy for animal in wolves] == pytest.approx(
        [expected_energy] * 4
    )
    assert sheep.cell is None


def test_energy_cost_is_paid_once_per_timestep():
    model = make_model(
        width=1,
        height=1,
        initial_sheep=0,
        initial_wolves=0,
        grass=False,
    )
    sheep = Sheep(model, energy=100, cell=model.grid[(0, 0)], speed=3)

    model.step()

    assert sheep.energy == 100 - ENERGY_COST_PER_STEP


def test_speed_distribution_reporters_exist():
    model = make_model(
        width=2,
        height=2,
        initial_sheep=4,
        initial_wolves=4,
        grass=False,
    )
    data = model.datacollector.get_model_vars_dataframe().iloc[0]

    for species in ("Sheep", "Wolves"):
        for speed in (1, 2, 3):
            assert f"{species} speed {speed}" in data


def test_initial_wolves_include_every_speed_group():
    model = make_model(
        initial_sheep=0,
        initial_wolves=3,
        grass=False,
    )

    speeds = {
        wolf.speed
        for wolf in model.agents_by_type[Wolf]
    }

    assert speeds == {1, 2, 3}
