import logging
import time
from typing import Iterable

import requests
from prometheus_client import Metric
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.registry import Collector

from config import REQUEST_TIMEOUT


class RemoteMetricsCollector(Collector):
    """
    一个从远程 Prometheus Exporter URL 拉取并转发指标的 Collector。
    """

    def __init__(self, url: str):
        """
        Args:
            url (str): Prometheus Exporter 的 metrics 接口地址。
        """
        self.url = url
        self.last_scrape_time = None

    def collect(self) -> Iterable[Metric]:
        try:
            resp = requests.get(self.url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            self.last_scrape_time = time.time()
            yield from text_string_to_metric_families(resp.text)
        except requests.RequestException as e:
            logging.error(f"Failed to collect remote metrics: {e}")
