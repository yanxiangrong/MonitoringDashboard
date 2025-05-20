from collections import defaultdict

from metrics.index import get_samples_by_labels, index_samples


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


def calculate_cpu_usage(samples: list[tuple], mode_exclude=("idle",)) -> float:
    """
    计算CPU使用率（百分比）
    samples: 某一instance所有core、mode的样本
    mode_exclude: 排除哪些mode（如idle、iowait）
    """
    # 按 (core, mode) 分组
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


def calculate_memory_usage(avail_samples, total_samples) -> float:
    """
    计算内存使用率（百分比）
    """
    # 获取最新的可用和总内存
    if not avail_samples or not total_samples:
        return 0.0
    avail = float(avail_samples[-1][0].value)
    total = float(total_samples[-1][0].value)
    if total == 0:
        return 0.0
    used = total - avail
    return used / total * 100


def analyze_all(index):
    cpu_samples = get_samples_by_labels(index, "windows_cpu_time_total")
    cpu_usage = calculate_cpu_usage(cpu_samples)

    avail_samples = get_samples_by_labels(index, "windows_memory_available_bytes")
    total_samples = get_samples_by_labels(index, "windows_memory_total_bytes")
    mem_usage = calculate_memory_usage(avail_samples, total_samples)
    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": mem_usage,
    }


def analyze_history(history):
    results = []
    for samples in history:
        index = index_samples(samples)
        metrics = analyze_all(index)
        results.append(metrics)
    return results  # 这是一个列表，每个元素是一次分析结果


def extract_disk_usage():
    pass


def extract_network_usage():
    pass
