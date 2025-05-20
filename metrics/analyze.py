import math
import statistics
from collections import defaultdict
from typing import Literal

from prometheus_client.samples import Sample

from metrics.collect import TimedSample
from metrics.index import get_samples_by_labels, index_samples, TimedSampleList, GroupedSamples

AggType = Literal["avg", "sum", "max", "min", "count"]


def aggregate_samples(samples: TimedSampleList, agg: str = "avg") -> float:
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


class CpuUsageCalculator:
    def __init__(self, mode_exclude=("idle",)):
        self.prev_values: dict[tuple[str, str], float] = {}  # key: (core, mode), value: (value, timestamp)
        self.mode_exclude = mode_exclude

    def calculate_cpu_usage(self, index: GroupedSamples) -> dict[str, float]:
        """
        计算CPU使用率（百分比）
        index: 分组后的样本索引
        """
        samples = get_samples_by_labels(index, "windows_cpu_time_total")

        # 1. 收集 values
        values: dict[tuple[str, str], list[float]] = defaultdict(list)
        for sample, _ts in samples:
            core = sample.labels.get("core")
            mode = sample.labels.get("mode")
            values[(core, mode)].append(sample.value)

        # 2. 统计 usages 和 totals
        usages: dict[str, float] = defaultdict(float)
        totals: dict[str, float] = defaultdict(float)
        for (core, mode), value_list in values.items():
            avg_value = statistics.mean(value_list)
            if (core, mode) not in self.prev_values:
                self.prev_values[(core, mode)] = avg_value
            delta = avg_value - self.prev_values[(core, mode)]

            totals[core] += delta
            if mode not in self.mode_exclude:
                usages[core] += delta

        # 3. 计算 CPU 使用率
        usages_rate: dict[str, float] = {
            core: (usages[core] / totals[core] * 100) if totals[core] > 0 else 0
            for core in totals.keys()
        }

        return usages_rate


def calculate_memory_usage(avail_samples: TimedSampleList, total_samples: TimedSampleList) -> float:
    """
    计算内存使用率（百分比）
    avail_samples: 可用内存样本
    total_samples: 总内存样本
    """
    if not avail_samples or not total_samples:
        return 0.0
    avail = aggregate_samples(avail_samples, "avg")
    total = aggregate_samples(total_samples, "avg")
    if total == 0:
        return 0.0
    return (total - avail) / total * 100


cpu_calc = CpuUsageCalculator()


class Analyzer:
    def __init__(self):
        self.cpu_calculator = CpuUsageCalculator()

    def analyze_all(self, index):
        cpu_samples = get_samples_by_labels(index, "windows_cpu_time_total")
        cpu_usage = cpu_calc.calculate_cpu_usage(cpu_samples)

        avail_samples = get_samples_by_labels(index, "windows_memory_available_bytes")
        total_samples = get_samples_by_labels(index, "windows_memory_total_bytes")
        mem_usage = calculate_memory_usage(avail_samples, total_samples)
        return {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": mem_usage,
        }


def extract_disk_usage():
    pass


def extract_network_usage():
    pass
