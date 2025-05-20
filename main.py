import time
from typing import Any, Generator

import requests
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


def collect_metrics(url: str) -> Generator[tuple[Sample, float], Any, None]:
    """
    Collect metrics from the given URL.
    Args:
        url (str): The URL to collect metrics from.
    Yields:
        tuple[Sample, float]: A tuple containing the sample and the scrape time.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    scrape_time = time.time()
    for family in text_string_to_metric_families(resp.text):
        for sample in family.samples:
            yield sample, scrape_time


def index_samples(samples: list[tuple[Sample, float]]) -> dict[str, list[tuple[Sample, float]]]:
    """
    按 metric 名称分组，返回字典
    """
    index: dict[str, list[tuple[Sample, float]]] = {}
    for sample, ts in samples:
        index.setdefault(sample.name, []).append((sample, ts))
    return index


def get_samples_by_labels(
        index: dict[str, list[tuple]],
        metric_name: str,
        label_filter: dict
) -> list[tuple]:
    """
    从 index 中按 metric_name 和 label_filter 过滤样本

    Args:
        index: {metric_name: [(Sample, ts), ...]}
        metric_name: 指标名
        label_filter: dict，label 过滤条件，如 {"instance": "host1"}
    Returns:
        list[tuple]: 所有匹配的 (Sample, ts)
    """
    result = []
    for sample, ts in index.get(metric_name, []):
        if all(sample.labels.get(k) == v for k, v in label_filter.items()):
            result.append((sample, ts))
    return result


def aggregate_samples(samples: list[tuple], agg: str = "avg") -> float:
    """
    对样本值做聚合分析
    agg: "avg", "sum", "max", "min", "count"
    """
    values = [float(sample.value) for sample, _ in samples]
    if not values:
        return 0.0
    if agg == "avg":
        return sum(values) / len(values)
    elif agg == "sum":
        return sum(values)
    elif agg == "max":
        return max(values)
    elif agg == "min":
        return min(values)
    elif agg == "count":
        return len(values)
    else:
        raise ValueError(f"Unknown agg: {agg}")

def calculate_cpu_usage(samples: list[tuple], mode_exclude=("idle", "iowait")) -> float:
    """
    计算CPU使用率（百分比）
    samples: 某一instance所有core、mode的样本
    mode_exclude: 排除哪些mode（如idle、iowait）
    """
    # 按 (core, mode) 分组
    from collections import defaultdict
    grouped = defaultdict(list)
    for sample, ts in samples:
        core = sample.labels.get("core")
        mode = sample.labels.get("mode")
        grouped[(core, mode)].append((sample, ts))

    usage = 0.0
    total = 0.0
    for (core, mode), group in grouped.items():
        if len(group) < 2:
            continue
        # 取最新两条
        (s1, t1), (s2, t2) = group[-2], group[-1]
        delta = float(s2.value) - float(s1.value)
        if mode in mode_exclude:
            total += delta
        else:
            usage += delta
            total += delta
    if total == 0:
        return 0.0
    return usage / total * 100

def calculate_memory_usage(index, instance: str) -> float:
    """
    计算内存使用率（百分比）
    """
    # 获取最新的可用和总内存
    avail_samples = get_samples_by_labels(index, "windows_memory_available_bytes", {"instance": instance})
    total_samples = get_samples_by_labels(index, "windows_memory_total_bytes", {"instance": instance})
    if not avail_samples or not total_samples:
        return 0.0
    avail = float(avail_samples[-1][0].value)
    total = float(total_samples[-1][0].value)
    if total == 0:
        return 0.0
    used = total - avail
    return used / total * 100

def analyze_all(index, instance: str):
    cpu_samples = get_samples_by_labels(index, "windows_cpu_time_total", {"instance": instance})
    cpu_usage = calculate_cpu_usage(cpu_samples)
    mem_usage = calculate_memory_usage(index, instance)
    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": mem_usage,
    }

def extract_disk_usage():
    pass


def extract_network_usage():
    pass


def main():
    samples = list(collect_metrics(EXPORTER_URL))
    result = analyze_metrics(samples)
    print(result)


def main():
    for sample, ts in collect_metrics(EXPORTER_URL):
        print(sample, ts)


if __name__ == "__main__":
    main()
