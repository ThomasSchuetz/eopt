from energy_system_optimizer.optimization_frameworks.variable_types import VariableTypes


class Battery:
    def __init__(self, model, static_config):
        self.model = model

        self.id = static_config["id"]
        self.energy_init_kWh = static_config["energy_init_kWh"]
        self.energy_max_kWh = static_config["energy_max_kWh"]
        self.power_max_kW = static_config["power_max_kW"]
        self.efficiency = static_config["efficiency"]

    def add_to_model(self, discretization):
        time_steps = discretization["time_steps"]
        dt_h = discretization["dt_h"]

        variables = self.create_variables(time_steps)
        power_charge, power_discharge, energy, is_charging = variables
        costs_ageing = 0

        for t in time_steps:
            if t == time_steps[0]:
                energy_previous = self.energy_init_kWh
            else:
                energy_previous = energy[t - 1]

            self.model.add_constraint(
                energy[t]
                == energy_previous
                + dt_h * (self.efficiency * power_charge[t] - power_discharge[t]),
                self._get_name(f"energy_balance_{t}"),
            )

        for t in time_steps:
            self.model.add_constraint(
                power_charge[t] <= is_charging[t] * self.power_max_kW,
                self._get_name(f"max_charging_power_{t}"),
            )

        for t in time_steps:
            self.model.add_constraint(
                power_discharge[t] <= (1 - is_charging[t]) * self.power_max_kW,
                self._get_name(f"max_discharging_power_{t}"),
            )

        return power_charge, power_discharge, energy, costs_ageing

    def _get_name(self, postfix: str):
        return f"battery_{id}_{postfix}"

    def create_variables(self, time_steps):
        power_charge = {
            t: self.model.add_continuous_variable(
                self._get_name(f"power_charge_{t}"),
                lb=0.0,
                ub=self.power_max_kW,
            )
            for t in time_steps
        }

        power_discharge = {
            t: self.model.add_continuous_variable(
                self._get_name(f"power_discharge_{t}"),
                lb=0.0,
                ub=self.power_max_kW,
            )
            for t in time_steps
        }

        energy = {
            t: self.model.add_continuous_variable(
                self._get_name(f"energy_{t}"),
                lb=0.0,
                ub=self.energy_max_kWh,
            )
            for t in time_steps
        }

        is_charging = {
            t: self.model.add_binary_variable(self._get_name(f"is_charging_{t}"))
            for t in time_steps
        }

        return power_charge, power_discharge, energy, is_charging
