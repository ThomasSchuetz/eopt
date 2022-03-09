import pytest
from energy_system_optimizer.components.battery import Battery
from energy_system_optimizer.components.battery_degradation_decorator import \
    BatteryDegradationDecorator
from energy_system_optimizer.optimization_frameworks.objective_types import \
    ObjectiveTypes
from energy_system_optimizer.optimization_frameworks.ortools_wrapper import \
    ORToolsWrapper

from test_utils.battery_utils import parameterize_battery
from test_utils.time_utils import create_discretization


def test_battery_degradation_leads_to_positive_degradation_costs():
    model = ORToolsWrapper.initialize_cbc()
    battery_config = parameterize_battery(
        energy_init=0, energy_max=100, power_max=100, efficiency=1, costs_per_full_cycle=1
    )
    set_profile = [100, -100, 50]  # positive: charging
    time_steps = range(len(set_profile))
    discretization = create_discretization(time_steps, 1)
    base_battery = Battery(model, battery_config)
    battery = BatteryDegradationDecorator(model, battery_config, base_battery)

    power_charge, power_discharge, energy, costs_ageing = battery.add_to_model(
        discretization
    )

    for t in time_steps:
        model.add_constraint(
            power_charge[t] - power_discharge[t] == set_profile[t],
            f"fixed_battery_power_{t}",
        )

    model.solve()

    res_costs_ageing = model.get_result(costs_ageing)

    assert res_costs_ageing == pytest.approx(1.5)