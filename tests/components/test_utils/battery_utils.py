def parameterize_battery(
    id=1, energy_init=50, energy_max=100, power_max=100, efficiency=0.9, **other_args
):
    return dict(
        id=id,
        energy_init_kWh=energy_init,
        energy_max_kWh=energy_max,
        power_max_kW=power_max,
        efficiency=efficiency,
        **other_args
    )
