from typing import TypedDict


class AppConfig(TypedDict):
    url: str
    fullscreen: bool
    title: str
    refresh_interval: float  # 刷新间隔，单位为秒
    fetch_timeout: float  # 数据拉取超时时间，单位为秒
