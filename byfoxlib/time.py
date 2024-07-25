from datetime import datetime

from nextcord.utils import format_dt


def join_dt(dt: datetime) -> str:
    return f"{format_dt(dt, style='D')}({format_dt(dt, style='R')})"
