import time
from typing import Generator, Any

import requests
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample


def collect_metrics(url: str) -> Generator[tuple[Sample, float], Any, None]:
    """
    Collect metrics from the given URL.
    Args:
        url (str): The URL to collect metrics from.
    Yields:
        tuple[Sample, float]: A tuple containing the sample and the scrape time.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    scrape_time = time.time()
    for family in text_string_to_metric_families(resp.text):
        for sample in family.samples:
            yield sample, scrape_time
