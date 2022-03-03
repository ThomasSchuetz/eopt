import pytest
from energy_system_optimizer.components.battery import Battery

from energy_system_optimizer.optimization_frameworks.ortools_wrapper import (
    ORToolsWrapper,
)
from energy_system_optimizer.optimization_frameworks.variable_types import VariableTypes
from energy_system_optimizer.optimization_frameworks.objective_types import (
    ObjectiveTypes,
)


def test_basic_battery():

    model = ORToolsWrapper("CBC_MIXED_INTEGER_PROGRAMMING")

    load = [140, 150, 60]
    battery_config = {
        "id": 1,
        "energy_init_kWh": 90,
        "energy_max_kWh": 200,
        "power_max_kW": 50,
        "efficiency": 1,
    }
    expected_battery_power = [-40, -50]
    time_steps = range(len(load))
    discretization = {"time_steps": time_steps, "dt_h": 1}

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

    model.set_objective(ObjectiveTypes.minimize, model.sum(grid_import))

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
