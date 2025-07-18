import statistics
from collections import defaultdict
from typing import Iterable, Literal, Optional

from prometheus_client import Metric
from prometheus_client.samples import Sample

from .utils import assert_samples_consistent


def build_metric_map(metrics: Iterable[Metric]) -> dict[str, Metric]:
    """
    将 Metric 列表转换为 name -> Iterable[Sample] 的映射
    """
    return {m.name: m for m in metrics}


def filter_by_labels(
    samples: Iterable[Sample], labels: Optional[dict[str, str]] = None
) -> Iterable[Sample]:
    """
    过滤样本
    labels: 按哪些labels过滤，None表示不过滤
    """

    for s in assert_samples_consistent(samples):
        if not labels:
            yield s
            continue
        if all(s.labels.get(k) == v for k, v in labels.items()):
            yield s


AggType = Literal["avg", "sum", "max", "min", "count"]


def aggregate_by(
    samples: Iterable[Sample],
    agg: AggType = "avg",
    labels: Optional[list[str]] = None,
) -> Iterable[Sample]:
    """
    对样本值做聚合分析
    agg: "avg", "sum", "max", "min", "count"
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """

    # 分组
    group_dict = {}
    name = ""
    timestamp = 0.0
    for idx, s in enumerate(assert_samples_consistent(samples)):
        if idx == 0:
            # 取第一个样本的name和timestamp（已校验一致性）
            name = s.name
            timestamp = s.timestamp

        if labels is None:
            group_key = tuple()  # 全部聚合为一组
            group_labels = {}
        else:
            group_key = tuple((k, s.labels.get(k, "")) for k in labels)
            group_labels = {k: s.labels.get(k, "") for k in labels}
        if group_key not in group_dict:
            group_dict[group_key] = {"values": [], "labels": group_labels}
        group_dict[group_key]["values"].append(s.value)

    # 聚合
    for group in group_dict.values():
        values = group["values"]
        group_labels = group["labels"]
        if agg == "avg":
            agg_value = statistics.mean(values)
        elif agg == "sum":
            agg_value = sum(values)
        elif agg == "max":
            agg_value = max(values)
        elif agg == "min":
            agg_value = min(values)
        elif agg == "count":
            agg_value = len(values)
        else:
            raise ValueError(f"Unknown agg: {agg}")

        yield Sample(name, group_labels, agg_value, timestamp)


def sum_by(samples: Iterable[Sample], labels: list[str] = None) -> Iterable[Sample]:
    """
    对样本值做求和
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(samples, "sum", labels)


def avg_by(samples: Iterable[Sample], labels: list[str] = None) -> Iterable[Sample]:
    """
    对样本值做平均值
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(samples, "avg", labels)


def max_by(samples: Iterable[Sample], labels: list[str] = None) -> Iterable[Sample]:
    """
    对样本值做最大值
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(samples, "max", labels)


def min_by(samples: Iterable[Sample], labels: list[str] = None) -> Iterable[Sample]:
    """
    对样本值做最小值
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(samples, "min", labels)


def count_by(samples: Iterable[Sample], labels: list[str] = None) -> Iterable[Sample]:
    """
    对样本值做计数
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(samples, "count", labels)


def group_samples_by_time(samples: Iterable[Sample]) -> dict[float, list[Sample]]:
    """
    按时间戳分组样本
    :param samples: 样本列表
    :return: 时间戳 -> 样本列表的映射
    """
    grouped_samples = defaultdict(list)
    for sample in assert_samples_consistent(samples):
        grouped_samples[sample.timestamp].append(sample)
    return grouped_samples


def get_value_from_metric(
    metric: Metric,
    filter_labels: Optional[dict[str, str]] = None,
    agg: AggType = "avg",
) -> list[tuple[float, float]]:
    """
    从指标中获取值
    :param metric: 指标对象
    :param filter_labels: 过滤条件
    :param agg: 聚合方式
    :return: 指标值
    """
    if not metric:
        return []

    filtered = filter_by_labels(metric.samples, filter_labels)
    grouped_samples = group_samples_by_time(filtered)
    grouped_values: dict[float, float] = {}
    for timestamp, samples in grouped_samples.items():
        aggregated = next(iter(aggregate_by(samples, agg=agg)))
        grouped_values[timestamp] = aggregated.value

    return [
        (timestamp, grouped_values[timestamp])
        for timestamp in sorted(grouped_values.keys())
    ]


def get_value_from_metric_group_by(
    metric: Metric,
    group_labels: list[str],
    filter_labels: Optional[dict[str, str]] = None,
    agg: AggType = "avg",
) -> list[tuple[float, dict[str, float]]]:
    """
    从指标中获取值
    :param metric: 指标对象
    :param group_labels: 分组标签
    :param filter_labels: 过滤条件
    :param agg: 聚合方式
    :return: 指标值
    """
    if not metric:
        return []

    filtered = filter_by_labels(metric.samples, filter_labels)
    grouped_samples = group_samples_by_time(filtered)
    grouped_values: dict[float, dict[str, float]] = {}
    for timestamp, samples in grouped_samples.items():
        aggregated = aggregate_by(samples, agg=agg, labels=group_labels)
        grouped_values[timestamp] = {
            sample.labels.get(group_labels[0], ""): sample.value
            for sample in aggregated
        }

    return [
        (timestamp, grouped_values[timestamp])
        for timestamp in sorted(grouped_values.keys())
    ]
