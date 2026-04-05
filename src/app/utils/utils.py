
def validate_dates(start_date, end_date):
    valid = True
    if start_date > end_date:
        valid = False
    return valid

def highlight_invalid_field(field):
    field.setStyleSheet("border: 1px solid #FF5555;")

def clear_highlight_field(field):
    field.setStyleSheet("")