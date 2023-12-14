import math
from datetime import datetime
from enum import Enum
from typing import List


class Pakal(Enum):
    officer = 1
    class_commander = 2
    simple = 3
class Soldier:
    def __init__(self, name, pakal=Pakal.simple):
        self.name: str = name
        self.last_patrol: datetime = datetime(1970, 1, 1)
        self._actions: List = []
        self.pakal: Pakal = pakal
        self.home_time: List[List[datetime, datetime]] = []

    def is_home(self, time: datetime):
        for after in self.home_time:
            start_time, end_time = after
            if start_time < time < end_time:
                return True
        return False

    def add_home_time(self, start_date, start_time, end_date, end_time):
        try:
            if math.isnan(start_time) or math.isnan(start_date):
                return
        except TypeError:
            start = datetime.strptime(f"{start_date} {start_time}", '%d/%m/%Y %H:%M')
            end = datetime.strptime(f"{end_date} {end_time}", '%d/%m/%Y %H:%M')
            self.home_time.append([start, end])
    def add_action(self, action):
        self._actions.append(action)
        # check if the given action should be declared as the soldier's last patrol:
        if self.last_patrol < action.end_time:
            self.last_patrol = action.end_time
    def tash_score(self):
        return sum(act.get_score() for act in self._actions)

