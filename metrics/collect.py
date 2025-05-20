import time
from typing import Tuple

import requests
from prometheus_client.parser import text_string_to_metric_families

from metrics.types import Samples


def collect_metrics(url: str) -> Tuple[Samples, float]:
    """
    从指定的 Prometheus Exporter URL 采集一次全部指标样本，并返回统一的采集时间戳。

    Args:
        url (str): Prometheus Exporter 的 metrics 接口地址。

    Returns:
        samples (Iterable[Sample]): 一个生成器，依次产出本次采集到的所有 Sample 对象。
        scrape_time (float): 本次采集的统一时间戳（Unix 时间，单位秒）。
    """
    # 发送 HTTP 请求获取 Prometheus metrics 文本
    resp = requests.get(url)
    resp.raise_for_status()
    # 记录本次采集的时间戳
    scrape_time = time.time()
    # 生成器表达式，依次产出所有样本
    samples = (
        sample
        for family in text_string_to_metric_families(resp.text)
        for sample in family.samples
    )
    return samples, scrape_time
