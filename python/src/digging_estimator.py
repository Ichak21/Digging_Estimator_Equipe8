import math
from enum import Enum


class Shift(Enum):
    NIGHT = 0
    DAY = 1


class TunnelTooLongForDelayException(Exception):
    pass


class InvalidFormatException(Exception):
    pass


class Team:
    def __init__(self):
        self.miners = 0
        self.healers = 0
        self.smithies = 0
        self.lighters = 0
        self.inn_keepers = 0
        self.guards = 0
        self.guard_managers = 0
        self.washers = 0

    def set_inn_keepers(self, night_or_day: Shift):
        if night_or_day == Shift.DAY:
            self.inn_keepers = math.ceil(
                (self.miners + self.healers + self.smithies) / 4.0) * 4

        elif night_or_day == Shift.NIGHT:
            self.inn_keepers = math.ceil((self.miners + self.healers +
                                          self.smithies + self.lighters) / 4.0) * 4

    def set_washers(self, night_or_day: Shift):
        if night_or_day == Shift.DAY:
            self.washers = math.ceil((self.miners + self.healers +
                                      self.smithies + self.inn_keepers) / 10.0)

        elif night_or_day == Shift.NIGHT:
            self.washers = math.ceil((self.miners + self.healers + self.smithies + self.inn_keepers +
                                      self.lighters + self.guards + self.guard_managers) / 10.0)

    def set_guards(self):
        pass

    def set_guard_managers(self):
        pass


class TeamComposition:
    def __init__(self):
        self.day_team: Team = Team()
        self.night_team: Team = Team()
        self.head_count = 0


class DiggingEstimator:
    MAX_ROTATION = 2
    LIMIT_LENGTH = 0
    LIMIT_DAYS = 0
    MINER_INCREMENTOR = 1

    def digging_project_is_possible(self, tunnel_length, digging_days, max_dig_per_days):
        if not(isinstance(tunnel_length, int) and tunnel_length > 0 and isinstance(digging_days, int) and digging_days > 0):
            raise InvalidFormatException()

        if math.floor(tunnel_length / digging_days) > max_dig_per_days:
            raise TunnelTooLongForDelayException()

    def capacity_calculate(self, rock_type):
        dig_per_dwarf_numbers = self.get(rock_type)
        max_dig_per_shift = dig_per_dwarf_numbers[len(
            dig_per_dwarf_numbers) - 1]
        max_dig_per_days = self.MAX_ROTATION * max_dig_per_shift

        return [dig_per_dwarf_numbers, max_dig_per_shift, max_dig_per_days]

    def get(self, rock_type):
        # for example for granite it returns [0, 3, 5.5, 7]
        # if you put 0 dwarf, you dig 0m / d / team
        # if you put 1 dwarf, you dig 3m / d / team
        # 2 dwarves = 5.5 m / d / team
        # so a day team on 2 miners and a night team of 1 miner dig 8.5 m / d
        url = "dtp://research.vin.co/digging-rate/" + rock_type
        print("Trying to fetch" + url)
        raise Exception("Does not work in test mode")

    def average_per_day(self, lg, dys):
        return math.floor(lg / dys)

    def day_shift_handling(self, composition):
        day_shift = composition.day_team

        # DAY TIME
        if day_shift.miners > 0:
            day_shift.healers += 1
            day_shift.smithies += 2
            day_shift.set_inn_keepers(Shift.DAY)
            day_shift.set_washers(Shift.DAY)

        composition.head_count = self.day_shift_addition(day_shift)

        return composition.head_count

    def night_shift_handling(self, composition):
        self.composition = TeamComposition()
        night_shift = composition.night_team
        # NIGHT TIME
        if night_shift.miners > 0:
            night_shift.healers += 1
            night_shift.smithies += 2
            night_shift.lighters = night_shift.miners + 1
            night_shift.inn_keepers = math.ceil(
                (night_shift.miners + night_shift.healers + night_shift.smithies + night_shift.lighters) / 4.0) * 4
            while True:
                old_washers = night_shift.washers
                old_guards = night_shift.guards
                old_chief_guard = night_shift.guard_managers

                night_shift.washers = math.ceil((night_shift.miners + night_shift.healers + night_shift.smithies +
                                                night_shift.inn_keepers + night_shift.lighters + night_shift.guards + night_shift.guard_managers) / 10.0)
                night_shift.guards = math.ceil(
                    (night_shift.healers + night_shift.miners + night_shift.smithies + night_shift.lighters + night_shift.washers) / 3.0)
                night_shift.guard_managers = math.ceil(
                    (night_shift.guards) / 3.0)

                if old_washers == night_shift.washers and old_guards == night_shift.guards and old_chief_guard == night_shift.guard_managers:
                    break
        composition.head_count = self.night_shift_addition(night_shift)
        return composition.head_count

    def day_shift_addition(self, team):
        self.team = Team()
        return team.miners + team.washers + team.healers + team.smithies + team.inn_keepers

    def night_shift_addition(self, team):
        self.team = Team()
        return team.miners + team.washers + team.healers + team.smithies + team.inn_keepers + team.guards + team.guard_managers + team.lighters

    def tunnel(self, tunnel_length, digging_days, rock_type):
        distances_per_dwarf_numbers = self.capacity_calculate(rock_type)[0]
        max_dig_per_shift = self.capacity_calculate(rock_type)[1]
        max_dig_per_day = self.capacity_calculate(rock_type)[2]

        self.digging_project_is_possible(
            tunnel_length, digging_days, max_dig_per_day)

        composition = TeamComposition()

        # Miners
        for dig_distance in range(0, len(distances_per_dwarf_numbers) - 1):
            if distances_per_dwarf_numbers[dig_distance] < self.average_per_day(tunnel_length, digging_days):
                composition.day_team.miners += self.MINER_INCREMENTOR

            if distances_per_dwarf_numbers[dig_distance] + max_dig_per_shift < self.average_per_day(tunnel_length, digging_days):
                composition.night_team.miners += self.MINER_INCREMENTOR

        composition.head_count = self.day_shift_handling(
            composition) + self.night_shift_handling(composition)

        return composition
