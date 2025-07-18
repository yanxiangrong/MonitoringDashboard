class DataHistoryManager:
    def __init__(self):
        # 用于保存历史数据，便于后续画图
        self.cpu_history: list[tuple[float, float]] = []
        self.memory_history: list[tuple[float, float]] = []
        self.disk0_history: list[tuple[float, float]] = []
        self.disk1_history: list[tuple[float, float]] = []
        self.network_history_received: list[tuple[float, float]] = []
        self.network_history_sent: list[tuple[float, float]] = []
        self.cpu_heatmap_history: list[tuple[float, list[float]]] = []
        self.memory_commit_history: list[tuple[float, float]] = []
        self.logical_disk_space_values: list[tuple[str, float, float]] = []
        self.gpu_history: list[tuple[float, float]] = []
