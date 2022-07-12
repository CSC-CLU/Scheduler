import datetime


class PST(datetime.tzinfo):
    def tzname(self, __dt):
        return "US/Pacific"

    def dst(self, dt):
        if dt.month in range(4, 10) or (dt.month == 3 and dt.day >= 13) or (dt.month == 11 and dt.day < 6):
            return datetime.timedelta(hours=-1)
        else:
            return datetime.timedelta(hours=0)

    def utcoffset(self, dt):
        datetime.timedelta(hours=-7) + self.dst(dt)
