import time
from typing import Generator, Any, TypeAlias

import requests
from prometheus_client.parser import text_string_to_metric_families
from prometheus_client.samples import Sample

TimedSample:TypeAlias  = tuple[Sample, float]

def collect_metrics(url: str) -> Generator[TimedSample, Any, None]:
    """
    Collect metrics from the given URL.
    Args:
        url (str): The URL to collect metrics from.
    Yields:
        TimedSample: A tuple containing the sample and the scrape time.
    """
    resp = requests.get(url)
    resp.raise_for_status()
    scrape_time = time.time()
    for family in text_string_to_metric_families(resp.text):
        for sample in family.samples:
            yield sample, scrape_time
