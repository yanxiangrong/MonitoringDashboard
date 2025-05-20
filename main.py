import requests
from prometheus_client.parser import text_string_to_metric_families

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"

def collect_metrics(url:str):
    resp = requests.get(url)
    resp.raise_for_status()
    metrics = {}
    for family in text_string_to_metric_families(resp.text):
        for sample in family.samples:
            name, labels, value = sample
            metrics.setdefault(name, []).append((labels, value))
    return metrics
