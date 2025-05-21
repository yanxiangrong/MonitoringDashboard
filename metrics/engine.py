import collections
import threading
import time
from typing import Callable, Any, TypeAlias

from prometheus_client import CollectorRegistry

from metrics.analyze import MetricAnalyzer

# 回调类型：metric, labels, scrape_time
MetricCallback: TypeAlias= Callable[[], None]

class MetricEngine:
    def __init__(self, interval: float = 2.0, history_length: int = 300):
        """
        interval: 采集周期（秒）
        history_length: 每个表达式/指标保留的历史点数
        """
        self.registry = CollectorRegistry()
        self.analyzers: list[MetricAnalyzer] = []
        self.update_callbacks: list[MetricCallback] = []
        self.history = collections.defaultdict(list)  # name -> list of (timestamp, value)
        self.interval = interval
        self.history_length = history_length
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def register_collector(self, collector):
        """注册一个采集器（Collector），如 Gauge/Counter/自定义采集器"""
        self.registry.register(collector)

    def register_analyzer(self, analyzer: MetricAnalyzer):
        self.analyzers.append(analyzer)
    def register_on_update(self,  callback: MetricCallback):
        """
        注册回调：当 metric_name 且 labels 匹配时，调用 callback
        """
        self.update_callbacks.append(callback)

    def register_expression(self, name: str, expr_func: Callable[[CollectorRegistry], Any], callback: Callable[[float, Any], None] = None):
        """
        注册一个表达式/公式
        expr_func: 一个函数，参数为 registry，返回计算结果
        callback: 可选，结果更新时触发
        """
        self.expressions[name] = (expr_func, callback)

    def start(self):
        """启动定时采集线程"""
        self._stop_event.clear()
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        """停止采集线程"""
        self._stop_event.set()
        self._thread.join()

    def get_metric_value(self, metric_name: str, labels: Dict[str, str]) -> float:
        label_key = frozenset(labels.items())
        history = self._history.get(metric_name, {}).get(label_key, [])
        return history[-1][1] if history else None

    def get_metric_history(self, metric_name: str, labels: Dict[str, str], start_time: float, end_time: float) -> List[Tuple[float, float]]:
        label_key = frozenset(labels.items())
        history = self._history.get(metric_name, {}).get(label_key, [])
        return [(ts, val) for ts, val in history if start_time <= ts <= end_time]
    
    def _run(self):
        while not self._stop_event.is_set():
            # 采集所有指标
            metrics = self.registry.collect()
            scrape_time = time.time()
            # 计算所有表达式
            for analyzer in self.analyzers:
                new_metrics  = analyzer.analyze(metrics, scrape_time)
                for metric in new_metrics:
                    cbs = self._update_callbacks.get(metric.name, [])
                    for label_filter, cb in cbs:
                        if all(metric.labels.get(k) == v for k, v in label_filter.items()):
                            cb(metric.value, metric.labels, scrape_time)

            for callback in self.update_callbacks:
                callback()
            for name, (expr_func, callback) in self.expressions.items():
                try:
                    value = expr_func(self.registry)
                    self.history[name].append((now, value))
                    # 保留历史长度
                    if len(self.history[name]) > self.history_length:
                        self.history[name] = self.history[name][-self.history_length:]
                    if callback:
                        callback(now, value)
                except Exception as e:
                    print(f"Expression {name} error: {e}")
            time.sleep(self.interval)

    def get_history(self, name: str, since: float = None) -> list[tuple]:
        """
        获取某个表达式/指标的历史时序
        since: 只返回该时间戳之后的点
        """
        data = self.history.get(name, [])
        if since is not None:
            return [(ts, v) for ts, v in data if ts >= since]
        return data
