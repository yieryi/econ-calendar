import datetime
import logging
import random

import pytz
from ics import Calendar

from . import builder, client
from .config import (
    FEATURED_FEED,
    FORECAST_DAYS,
    FULL_FEED,
    SHUFFLE_DAY_ORDER,
    TIMEZONE,
)

logger = logging.getLogger("econ_calendar")


def collect(date_str):
    fetchers = [client.fetch_indicators, client.fetch_events]
    random.shuffle(fetchers)
    items = []
    for fetch in fetchers:
        items += fetch(date_str)
    return items


def run():
    zone = pytz.timezone(TIMEZONE)
    full = Calendar()
    featured = Calendar()

    logger.info("开始抓取未来 %s 天的日程", FORECAST_DAYS)
    today = datetime.datetime.now(zone)

    offsets = list(range(FORECAST_DAYS))
    if SHUFFLE_DAY_ORDER:
        random.shuffle(offsets)

    for index, offset in enumerate(offsets, 1):
        day = today + datetime.timedelta(days=offset)
        logger.info("处理 %s (%s/%s)", day.strftime("%Y-%m-%d"), index, FORECAST_DAYS)

        items = collect(day.strftime("%Y%m%d"))
        if not items:
            continue

        items.sort(key=lambda item: (item.sort_key, item.source_id, item.title))
        picks = [item for item in items if item.is_featured]

        total = builder.add_day(full, items, day)
        kept = builder.add_day(featured, picks, day)
        logger.info("  -> 全部 %s 条，精选 %s 条", total, kept)

    builder.write(full, FULL_FEED)
    builder.write(featured, FEATURED_FEED)
    logger.info("完成: %s (%s 条), %s (%s 条)", FULL_FEED, len(full.events), FEATURED_FEED, len(featured.events))


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run()


if __name__ == "__main__":
    main()
