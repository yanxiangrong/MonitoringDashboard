from typing import TypeAlias

from metrics.collect import TimedSample

TimedSampleList = list[TimedSample]
GroupedSamples: TypeAlias = dict[str, list[TimedSample]]
Label : TypeAlias = dict[str, str]


def index_samples(samples: TimedSampleList) -> GroupedSamples:
    """
    按 metric 名称分组，返回字典
    """
    index: GroupedSamples = {}
    for sample, ts in samples:
        index.setdefault(sample.name, []).append((sample, ts))
    return index


def get_samples_by_labels(
        index: GroupedSamples,
        metric_name: str,
        label_filter: Label  = None
) -> TimedSampleList:
    """
    从 index 中按 metric_name 和 label_filter 过滤样本

    Args:
        index (GroupedSamples): 分组后的样本索引
        metric_name (str): 指定的 metric 名称
        label_filter (Label): 标签过滤器，字典形式，键为标签名，值为标签值
    Returns:
        TimedSampleList: 过滤后的样本列表
    """
    result = []
    samples = index.get(metric_name, [])
    if not label_filter:
        return samples.copy()  # 返回所有样本
    for sample, ts in samples:
        if all(sample.labels.get(k) == v for k, v in label_filter.items()):
            result.append((sample, ts))
    return result
