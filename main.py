from collections import deque

from metrics.analyze import analyze_all
from metrics.collect import collect_metrics
from metrics.index import index_samples

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"

HISTORY_LEN = 60 *15
history = deque(maxlen=HISTORY_LEN)

def collect_and_store(url, history):
    samples = list(collect_metrics(url))
    history.append(samples)

def main():
    samples = list(collect_metrics(EXPORTER_URL))
    index = index_samples(samples)
    result = analyze_all(index)
    print(result)


if __name__ == "__main__":
    main()
