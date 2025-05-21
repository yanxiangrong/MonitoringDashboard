import time

from metrics.analyze import CpuUsageAnalyzer, MemoryTrendAnalyzer
from metrics.collect import RemoteMetricsCollector
from metrics.engine import MetricEngine

# Windows Exporter 的地址和端口，默认是9182
EXPORTER_URL = "http://localhost:9182/metrics"


def main():
    engine = MetricEngine(interval=1, history_size=600)

    def print_metrics():
        cpu_usage = engine.get_metric("cpu_usage_percent")
        memory_usage = engine.get_metric("memory_usage_percent")
        print("CPU Usage:", end="")
        for sample in cpu_usage.samples:
            print(f" {sample.labels['core']}: {sample.value:.2f}%", end=",")
        print()
        print(f"Memory Usage: {memory_usage.samples[0].value}%")


    # 注册远程采集器
    engine.register_collector(RemoteMetricsCollector(EXPORTER_URL))
    engine.register_analyzer(CpuUsageAnalyzer())
    engine.register_analyzer(MemoryTrendAnalyzer())
    engine.register_on_update(print_metrics)
    engine.start()
    while True:
        time.sleep(10)
    engine.stop()


if __name__ == "__main__":
    main()
