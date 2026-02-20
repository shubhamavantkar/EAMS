from datetime import timedelta


def format_duration(seconds: int) -> str:
    return str(timedelta(seconds=max(seconds, 0)))
