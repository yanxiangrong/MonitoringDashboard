import bisect
import threading
import time
from collections import deque
from typing import Callable, Deque, Optional

from prometheus_client import CollectorRegistry, Metric

from metrics.analyze import MetricAnalyzer
from metrics.index import filter_by_labels, build_metric_map

# 回调类型：metric, labels, scrape_time
MetricCallback = Callable[[], None]


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
        self, metric_name: str, labels: Optional[dict[str, str]] = None
    ) -> Optional[Metric]:
        """
        获取最新的指定 metric，并按 labels 过滤。
        """
        if not self.history or metric_name not in self.history[-1][1]:
            return None

        metric = self.history[-1][1][metric_name]
        if labels is None:
            return metric

        filed_metric = Metric(
            metric.name, metric.documentation, metric.type, metric.unit
        )
        filed_metric.samples = list(filter_by_labels(metric.samples, labels=labels))
        return filed_metric

    def get_metric_range(
        self,
        metric_name: str,
        start_time: float,
        end_time: Optional[float] = None,
        labels: Optional[dict[str, str]] = None,
    ) -> Optional[Metric]:
        """
        获取指定时间范围内的 metric 数据，并按 labels 过滤。
        :param metric_name: 指标名称
        :param start_time: 开始时间（时间戳）
        :param end_time: 结束时间（时间戳），None表示当前时间
        :param labels: 按哪些labels过滤，None表示不过滤
        """
        if not self.history:
            return None

        if end_time is None:
            end_time = time.time()

        keys = [x[0] for x in self.history]
        start_idx = bisect.bisect_left(keys, start_time)
        end_idx = len(self.history)
        filed_metric: Metric | None = None
        for i in range(start_idx, end_idx):
            scrape_time, metric_dict = self.history[i]
            if scrape_time < start_time or scrape_time > end_time:
                continue
            if metric_name not in metric_dict:
                continue
            metric = metric_dict[metric_name]
            if filed_metric is None:
                filed_metric = Metric(
                    metric.name, metric.documentation, metric.type, metric.unit
                )
            if labels is None:
                filed_metric.samples += metric.samples
                continue
            filed_metric.samples += list(
                filter_by_labels(metric.samples, labels=labels)
            )
        return filed_metric

    def get_last_scrape_time(self) -> Optional[float]:
        """
        获取最后一次采集的时间戳
        :return: 最后一次采集的时间戳
        """
        if not self.history:
            return None
        return self.history[-1][0]

    def _run(self):
        next_time = time.time() + self.interval
        while not self._stop_event.is_set():
            # 采集所有指标
            metrics = self.registry.collect()
            # 采集时间
            scrape_time = time.time()
            # 计算所有表达式
            metric_map = build_metric_map(metrics)
            all_metric_dict: dict[str, Metric] = {
                m.name: m
                for analyzer in self.analyzers
                for m in analyzer.analyze(metric_map, scrape_time)
            }
            # 更新历史
            self.history.append((scrape_time, all_metric_dict))
            # 执行回调
            for callback in self.update_callbacks:
                callback()
            # 计算下次采集时间
            now_time = time.time()
            while next_time < now_time:
                next_time += self.interval
            sleep_time = next_time - now_time
            time.sleep(sleep_time)
