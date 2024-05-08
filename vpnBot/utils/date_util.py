from datetime import datetime, date

from dateutil.relativedelta import relativedelta


def get_next_date(start_date: date | None = None):
    if start_date is None:
        start_date = datetime.now().date()
    return start_date + relativedelta(months=1)
