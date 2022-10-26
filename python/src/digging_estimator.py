import math


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


class TeamComposition:
    def __init__(self):
        self.day_team: Team = Team()
        self.night_team: Team = Team()
        self.total = 0


class DiggingEstimator:
    MAX_ROTATION = 2
    LIMIT_LENGTH = 0
    LIMIT_DAYS = 0
    MINER_INCREMENTOR = 1

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
        self.composition = TeamComposition()
        day_shift = composition.day_team
        #DAY TIME
        if day_shift.miners > 0:
            day_shift.healers += 1
            day_shift.smithies += 2
            day_shift.inn_keepers = math.ceil((day_shift.miners + day_shift.healers + day_shift.smithies) / 4.0) * 4
            day_shift.washers = math.ceil((day_shift.miners + day_shift.healers + day_shift.smithies + day_shift.inn_keepers) / 10.0)
        composition.total = self.day_shift_addition(day_shift)
        return composition.total

    def night_shift_handling(self, composition):
        self.composition = TeamComposition()
        night_shift = composition.night_team
        #NIGHT TIME
        if night_shift.miners > 0:
            night_shift.healers += 1
            night_shift.smithies += 2
            night_shift.lighters = night_shift.miners + 1                        
            night_shift.inn_keepers = math.ceil((night_shift.miners + night_shift.healers + night_shift.smithies + night_shift.lighters) / 4.0) * 4            
            while True:
                old_washers = night_shift.washers
                old_guards = night_shift.guards
                old_chief_guard = night_shift.guard_managers

                night_shift.washers = math.ceil((night_shift.miners + night_shift.healers + night_shift.smithies + night_shift.inn_keepers + night_shift.lighters + night_shift.guards + night_shift.guard_managers) / 10.0)
                night_shift.guards = math.ceil((night_shift.healers + night_shift.miners + night_shift.smithies + night_shift.lighters + night_shift.washers) / 3.0)
                night_shift.guard_managers = math.ceil((night_shift.guards) / 3.0)

                if old_washers == night_shift.washers and old_guards == night_shift.guards and old_chief_guard == night_shift.guard_managers:
                    break
        composition.total = self.night_shift_addition(night_shift)
        return composition.total

    def day_shift_addition(self, team):
        self.team = Team()
        return team.miners + team.washers + team.healers + team.smithies + team.inn_keepers

    def night_shift_addition(self, team):
        self.team = Team()
        return team.miners + team.washers + team.healers + team.smithies + team.inn_keepers + team.guards + team.guard_managers + team.lighters

    def tunnel(self, length, days, rock_type):
        dig_per_rotation = self.get(rock_type)
        max_dig_per_rotation = dig_per_rotation[len(dig_per_rotation) - 1]
        max_dig_per_day = self.MAX_ROTATION * max_dig_per_rotation

        if math.floor(length) != length or math.floor(days) != days or length < self.LIMIT_LENGTH or days < self.LIMIT_DAYS:
            raise InvalidFormatException()
        if self.average_per_day(length, days) > max_dig_per_day:
            raise TunnelTooLongForDelayException()

        composition = TeamComposition()

        # Miners
        for i in range(0, len(dig_per_rotation) -1):
            if dig_per_rotation[i] < self.average_per_day(length, days):
                composition.day_team.miners += self.MINER_INCREMENTOR
                
            if max_dig_per_rotation < self.average_per_day(length, days):
                if dig_per_rotation[i] + max_dig_per_rotation < self.average_per_day(length, days):
                    composition.night_team.miners += self.MINER_INCREMENTOR

        composition.total = self.day_shift_handling(composition) + self.night_shift_handling(composition)

        return composition