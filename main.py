from collections import deque

from metrics.analyze import analyze_all
from metrics.collect import collect_metrics
from metrics.index import index_samples

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


def main():
    samples = list(collect_metrics(EXPORTER_URL))
    index = index_samples(samples)
    result = analyze_all(index)
    print(result)


if __name__ == "__main__":
    main()
