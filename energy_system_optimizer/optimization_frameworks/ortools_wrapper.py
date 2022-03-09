from energy_system_optimizer.optimization_frameworks.variable_types import VariableTypes
from energy_system_optimizer.optimization_frameworks.objective_types import ObjectiveTypes
from ortools.linear_solver import pywraplp


class ORToolsWrapper:
    def __init__(self, solver):
        self.model = pywraplp.Solver.CreateSolver(solver)

    @staticmethod
    def initialize_cbc():
        return ORToolsWrapper("CBC_MIXED_INTEGER_PROGRAMMING")

    def add_variable(self, name, type=VariableTypes.continuous, lb=None, ub=None):
        if type == VariableTypes.binary:
            variable = self.model.BoolVar(name)
        elif type == VariableTypes.continuous:
            if lb is None:
                lb = 0.0
            if ub is None:
                ub = self.model.Infinity()
            variable = self.model.NumVar(lb, ub, name)
        return variable
    
    def add_binary_variable(self, name):
        return self.add_variable(name, VariableTypes.binary)
    def add_continuous_variable(self, name, lb=None, ub=None):
        return self.add_variable(name, VariableTypes.continuous, lb, ub)

    def add_constraint(self, constraint, name):
        self.model.Add(constraint, name)

    def set_objective(self, type, objective):
        if type == ObjectiveTypes.minimize:
            self.model.Minimize(objective)
        elif type == ObjectiveTypes.maximize:
            self.model.Maximize(objective)
        else:
            raise ValueError(f"Unknown objective type: {type}")

    def solve(self):
        self.model.Solve()

    def get_result(self, variable):
        if isinstance(variable, pywraplp.Variable):
            return variable.solution_value()
        else:
            return variable

    def get_objective_value(self):
        return self.model.Objective().Value()
