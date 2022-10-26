from logging import exception
from tokenize import Triple
from unittest.mock import MagicMock
import pytest
from src.digging_estimator import TunnelTooLongForDelayException
from src.digging_estimator import InvalidFormatException
from src.digging_estimator import RockAPIError
from src.digging_estimator import GoblinAPIError
from src.digging_estimator import DiggingEstimator


def test_should_be_Exception_From_Rock_API():
    dig_estimator_tested = DiggingEstimator()

    with pytest.raises(RockAPIError):
        dig_estimator_tested.tunnel(28, 2, "granite")


def test_should_be_Exception_From_Goblin_API():
    dig_estimator_tested = DiggingEstimator("stormwind")
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])

    with pytest.raises(GoblinAPIError):
        dig_estimator_tested.tunnel(28, 2, "granite")


def test_should_be_Exception_format_for_input():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    with pytest.raises(InvalidFormatException):
        dig_estimator_tested.tunnel(5.5, 2, "granite")


def test_should_be_Exception_tunnel_too_long():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    with pytest.raises(TunnelTooLongForDelayException):
        dig_estimator_tested.tunnel(100, 2, "granite")


def test_1dwarve_should_dig_3m_by_day_in_granite():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(3, 1, "granite")

    assert nb_dwarves_needed.day_team.miners == 1


def test_1shift_1dwarve_should_9_total_dwarves():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(3, 1, "granite")

    assert nb_dwarves_needed.head_count == 9


def test_3dwarve_should_dig_7m_by_day_in_granite():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(7, 1, "granite")

    assert nb_dwarves_needed.day_team.miners == 3


def test_should_be_48_dwarves_for_2days_28_meters():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.head_count == 48


def test_possible_to_have_2shift_in_one_day():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(11, 1, "granite")

    assert nb_dwarves_needed.day_team.miners > 0
    assert nb_dwarves_needed.night_team.miners > 0


def test_we_must_have_2_smithies_by_shift():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(21, 2, "granite")

    assert nb_dwarves_needed.day_team.smithies == 2
    assert nb_dwarves_needed.night_team.smithies == 2


def test_we_must_have_1_healers_by_shift():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(14, 1, "granite")

    assert nb_dwarves_needed.day_team.healers == 1
    assert nb_dwarves_needed.night_team.healers == 1


def test_we_must_have_1_lighter_by_miners_and_1_lighter_for_camp_for_nightshift():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(17, 2, "granite")

    assert nb_dwarves_needed.day_team.lighters == 0
    assert nb_dwarves_needed.night_team.lighters == nb_dwarves_needed.night_team.miners+1


def test_we_must_have_1_innkeepers_by_4_dwaves_in_miners_smithies_healers_lighters():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.day_team.inn_keepers + \
        nb_dwarves_needed.night_team.inn_keepers == 20


def test_we_must_have_1_guards_by_3_dwaves_exclude_innkeeper():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.day_team.guards + \
        nb_dwarves_needed.night_team.guards == 5


def test_we_must_have_1_guardsManager_by_3_guards():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.day_team.guard_managers + \
        nb_dwarves_needed.night_team.guard_managers == 2


def test_we_must_have_1_washer_by_10_dwarves():
    dig_estimator_tested = DiggingEstimator()
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.day_team.washers + \
        nb_dwarves_needed.night_team.washers == 5


def test_should_be_True_if_area_is_risky():
    dig_estimator_tested = DiggingEstimator("risky_area")
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=True)

    assert dig_estimator_tested.get_goblin_risk() == True


def test_should_be_False_if_area_is_safe():
    dig_estimator_tested = DiggingEstimator("safe_area")
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=False)

    assert dig_estimator_tested.get_goblin_risk() == False


def test_should_be_2protectors_by_shift_if_there_are_risk():
    dig_estimator_tested = DiggingEstimator("risky_area")
    dig_estimator_tested.get_dig_speed = MagicMock(return_value=[0, 3, 5.5, 7])
    dig_estimator_tested._call_api_goblin = MagicMock(return_value=True)

    nb_dwarves_needed = dig_estimator_tested.tunnel(28, 2, "granite")

    assert nb_dwarves_needed.day_team.protectors == 2
    assert nb_dwarves_needed.night_team.protectors == 2
