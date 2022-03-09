from energy_system_optimizer.optimization_frameworks.optimization_name_generator import OptimizationNameGenerator


def test_name_generator_produces_reasonable_name():
    any_component = "anyComponent"
    any_id = 123
    any_postfix = "variable_987"

    generator = OptimizationNameGenerator(any_component, any_id)
    
    name = generator.get_name(any_postfix)

    assert any_component in name
    assert str(any_id) in name
    assert any_postfix in name