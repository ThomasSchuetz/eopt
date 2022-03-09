from energy_system_optimizer.optimization_frameworks.optimization_name_generator import (
    OptimizationNameGenerator,
)


class BatteryDegradationDecorator:
    def __init__(self, model, static_config, base_battery):
        self.model = model

        self.energy_max_kWh = static_config["energy_max_kWh"]
        self.costs_per_full_cycle = static_config["costs_per_full_cycle"]

        self.base_battery = base_battery
        self._get_name = OptimizationNameGenerator(
            "battery", static_config["id"]
        ).get_name

    def add_to_model(self, discretization):
        # Note: base_battery is supposed to NOT define any degradation costs!
        # Otherwise, there would be some variables defined multiple times and
        # some equations could contradict themselves
        power_charge, power_discharge, energy, _ = self.base_battery.add_to_model(
            discretization
        )

        costs_degradation = self.model.add_continuous_variable(
            self._get_name("costs_degradation"), lb=0.0
        )

        dt_h = discretization["dt_h"]
        full_cycles = dt_h / self.energy_max_kWh * sum(power_charge.values())

        self.model.add_constraint(
            self.costs_per_full_cycle * full_cycles == costs_degradation,
            self._get_name("cost_degradation_definition"),
        )

        return power_charge, power_discharge, energy, costs_degradation
