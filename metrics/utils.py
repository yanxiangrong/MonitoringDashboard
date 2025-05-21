from prometheus_client import Metric


def check_metric_samples_consistency(metric: Metric) -> bool:
    """
    检查Metric的所有Sample是否具有相同的name和timestamp
    """
    if not metric.samples:
        return True  # 空样本视为一致

    first_name = metric.samples[0].name
    first_ts = metric.samples[0].timestamp

    for s in metric.samples:
        if s.name != first_name or s.timestamp != first_ts:
            return False
    return True

def assert_metric_samples_consistency(metric: Metric):
    if not check_metric_samples_consistency(metric):
        raise ValueError("All samples in the metric must have the same name and timestamp")
