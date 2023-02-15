from datetimerange import DateTimeRange
# from collections import namedtuple


def check_date_overlap(startDate1, endDate1, startDate2, endDate2):
    if endDate2 > startDate1 and startDate2 < endDate1 and startDate1 < endDate1:
        return True
    else:
        return False

    
