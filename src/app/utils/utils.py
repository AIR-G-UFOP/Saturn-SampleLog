
def validate_dates(start_date, end_date):
    valid = True
    if start_date > end_date:
        valid = False
    return valid