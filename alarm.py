from dataclasses import dataclass
from datetime import datetime


def wrap_with_zero(a: int):
    if a < 10:
        return f"0{a}"
    return str(a)


@dataclass()
class Alarm:
    hour: int
    minute: int

    def is_equal(self, date: datetime):
        return self.minute == date.minute and self.hour == date.hour

    def short(self):
        return f"{wrap_with_zero(self.hour)}:{wrap_with_zero(self.minute)}"

    def from_now(self, now: datetime):
        tmp = self._from_now_minutes(now)
        return f"{wrap_with_zero(tmp // 60)}:{wrap_with_zero(tmp % 60)}"

    def _from_now_minutes(self, now: datetime):
        curr_time = now.hour * 60 + now.minute
        alarm_time = self.hour * 60 + self.minute

        if curr_time > alarm_time:
            return alarm_time + (24 * 60 - curr_time)

        return alarm_time - curr_time
