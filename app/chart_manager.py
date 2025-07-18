class ChartManager:
    def __init__(self, root):
        self.root = root
        self.charts = []
        self._init_charts()

    def _init_charts(self):
        # 创建并布局所有图表
        pass

    def add_chart(self, chart):
        # 负责布局和管理
        pass

    def draw_charts(self):
        for chart in self.charts:
            chart.draw_chart()
