import time

from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


def main():
    engine = MetricEngine(interval=2)

    # 注册远程采集器
    engine.register_collector(RemoteMetricsCollector(EXPORTER_URL))
    engine.start()
    time.sleep(10)
    engine.stop()


if __name__ == "__main__":
    main()
