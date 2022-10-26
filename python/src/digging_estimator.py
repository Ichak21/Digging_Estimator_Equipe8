import math
from enum import Enum


def average_per_day(tunnel_length: int, digging_days: int):
    return math.floor(tunnel_length / digging_days)


class Shift(Enum):
    NIGHT = 0
    DAY = 1


class TunnelTooLongForDelayException(Exception):
    pass


class InvalidFormatException(Exception):
    pass


class RockAPIError(Exception):
    Exception("Does not work in test mode")


class GoblinAPIError(Exception):
    Exception("Does not work in test mode")


class Team:
    miners: int
    healers: int
    smithies: int
    lighters: int
    inn_keepers: int
    guards: int
    guard_managers: int
    washers: int
    protectors: int
    for_guards_count: int
    for_washers_count: int
    for_inn_keeper_count: int
    for_guards_manager_count: int

    def __init__(self):
        self.miners = 0
        self.healers = 0
        self.smithies = 0
        self.lighters = 0
        self.inn_keepers = 0
        self.guards = 0
        self.guard_managers = 0
        self.washers = 0
        self.protectors = 0
        self.for_inn_keeper_count = 0
        self.for_washers_count = 0
        self.for_guards_count = 0
        self.for_guards_manager_count = 0

    def update_counts(self):
        self.for_inn_keeper_count = self.miners + self.healers + \
            self.smithies + self.lighters + self.protectors

        self.for_washers_count = self.miners + self.healers + self.smithies + \
            self.inn_keepers + self.lighters + self.guards + \
            self.guard_managers + self.protectors

        self.for_guards_count = self.healers + self.miners + \
            self.smithies + self.lighters + self.washers

        self.for_guards_manager_count: int = self.guards

        return self

    def set_inn_keepers(self):
        self.update_counts()
        self.inn_keepers = math.ceil((self.for_inn_keeper_count) / 4.0) * 4

        return self

    def set_washers(self):
        self.update_counts()
        self.washers = math.ceil(self.for_washers_count / 10.0)

        return self

    def night_updater_for_all_guard_and_washer(self):
        previous_washers: int = 0
        previous_guards: int = 0
        previous_guard_manager: int = 0

        while not (previous_washers == self.washers and previous_guards == self.guards and previous_guard_manager == self.guard_managers):

            previous_washers: int = self.washers
            previous_guards: int = self.guards
            previous_guard_manager: int = self.guard_managers

            self.update_counts()

            self.washers = math.ceil(self.for_washers_count / 10.0)
            self.guards = math.ceil(self.for_guards_count / 3.0)
            self.guard_managers = math.ceil(
                self.for_guards_manager_count / 3.0)

        return self

    def get_head_count(self):
        return self.miners + self.washers + self.healers + self.smithies + self.inn_keepers + self.guards + self.guard_managers + self.lighters


class TeamComposition:
    MINER_INCREMENTOR: int = 1

    def __init__(self):
        self.day_team: Team = Team()
        self.night_team: Team = Team()
        self.head_count: int = 0

    def update_head_count(self):
        self.head_count = self.day_team.get_head_count() + self.night_team.get_head_count()

    def get_head_count(self):
        return self.head_count

    def define_miners_needed(self, distances_per_dwarf_numbers: int, tunnel_length: int, digging_days: int, max_dig_per_shift: int):
        for dig_distance in range(0, len(distances_per_dwarf_numbers) - 1):
            if distances_per_dwarf_numbers[dig_distance] < average_per_day(tunnel_length, digging_days):
                self.day_team.miners += self.MINER_INCREMENTOR

            if distances_per_dwarf_numbers[dig_distance] + max_dig_per_shift < average_per_day(tunnel_length, digging_days):
                self.night_team.miners += self.MINER_INCREMENTOR

        return self

    def day_shift_handling(self, local_risk: bool):
        day_shift: Team = self.day_team

        if day_shift.miners > 0:
            day_shift.healers += 1
            day_shift.smithies += 2

            if local_risk:
                day_shift.protectors += 2

            day_shift.set_inn_keepers()
            day_shift.set_washers()

        self.update_head_count()
        return self

    def night_shift_handling(self, local_risk: bool):
        night_shift: Team = self.night_team

        if night_shift.miners > 0:
            night_shift.healers += 1
            night_shift.smithies += 2
            night_shift.lighters = night_shift.miners + 1

            if local_risk:
                night_shift.protectors += 2
                night_shift.lighters += 2

            night_shift.set_inn_keepers()
            night_shift.set_washers()
            night_shift.night_updater_for_all_guard_and_washer()

        self.update_head_count()
        return self


class DiggingEstimator:
    MAX_ROTATION: int = 2
    LIMIT_LENGTH: int = 0
    LIMIT_DAYS: int = 0
    LOCAL_AREA: str

    def __init__(self, local_area: str = ""):
        self.LOCAL_AREA = local_area

    def digging_project_is_possible(self, tunnel_length, digging_days, max_dig_per_days: int):
        if not(isinstance(tunnel_length, int) and tunnel_length > 0 and isinstance(digging_days, int) and digging_days > 0):
            raise InvalidFormatException()

        if math.floor(tunnel_length / digging_days) > max_dig_per_days:
            raise TunnelTooLongForDelayException()

    def capacity_calculate(self, rock_type: str):
        dig_per_dwarf_numbers: list = self.get_dig_speed(rock_type)
        max_dig_per_shift: float = dig_per_dwarf_numbers[len(
            dig_per_dwarf_numbers) - 1]
        max_dig_per_days: float = self.MAX_ROTATION * max_dig_per_shift

        return [dig_per_dwarf_numbers, max_dig_per_shift, max_dig_per_days]

    def tunnel(self, tunnel_length, digging_days, rock_type):

        distances_per_dwarf_numbers: list = self.capacity_calculate(rock_type)[
            0]
        max_dig_per_shift: int = self.capacity_calculate(rock_type)[1]
        max_dig_per_day: int = self.capacity_calculate(rock_type)[2]

        self.digging_project_is_possible(
            tunnel_length, digging_days, max_dig_per_day)

        composition_for_project: TeamComposition = TeamComposition()
        composition_for_project.define_miners_needed(
            distances_per_dwarf_numbers, tunnel_length, digging_days, max_dig_per_shift)

        local_risk: bool = self.get_goblin_risk()
        composition_for_project.day_shift_handling(local_risk)
        composition_for_project.night_shift_handling(local_risk)

        return composition_for_project

    def get_dig_speed(self, rock_type: str):
        # for example for granite it returns [0, 3, 5.5, 7]
        # if you put 0 dwarf, you dig 0m / d / team
        # if you put 1 dwarf, you dig 3m / d / team
        # 2 dwarves = 5.5 m / d / team
        # so a day team on 2 miners and a night team of 1 miner dig 8.5 m / d
        url = "dtp://research.vin.co/digging-rate/" + rock_type
        print("Trying to fetch" + url)
        raise RockAPIError

    def get_goblin_risk(self):
        risk = self._call_api_goblin(self.LOCAL_AREA)

        if risk == True:
            return True
        else:
            return False

    def _call_api_goblin(self, local_area: str):
        response = "dtp://research.vin.co/are-there-goblins/" + local_area
        raise GoblinAPIError
        return response
