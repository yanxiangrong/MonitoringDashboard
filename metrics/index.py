from typing import Iterable

from prometheus_client import Metric

from metrics.utils import check_metric_samples_consistency


def build_metric_map(metrics: Iterable[Metric]) -> dict[str, Metric]:
    """
    将 Metric 列表转换为 name -> Metric 的映射
    """
    return {m.name: m for m in metrics}


def filter_by(metric: Metric, labels: dict[str, str] | None = None) -> Metric:
    """
    过滤样本
    labels: 按哪些labels过滤，None表示不过滤
    """
    # 校验一致性
    check_metric_samples_consistency(metric)

    if not metric.samples:
        return Metric(metric.name, metric.documentation, metric.type, metric.unit)

    # 过滤
    filtered_metric = Metric(
        metric.name, metric.documentation, metric.type, metric.unit
    )
    for s in metric.samples:
        if labels is not None and not all(
            s.labels.get(k) == v for k, v in labels.items()
        ):
            continue
        filtered_metric.add_sample(s.name, s.labels, s.value, s.timestamp)

    return filtered_metric


def aggregate_by(
    metric: Metric, agg: str = "avg", labels: Iterable[str] | None = None
) -> Metric:
    """
    对样本值做聚合分析
    agg: "avg", "sum", "max", "min", "count"
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """

    # 校验一致性
    check_metric_samples_consistency(metric)

    if not metric.samples:
        return Metric(metric.name, metric.documentation, metric.type, metric.unit)

    # 分组
    group_dict = {}
    for s in metric.samples:
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


def sum_by(metric: Metric, labels: dict[str, str] = None) -> Metric:
    """
    对样本值做求和
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "sum", labels)


def avg_by(metric: Metric, labels: dict[str, str] = None) -> Metric:
    """
    对样本值做平均值
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "avg", labels)


def max_by(metric: Metric, labels: dict[str, str] = None) -> Metric:
    """
    对样本值做最大值
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "max", labels)


def min_by(metric: Metric, labels: dict[str, str] = None) -> Metric:
    """
    对样本值做最小值
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "min", labels)


def count_by(metric: Metric, labels: dict[str, str] = None) -> Metric:
    """
    对样本值做计数
    labels: 按哪些labels分组聚合，None表示全部聚合为一组
    """
    return aggregate_by(metric, "count", labels)
