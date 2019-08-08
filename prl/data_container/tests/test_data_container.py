from unittest import TestCase
import numpy as np
from numpy.testing import assert_allclose
from traits.testing.api import UnittestTools
from prl.data_container import CurveData


class TestCurveData(TestCase, UnittestTools):
    def test_create_blank(self):
        curve = CurveData.create_blank()
        assert_allclose(curve.data, np.zeros(1024))

    def test_append(self):
        curve = CurveData.create_blank()
        for i in range(1024):
            curve.append(i)
        assert_allclose(curve.data, np.arange(1024))

    def test_update_event(self):
        curve = CurveData.create_blank()
        with self.assertTraitChanges(curve, 'updated', count=100):
            for i in range(100):
                curve.append(i)
