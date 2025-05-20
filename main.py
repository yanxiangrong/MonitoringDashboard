import time

from metrics.analyze import Analyzer
from metrics.collect import collect_metrics
from metrics.index import index_samples

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


def main():
    analyzer = Analyzer()
    # samples = list(collect_metrics(EXPORTER_URL))
    # for sample, _ts in samples:
    #     print(sample)
    while True:
        samples = list(collect_metrics(EXPORTER_URL))
        index = index_samples(samples)
        result = analyzer.analyze_all(index)
        print(result)
        time.sleep(1)


if __name__ == "__main__":
    main()
