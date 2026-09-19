from pathlib import Path

# 接口地址与请求头（值属于上游契约，保持固定）
API_ROOT = "https://qhcal-api.jin10.com"
REQUEST_TIMEOUT = 10
# 请求节奏：随机抖动 + 失败退避，避免固定间隔的机械特征
REQUEST_MIN_DELAY = 0.15
REQUEST_MAX_DELAY = 0.65
REQUEST_RETRIES = 3
RETRY_MIN_BACKOFF = 1.0
RETRY_MAX_BACKOFF = 3.0
# 打乱日期处理顺序，避免按日递增的固定序列
SHUFFLE_DAY_ORDER = True
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "x-app-id": "1coXNOi34tU5TDTl",
    "x-version": "1.0",
    "Referer": "https://qihuo.jin10.com/",
    "Origin": "https://qihuo.jin10.com",
    "Accept-Encoding": "gzip, deflate",
}

# 抓取范围与排版节奏
FORECAST_DAYS = 30
SLOT_START_HOUR = 8
SLOT_START_MINUTE = 0
SLOT_INTERVAL_MINUTES = 10

# 精选 feed 的入选规则
FEATURED_MIN_STARS = 4
FEATURED_TAG = "黄金"

# 输出位置
FEED_DIR = Path("feeds")
FULL_FEED = FEED_DIR / "full.ics"
FEATURED_FEED = FEED_DIR / "featured.ics"

TIMEZONE = "Asia/Shanghai"

# 事件 UID 的命名域（保证重跑稳定，避免日历出现重复条目）
UID_DOMAIN = "econ-calendar"
