from datetime import datetime, timedelta


class After:
    def __int__(self, duration):
        self.duration = duration

    def get_score(self):
        return self.duration
class Patrol:
    TOUGH = -2
    EASY = -1
    def __init__(self, start_date: str, start_time: str, end_time: str):
        start_time = datetime.strptime(f"{start_date} {start_time}", '%d/%m/%Y %H:%M')
        end_time = datetime.strptime(f"{start_date} {end_time}", '%d/%m/%Y %H:%M')
        if end_time < start_time:
            end_time += timedelta(days=1)
        duration_in_s = (end_time - start_time).total_seconds()
        self.duration = divmod(duration_in_s, 3600)[0]
        if self.duration < 0:
            print("stop")
        self.start_time = start_time
        self.end_time = end_time
    def classification(self):
        if self.start_time.hour < 5 or self.start_time.hour >= 23:
            return self.TOUGH
        else:
            return self.EASY
    def get_score(self):
        return self.duration * self.classification()

class Rest:
    TOUGH = 1
    EASY = 0.5

    def __init__(self,date, start_time, end_time):
        start_time = datetime.strptime(f"{date} {start_time}", '%d/%m/%y %H:%M')
        end_time = datetime.strptime(f"{date} {end_time}", '%d/%m/%y %H:%M')
        duration_in_s = (end_time - start_time).total_seconds()
        self.duration = divmod(duration_in_s, 3600)[0]
        self.start_time = start_time
        self.end_time = end_time
    def classification(self):
        if self.start_time.hour < 5 or self.start_time.hour >= 23:
            return self.TOUGH
        else:
            return self.EASY
    def get_score(self):
        return self.duration * self.classification()