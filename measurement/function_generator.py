from math import sin, pi
from traits.api import cached_property, Callable, Enum, Float, HasTraits, Int, Property

FUNCTIONS = {"sin": sin}


class FunctionGenerator(HasTraits):
    """ Generator of Functions
    """
    function_name = Enum(*(FUNCTIONS.keys()))
    function_factory = Property(Callable, depends_on='function_name')
    current_index = Int
    rate = Float(pi/10)

    @cached_property
    def _get_function_factory(self):
        return FUNCTIONS[self.function_name]

    def get_new_value(self):
        new_value = self.function_factory(self.current_index)
        self.current_index += 1
        return new_value

    def reset_index(self):
        self.current_index = 0