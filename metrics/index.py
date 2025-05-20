from typing import Iterable

from black.trans import defaultdict
from prometheus_client.samples import Sample

from metrics.types import Samples, GroupedSamples, Label


def group_by_name(samples: Samples) -> GroupedSamples:
    """
    按 metric 名称分组，返回字典
    """
    index = defaultdict(list)
    for sample, ts in samples:
        index[sample.name].append(samples)
    return index


def filter_by_labels(samples: Samples, labels: Label = None) -> Iterable[Sample]:
    """
    从 index 中按 metric_name 和 label_filter 过滤样本

    Args:
        samples (Samples): 样本列表
        labels (Label): 标签过滤器，字典格式，键为标签名，值为标签值
    Returns:
        TimedSampleList: 过滤后的样本列表
    """
    if not labels:
        return samples  # 返回所有样本
    return [
        sample for sample in samples
        if all(sample.labels.get(k) == v for k, v in labels.items())
    ]

def aggregate_by_labels(samples: Samples,label:Label = None, agg: str = "avg") -> Sample:
    """
    对样本值做聚合分析
    agg: "avg", "sum", "max", "min", "count"
    """
    values = [float(sample.value) for sample in filter_by_labels(samples, label)]
    if not values:
        return
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
