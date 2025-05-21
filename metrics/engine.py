import threading
import time
from collections import deque
from typing import Callable, TypeAlias, Deque, Iterable

from prometheus_client import CollectorRegistry, Metric

from metrics.analyze import MetricAnalyzer
from metrics.index import filter_by

# 回调类型：metric, labels, scrape_time
MetricCallback: TypeAlias = Callable[[], None]


class MetricEngine:
    def __init__(self, interval: float = 2.0, history_size: int = 300):
        """
        interval: 采集周期（秒）
        history_length: 每个表达式/指标保留的历史点数
        """
        self.registry = CollectorRegistry()
        self.analyzers: list[MetricAnalyzer] = []
        self.update_callbacks: list[MetricCallback] = []
        self.history: Deque[tuple[float, dict[str, Metric]]] = deque(
            maxlen=history_size
        )
        self.history_size = history_size
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def register_collector(self, collector):
        """
        注册一个指标采集器（Collector），用于采集指标数据
        :param collector: 指标采集器实例
        :type collector: Collector
        """
        self.registry.register(collector)

    def register_analyzer(self, analyzer: MetricAnalyzer):
        """
        注册一个分析器（Analyzer），用于分析采集到的指标数据
        :param analyzer: 分析器实例
        :type analyzer: MetricAnalyzer
        """
        self.analyzers.append(analyzer)

    def register_on_update(self, callback: MetricCallback):
        """
        注册一个回调函数，当采集到新数据时会调用该函数
        :param callback: 回调函数，参数为采集到的指标数据
        :type callback: MetricCallback
        """
        self.update_callbacks.append(callback)

    def start(self):
        """
        启动采集线程
        """
        self._stop_event.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        """
        停止采集线程
        """
        self._stop_event.set()
        self._thread.join()

    def get_metric(
        self, metric_name: str, labels: dict[str, str] | None = None
    ) -> Metric | None:
        """
        获取最新的指定 metric，并按 labels 过滤。
        """
        if not self.history or metric_name not in self.history[-1][1]:
            return None
        return filter_by(self.history[-1][1][metric_name], labels=labels)

    def get_metric_range(
        self,
        metric_name: str,
        start_time: float,
        end_time: float | None = None,
        labels: dict[str, str] | None = None,
    ) -> Iterable[Metric]:
        """
        获取指定时间范围内的 metric 数据，并按 labels 过滤。
        :param metric_name: 指标名称
        :param start_time: 开始时间（时间戳）
        :param end_time: 结束时间（时间戳），None表示当前时间
        :param labels: 按哪些labels过滤，None表示不过滤
        """
        if end_time is None:
            end_time = time.time()
        return (
            filter_by(m[metric_name], labels=labels)
            for t, m in self.history
            if start_time <= t <= end_time and metric_name in m
        )

    def _run(self):
        while not self._stop_event.is_set():
            # 采集所有指标
            metrics = self.registry.collect()
            scrape_time = time.time()
            # 计算所有表达式
            all_metric_dict: dict[str, Metric] = {
                m.name: m
                for analyzer in self.analyzers
                for m in analyzer.analyze(metrics, scrape_time)
            }
            # 更新历史
            self.history.append((scrape_time, all_metric_dict))
            # 执行回调
            for callback in self.update_callbacks:
                callback()
            # 等待下次采集
            time.sleep(self.interval)
