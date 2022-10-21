from unittest.mock import MagicMock
import pytest
from src.digging_estimator import DiggingEstimator



def test_should_be_Exception_From_Rock_API():
    dig_estimator_tested = DiggingEstimator()
    with pytest.raises(Exception):
        dig_estimator_tested.tunnel(28, 2, "granite")

def test_should_be_48_for_2days_28_meters():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get = MagicMock(return_value = [0, 3, 5.5, 7])

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.total == 48
