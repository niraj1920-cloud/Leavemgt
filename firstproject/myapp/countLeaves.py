from datetime import datetime, timedelta, date


def leave_days(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    exclude_dates = []
    date_2023 = datetime(2023, 1, 1)
    while date_2023.year == 2023:
        if date_2023.weekday() in [5, 6]:
            exclude_dates.append(date_2023)
        date_2023 += timedelta(days=1)

    exclude_dates = [date.date() for date in exclude_dates]

    print(len(exclude_dates))

    print(start_date, "  ", end_date)
    leave_days = 0
    d = start_date
    while d <= end_date:
        if d not in exclude_dates:
            leave_days += 1
        d += timedelta(days=1)
    return leave_days
