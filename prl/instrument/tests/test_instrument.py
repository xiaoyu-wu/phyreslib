from unittest import TestCase
import numpy as np
from numpy.testing import assert_array_almost_equal
from prl.instrument import MockupInstrument

class TestMockupInstrument(TestCase):
    def test_func_gen(self):
        mui = MockupInstrument()
        time_series = np.arange(100)
        read_results = [
            mui.read("some_value") for i in time_series
        ]
        expected = np.sin(np.pi / 100 * time_series)
        assert_array_almost_equal(read_results, expected)
