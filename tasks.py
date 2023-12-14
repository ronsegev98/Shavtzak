from typing import List
from typing_extensions import Self

import pandas as pd

from definitions import MISSING, MINUTES_AN_HOUR, HOURS_A_DAY


class GuardingStand:
    def __init__(self, name, pattern, start_date, end_date):
        self.name = name
        self.patterns = self.parse_pattern(pattern)
        self.start_date = start_date
        self.end_date = end_date
        self.manning = pd.DataFrame(columns=["task", "start_date", "start_time", "end_date", "end_time",
                                             "soldier1", "soldier2", "soldier3", "soldier4"])
        self.init_manning()

    @staticmethod
    def parse_pattern(pattern):
        """
        pattern should be: "hour:hour:shift_time:manning,hour:hour:shift_time:manning.."
        for example, if a task should be occupied in a 2-hours shifts, between 22:00 to 04:00 with 2 people,
        and from 04:00 to 08:00 with 1, and all other time without anyone - the pattern should be:
        '0800:2200:2:0;2200:0400:2:2;0400:0800:2:1'
        for a single soldier, all day long, 3 hours shift:
        '0000:2400:1'
        :return: [[start_ts (Time), end_ts (Time), shift_time, amount of soldiers], [...]]
        """
        final_zones = []
        pattern = pattern.replace(" ", "")
        zones = pattern.split(";")
        for zone in zones:
            try:
                start, end, shift_time, amount = zone.split(":")
                start = Time.from_str(start)
                end = Time.from_str(end)
                end.set_midnight_time()
                final_zones.append([start, end, int(shift_time), int(amount)])
            except Exception as e:
                print(f"Error while parsing the tasks patterns: {zone}, error: {e}")
        return final_zones

    def init_manning(self):
        i = 0
        for pattern in self.patterns:
            start, end, shift, amount = pattern
            for start_time in start.between(end, shift):
                end_time = Time(start_time.hours, start_time.minutes)
                end_time.add(hours=shift)
                row = [self.name, self.start_date, start_time.to_string(), self.end_date, end_time.to_string(), "", "", "", ""]
                for j in range(amount):
                    row[5 + j] = MISSING
                self.manning.loc[i] = row
                i += 1
        self.manning = self.manning.sort_values("start_time")

class Time:
    def __init__(self, hours: int, minutes: int):
        self.hours = hours
        self.minutes = minutes

    @staticmethod
    def from_str(time: str):
        hour = int(time[:2])
        minutes = int(time[2:])
        return Time(hour, minutes)

    def set_midnight_time(self):
        if self.hours == 0:
            self.hours = 24

    def earlier_than(self, time):
        if self.hours < time.hours or (self.hours == time.hours and self.minutes <= time.minutes):
            return True
        else:
            return False

    def add(self, hours=0, minutes=0):
        self.hours += hours
        self.minutes += minutes
        if self.minutes > MINUTES_AN_HOUR:
            self.hours += int(minutes / MINUTES_AN_HOUR)
            self.minutes = self.minutes % MINUTES_AN_HOUR
        self.hours = self.hours % HOURS_A_DAY

    def between(self, time, shift) -> List[Self]:
        """
        the time between this time, and the given time.
        :param time:
        :param shift: time difference in hours
        :return: an array of the shifts between the current object and the given time.
        for example, if the given object represents the time 05:00, the other time is 9:00, and the shift is 2 hours,
        the following output will be given: [5,7,9]
        """
        if self.hours < time.hours:
            return [Time(hour, self.minutes) for hour in range(self.hours, time.hours, shift)]
        else:
            hours = []
            iterated_hour = self.hours
            while iterated_hour > time.hours:
                hours.append(Time(iterated_hour, self.minutes))
                iterated_hour = (iterated_hour + shift) % HOURS_A_DAY
            return hours + [Time(hour, self.minutes) for hour in range(iterated_hour, time.hours, shift)]

    def to_string(self):
        hour = f"0{self.hours}" if self.hours < 10 else self.hours
        minutes = f"0{self.minutes}" if self.minutes < 10 else self.minutes
        return f"{hour}:{minutes}"
