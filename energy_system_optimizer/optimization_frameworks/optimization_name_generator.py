class OptimizationNameGenerator:
    def __init__(self, type_of_component: str, id: int):
        self.type = type_of_component
        self.id = id

    def get_name(self, postfix: str):
        return f"{self.type}_{self.id}_{postfix}"
