from datetime import datetime
from constants import server_launch
from dateutil.relativedelta import relativedelta


class DateFunc:

    delta_hours = 3 if server_launch else 0

    @classmethod
    def get_cur_date(cls, date_format: str = "%Y-%m-%d"):
        cur_date = datetime.now().date()
        delta = relativedelta(hours=cls.delta_hours)
        date = cur_date + delta
        return date.strftime(date_format)

    @classmethod
    def get_cur_time(cls, time_format: str = "%Y-%m-%d %H:%M"):
        cur_date = datetime.now()
        delta = relativedelta(hours=cls.delta_hours)
        date = cur_date + delta
        return date.strftime(time_format)

    @classmethod
    def get_next_date(cls, date_string: str = None, months: int = 1):
        date = datetime.strptime(date_string, "%Y-%m-%d")
        delta = relativedelta(months=months)
        next_payment_date = date.replace(day=date.day) + delta
        return next_payment_date.strftime("%Y-%m-%d")
