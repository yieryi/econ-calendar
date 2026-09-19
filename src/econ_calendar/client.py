import datetime
import logging
import random
import time

import requests

from .config import (
    API_ROOT,
    REQUEST_HEADERS,
    REQUEST_MAX_DELAY,
    REQUEST_MIN_DELAY,
    REQUEST_RETRIES,
    REQUEST_TIMEOUT,
    RETRY_MAX_BACKOFF,
    RETRY_MIN_BACKOFF,
)
from .models import CalendarItem

logger = logging.getLogger(__name__)

_session = None


def _connection():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update(REQUEST_HEADERS)
    return _session


def _pause():
    time.sleep(random.uniform(REQUEST_MIN_DELAY, REQUEST_MAX_DELAY))


def _get(path, date_str):
    last_error = None
    for attempt in range(REQUEST_RETRIES):
        _pause()
        try:
            response = _connection().get(
                f"{API_ROOT}{path}",
                params={"date": date_str},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as exc:
            last_error = exc
        else:
            if response.status_code == 200:
                return response.json().get("data", [])
            last_error = f"HTTP {response.status_code}"
            if response.status_code not in (429, 500, 502, 503, 504):
                break
        time.sleep(random.uniform(RETRY_MIN_BACKOFF, RETRY_MAX_BACKOFF) * (attempt + 1))
    raise RuntimeError(f"请求失败 {path} {date_str}: {last_error}")


def _stars(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _text(value):
    return str(value) if value is not None else "--"


def _moment(value):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None


def fetch_indicators(date_str):
    try:
        rows = _get("/data", date_str)
    except Exception as exc:
        logger.warning("指标抓取失败: %s", exc)
        return []

    items = []
    for row in rows:
        title = row.get("title") or row.get("name") or "未命名数据"
        moment = _moment(row.get("publictime"))
        clock = moment.strftime("%H:%M") if moment else ""
        stars = _stars(row.get("star"))
        body = (
            "【经济数据】\n"
            f"真实时间: {clock}\n"
            f"项目: {title}\n"
            f"国家: {row.get('country', '')}\n"
            f"重要性: {stars}星\n"
            "----------------\n"
            f"今值: {_text(row.get('actual'))}\n"
            f"预测: {_text(row.get('consensus'))}\n"
            f"前值: {_text(row.get('previous'))} {_text(row.get('unit'))}"
        )
        items.append(
            CalendarItem(
                kind="data",
                title=title,
                country=row.get("country", ""),
                stars=stars,
                tag=row.get("qh_affect_text", ""),
                moment=moment,
                clock=clock,
                body=body,
                source_id=str(row.get("id") or row.get("dataId") or ""),
            )
        )
    return items


def fetch_events(date_str):
    try:
        rows = _get("/event", date_str)
    except Exception as exc:
        logger.warning("大事抓取失败: %s", exc)
        return []

    items = []
    for row in rows:
        content = row.get("eventcontent", "未命名事件")
        moment = _moment(row.get("dateTimeStr"))
        clock = moment.strftime("%H:%M") if moment else ""
        stars = _stars(row.get("star"))
        people = row.get("people")
        title = content if len(content) < 30 else content[:28] + "..."
        body = (
            "【财经大事】\n"
            f"真实时间: {clock}\n"
            f"内容: {content}\n"
            f"国家: {row.get('country', '')}\n"
            f"人物: {people if people else '--'}\n"
            f"重要性: {stars}星"
        )
        items.append(
            CalendarItem(
                kind="event",
                title=title,
                country=row.get("country", ""),
                stars=stars,
                tag="",
                moment=moment,
                clock=clock,
                body=body,
                source_id=str(row.get("id") or ""),
            )
        )
    return items
