from datetime import timedelta

from ics import Calendar, Event

from .config import SLOT_INTERVAL_MINUTES, SLOT_START_HOUR, SLOT_START_MINUTE


def _title(item):
    stars = "★" * item.stars if item.stars > 0 else ""
    if item.kind == "data":
        tag = f"[{item.tag}]" if item.tag else ""
        return f"{item.clock} {stars} {tag} {item.title}".strip()
    return f"{item.clock} [大事] {stars} {item.country} {item.title}".strip()


def _to_event(item, begin):
    event = Event(uid=item.uid)
    event.name = _title(item)
    event.description = item.body
    event.begin = begin
    # 零时长，在日历中呈现为一条时间线
    event.duration = {"minutes": 0}
    return event


def add_day(calendar, items, day):
    """把某天的条目从 08:00 起按固定间隔排入日历。"""
    if not items:
        return 0

    cursor = day.replace(
        hour=SLOT_START_HOUR, minute=SLOT_START_MINUTE, second=0, microsecond=0
    )
    for item in items:
        calendar.events.add(_to_event(item, cursor))
        cursor += timedelta(minutes=SLOT_INTERVAL_MINUTES)
    return len(items)


def write(calendar, path):
    # 固定输出顺序，避免处理顺序变化导致文件抖动
    calendar.events = sorted(calendar.events, key=lambda event: (str(event.begin), event.uid))
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.writelines(calendar.serialize_iter())
