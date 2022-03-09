from energy_system_optimizer.optimization_frameworks.ortools_wrapper import (
    ORToolsWrapper,
)
from energy_system_optimizer.optimization_frameworks.variable_types import VariableTypes
from energy_system_optimizer.optimization_frameworks.objective_types import (
    ObjectiveTypes,
)


def test_ortools_primer():
    model = ORToolsWrapper("CBC_MIXED_INTEGER_PROGRAMMING")

    x = model.add_variable("x", VariableTypes.continuous)
    y = model.add_variable("y", VariableTypes.continuous)

    model.add_constraint(x + 7 * y <= 17.5, "sum_limit")
    model.add_constraint(x <= 3.5, "x_limit")

    model.set_objective(ObjectiveTypes.maximize, x + 10 * y)

    model.solve()

    res_obj = model.get_objective_value()
    res_x = model.get_result(x)
    res_y = model.get_result(y)

    assert res_obj == 25.0
    assert res_x == 0.0
    assert res_y == 2.5


def test_retrieve_solution_value_of_float_returns_float_itself():
    model = ORToolsWrapper.initialize_cbc()
    x = model.add_continuous_variable("x", 5, 10)
    y = 12

    model.set_objective(ObjectiveTypes.maximize, x * y)

    model.solve()

    assert model.get_result(y), 12
