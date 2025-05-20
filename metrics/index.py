from prometheus_client.samples import Sample


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
        label_filter: dict = None
) -> list[tuple]:
    """
    从 index 中按 metric_name 和 label_filter 过滤样本

    Args:
        index: {metric_name: [(Sample, ts), ...]}
        metric_name: 指标名
        label_filter: dict，label 过滤条件，如 {"instance": "host1"}，可不填
    Returns:
        list[tuple]: 所有匹配的 (Sample, ts)
    """
    result = []
    samples = index.get(metric_name, [])
    if not label_filter:
        return samples.copy()  # 返回所有样本
    for sample, ts in samples:
        if all(sample.labels.get(k) == v for k, v in label_filter.items()):
            result.append((sample, ts))
    return result
