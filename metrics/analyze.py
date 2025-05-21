import statistics
from collections import defaultdict
from typing import Iterable

from prometheus_client import Metric
from prometheus_client.samples import Sample

from metrics.index import avg_by


class MetricAnalyzer:
    """
    读取采集到的所有 metrics，分析并生成新的 metrics。
    """

    def analyze(
        self, metrics: dict[str, Metric], scrape_time: float
    ) -> Iterable[Metric]:
        """
        metrics: 采集到的所有 MetricFamily 或 Sample
        返回：新的 MetricFamily 或 Sample 列表
        """
        raise NotImplementedError


class CpuUsageAnalyzer(MetricAnalyzer):
    """
    分析 CPU 使用率
    """

    def __init__(self, mode_exclude=("idle",)):
        """
        mode_exclude: 排除的 CPU 模式（如 idle）
        """

        self.prev_values: dict[tuple[str, str], float] = (
            {}
        )  # key: (core, mode), value: (value, timestamp)
        self.mode_exclude = mode_exclude

    def analyze(
        self, metrics: dict[str, Metric], scrape_time: float
    ) -> Iterable[Metric]:
        """
        metrics: 采集到的所有 MetricFamily 或 Sample
        返回：新的 MetricFamily 或 Sample 列表
        """
        # 1. 收集 CPU 使用率指标
        cpu_usage_metric = metrics.get("windows_cpu_time")
        if not cpu_usage_metric:
            return []

        # 2. 计算 CPU 使用率
        cpu_usage = self.calculate_cpu_usage(cpu_usage_metric.samples)

        # 3. 返回新的指标
        new_metric = Metric("cpu_usage_percent", "CPU Usage Percentage", "gauge")
        for core, usage in cpu_usage.items():
            new_metric.add_sample(
                "cpu_usage_percent",
                {"core": core},
                value=usage,
                timestamp=scrape_time,
            )

        return [new_metric]

    def calculate_cpu_usage(self, samples: Iterable[Sample]) -> dict[str, float]:
        """
        计算CPU使用率（百分比）
        samples: CPU 使用率指标的样本列表
        返回：每个 CPU 核心的使用率（百分比）
        """

        # 1. 收集 values
        values: dict[tuple[str, str], list[float]] = defaultdict(list)
        for sample in samples:
            core = sample.labels.get("core")
            mode = sample.labels.get("mode")
            values[(core, mode)].append(float(sample.value))

        # 2. 统计 usages 和 totals
        usages: dict[str, float] = defaultdict(float)
        totals: dict[str, float] = defaultdict(float)
        for (core, mode), value_list in values.items():
            avg_value = statistics.mean(value_list)
            delta = avg_value - self.prev_values.get((core, mode), avg_value)
            self.prev_values[(core, mode)] = avg_value

            totals[core] += delta
            if mode not in self.mode_exclude:
                usages[core] += delta

        # 3. 计算 CPU 使用率
        usages_rate: dict[str, float] = {
            core: (usages[core] / totals[core] * 100) if totals[core] > 0 else 0.0
            for core in totals.keys()
        }

        return usages_rate


class MemoryTrendAnalyzer(MetricAnalyzer):
    """
    分析内存使用率趋势
    """

    def analyze(
        self, metrics: dict[str, Metric], scrape_time: float
    ) -> Iterable[Metric]:
        """
        metrics: 采集到的所有 MetricFamily 或 Sample
        返回：新的 MetricFamily 或 Sample 列表
        """
        # 1. 收集内存指标
        memory_free_metric = metrics.get("windows_os_physical_memory_free_bytes")
        memory_total_metric = metrics.get("windows_cs_physical_memory_bytes")
        if not memory_free_metric or not memory_total_metric:
            return

        # 2. 计算内存使用率
        memory_free = next(iter(avg_by(memory_free_metric.samples))).value
        memory_total = next(iter(avg_by(memory_total_metric.samples))).value
        memory_usage = (
            (memory_total - memory_free) / memory_total * 100
            if memory_total > 0
            else 0.0
        )

        # 3. 返回新的指标
        new_metric = Metric("memory_usage_percent", "Memory Usage Percentage", "gauge")
        new_metric.add_sample(
            "memory_usage_percent",
            {},
            value=memory_usage,
            timestamp=scrape_time,
        )

        yield new_metric
