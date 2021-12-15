from datetime import datetime

def diff_in_hours(dt1: datetime, dt2: datetime) -> float:
    diff = dt1 - dt2
    return diff.total_seconds() / 3600

