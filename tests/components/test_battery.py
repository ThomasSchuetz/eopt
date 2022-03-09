import pytest
from energy_system_optimizer.components.battery import Battery

from energy_system_optimizer.optimization_frameworks.ortools_wrapper import (
    ORToolsWrapper,
)
from energy_system_optimizer.optimization_frameworks.objective_types import (
    ObjectiveTypes,
)

from test_utils.time_utils import create_discretization
from test_utils.battery_utils import parameterize_battery


def test_battery_charging_discharing():
    model = ORToolsWrapper.initialize_cbc()
    battery_config = parameterize_battery(
        energy_init=0, energy_max=100, power_max=100, efficiency=0.8
    )
    set_profile = [50, 0, -10]  # positive: charging
    time_steps = range(len(set_profile))
    discretization = create_discretization(time_steps, 1)
    battery = Battery(model, battery_config)

    power_charge, power_discharge, energy, costs_ageing = battery.add_to_model(
        discretization
    )

    for t in time_steps:
        model.add_constraint(
            power_charge[t] - power_discharge[t] == set_profile[t],
            f"fixed_battery_power_{t}",
        )

    model.solve()

    res_energy = [model.get_result(energy[t]) for t in time_steps]

    assert res_energy == pytest.approx([40, 40, 30])


def test_battery_grid_integration():
    model = ORToolsWrapper.initialize_cbc()

    battery_config = parameterize_battery(
        energy_init=90, energy_max=200, power_max=50, efficiency=1
    )
    load = [140, 150, 60]

    expected_battery_power = [-40, -50]
    time_steps = range(len(load))
    discretization = create_discretization(time_steps, 1)

    battery = Battery(model, battery_config)

    power_charge, power_discharge, energy, costs_ageing = battery.add_to_model(
        discretization
    )

    grid_import = {
        t: model.add_continuous_variable(f"grid_import_{t}", 0, 100) for t in time_steps
    }

    for t in time_steps:
        model.add_constraint(
            grid_import[t] + power_discharge[t] == power_charge[t] + load[t],
            f"grid_balance_{t}",
        )

    model.set_objective(ObjectiveTypes.minimize, sum(grid_import.values()))

    model.solve()

    res_grid_import = [model.get_result(grid_import[t]) for t in time_steps]
    res_battery_energy = [model.get_result(energy[t]) for t in time_steps]
    res_battery_power = [
        model.get_result(power_charge[t]) - model.get_result(power_discharge[t])
        for t in time_steps
    ]

    assert res_grid_import == pytest.approx([100, 100, 60])
    assert res_battery_energy == pytest.approx([50, 0, 0])
    assert res_battery_power[: len(expected_battery_power)] == pytest.approx(
        expected_battery_power
    )
