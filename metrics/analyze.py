import statistics
from collections import defaultdict
from typing import Literal, Any

from metrics.index import get_samples_by_labels, GroupedSamples

AggType = Literal["avg", "sum", "max", "min", "count"]




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
            values[(core, mode)].append(float(sample.value))

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
            core: (usages[core] / totals[core] * 100) if totals[core] > 0 else 0.0
            for core in totals.keys()
        }

        return usages_rate


def calculate_memory_usage(index: GroupedSamples) -> float:
    """
    计算内存使用率（百分比）
    index: 分组后的样本索引
    """

    avail_samples = get_samples_by_labels(index, "windows_os_physical_memory_free_bytes")
    total_samples = get_samples_by_labels(index, "windows_cs_physical_memory_bytes")

    avail = aggregate_samples(avail_samples, "avg")
    total = aggregate_samples(total_samples, "avg")

    return (total - avail) / total * 100 if total > 0 else 0.0


class Analyzer:
    def __init__(self):
        self.cpu_calculator = CpuUsageCalculator()

    def analyze_all(self, index: GroupedSamples) -> dict[str, Any]:
        cpu_usage = self.cpu_calculator.calculate_cpu_usage(index)

        mem_usage = calculate_memory_usage(index)
        return {
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": mem_usage,
        }
