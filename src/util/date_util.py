"""Datetime util"""
from datetime import datetime, time, timedelta


def seconds_until(hours: int, minute: int) -> int:
    """Return seconds until given hour and minute"""
    given_time = time(hour=hours, minute=minute)
    now = datetime.now()
    future_exec = datetime.combine(now, given_time)
    if (future_exec - now).days < 0:
        # If we are past the execution, it will take place tomorrow
        future_exec = datetime.combine(now + timedelta(days=1), given_time) # days always >= 0
    return (future_exec - now).total_seconds()

def ceil_datetime(dt: datetime, delta: timedelta) -> datetime:
    """Return datetime rounded up to the nearest given delta"""
    return dt + (datetime.min - dt) % delta
