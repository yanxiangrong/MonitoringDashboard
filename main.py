import time
from typing import Any, Generator, Tuple

import requests
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


def collect_metrics(url: str) -> Generator[tuple[Sample, float], Any, None]:
    resp = requests.get(url)
    resp.raise_for_status()
    scrape_time = time.time()
    for family in text_string_to_metric_families(resp.text):
        for sample in family.samples:
            yield sample, scrape_time


def main():
    for sample, ts in collect_metrics(EXPORTER_URL):
        print(sample, ts)


if __name__ == "__main__":
    main()
