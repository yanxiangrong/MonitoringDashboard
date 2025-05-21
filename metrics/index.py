from typing import Iterable

from prometheus_client import Metric

from metrics.types import Label, MetricMap
from metrics.utils import check_metric_samples_consistency


def build_metric_map(metrics: Iterable[Metric]) -> MetricMap:
    """
    将 Metric 列表转换为 name -> Metric 的映射
    """
    return {m.name: m for m in metrics}


def aggregate_by(metric: Metric, agg: str = "avg", label: Iterable[str]|None = None) -> Metric:
    """
    对样本值做聚合分析
    agg: "avg", "sum", "max", "min", "count"
    label: 按哪些label分组聚合，None表示全部聚合为一组
    """

    # 校验一致性
    check_metric_samples_consistency(metric)

    if not metric.samples:
        return Metric(metric.name, metric.documentation, metric.type, metric.unit)

    # 分组
    group_dict = {}
    for s in metric.samples:
        if label is None:
            group_key = tuple()  # 全部聚合为一组
            group_labels = {}
        else:
            group_key = tuple((k, s.labels.get(k, "")) for k in label)
            group_labels = {k: s.labels.get(k, "") for k in label}
        if group_key not in group_dict:
            group_dict[group_key] = {"values": [], "labels": group_labels}
        group_dict[group_key]["values"].append(s.value)

    # 聚合
    agg_metric = Metric(metric.name, metric.documentation, metric.type, metric.unit)
    for group in group_dict.values():
        values = group["values"]
        labels = group["labels"]
        if agg == "avg":
            agg_value = sum(values) / len(values)
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

        # 取第一个样本的name和timestamp（已校验一致性）
        sample0 = metric.samples[0]
        agg_metric.add_sample(sample0.name, labels, agg_value, sample0.timestamp)


    return agg_metric

def sum_by(metric: Metric, label: Label = None) -> Metric:
    """
    对样本值做求和
    label: 按哪些label分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "sum", label)
def avg_by(metric: Metric, label: Label = None) -> Metric:
    """
    对样本值做平均值
    label: 按哪些label分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "avg", label)
def max_by(metric: Metric, label: Label = None) -> Metric:
    """
    对样本值做最大值
    label: 按哪些label分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "max", label)

def min_by(metric: Metric, label: Label = None) -> Metric:
    """
    对样本值做最小值
    label: 按哪些label分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "min", label)

def count_by(metric: Metric, label: Label = None) -> Metric:
    """
    对样本值做计数
    label: 按哪些label分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "count", label)
