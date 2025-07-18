import time
from collections import deque
from typing import Callable, Any, Deque, Tuple, List

class MetricDataService:
    """
    拉模式时序数据服务：每次 get_history 都会实时拉取新数据并缓存。
    """
    def __init__(self, data_source: Callable[[], dict], maxlen: int = 300):
        """
        data_source: 一个无参函数，返回最新的指标数据（如 {"cpu": 12.3, "mem": 45.6}）
        maxlen: 历史数据点数
        """
        self.data_source = data_source
        self.maxlen = maxlen
        # {metric_name: deque([(timestamp, value), ...])}
        self.history: dict[str, Deque[Tuple[float, Any]]] = {}

    def get_history(self) -> dict[str, List[Tuple[float, Any]]]:
        """
        拉取最新数据，加入历史，返回所有历史数据
        """
        now = time.time()
        latest = self.data_source()  # 获取最新数据
        for k, v in latest.items():
            if k not in self.history:
                self.history[k] = deque(maxlen=self.maxlen)
            self.history[k].append((now, v))
        # 返回所有历史
        return {k: list(deq) for k, deq in self.history.items()}
