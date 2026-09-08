from datetime import datetime, timedelta


def get_delta_time_secs(start_time: datetime, end_time: datetime) -> int:
    """Retruns the total number of seconds between two datetime objects"""
    delta: timedelta = end_time - start_time
    return int(delta.total_seconds())


def get_delta_time_HM(start_time: datetime, end_time: datetime) -> tuple[int, int]:
    """Returns the hours and minutes between two datetime objects"""

    total_seconds: int = get_delta_time_secs(start_time, end_time)

    minutes: int = total_seconds // 60
    hours: int = minutes // 60

    # works whether hours >= 0
    remainder_minutes: int = minutes - (hours * 60)

    return (hours, remainder_minutes)


def short_time(time: str) -> str:

    # remove leading zeros
    time = time.lstrip("0")

    # swap A for AM and P for PM
    time = time.replace(" AM", "A")
    time = time.replace(" PM", "P")

    return time


def short_event(eventname: str) -> str | None:

    lookup: dict[str, str] = {
        "Butterfly": "Fly",
        "Backstroke": "BK",
        "Breaststroke": "BR",
        "Freestyle": "FR",
        "Medley": "Med",
        "IM": "IM",
    }

    # returns None if eventname is not found
    return lookup.get(eventname)


def short_gender(gender: str) -> str | None:

    lookup: dict[str, str] = {
        "Girls": "W",
        "Women": "W",
        "Boys": "M",
        "Men": "M",
        "Mixed": "X",
    }

    # returns None if gender is not found
    return lookup.get(gender)
