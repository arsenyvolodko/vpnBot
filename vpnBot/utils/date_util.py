from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_next_date(**kwargs) -> datetime.date:
    start_date = kwargs.get("start_date", datetime.now().date())
    months_delta = kwargs.get("months_delta", 1)
    hours_delta = kwargs.get("hours_delta", 0)
    return start_date + relativedelta(months=months_delta, hours=hours_delta)
