from typing import TYPE_CHECKING

from .index import get_value_from_metric, get_value_from_metric_group_by

if TYPE_CHECKING:
    from app.main_window import MonitoringDashboardApp


def update_metrics(app: "MonitoringDashboardApp"):
    # 这里实现 update_metrics 逻辑
    # 通过 app.engine、app.data_history 等访问数据

    scrape_time = app.engine.get_last_scrape_time()
    cpu_usage_metrics = app.engine.get_metric_range(
        "cpu_usage_percent", scrape_time - 61, scrape_time
    )
    memory_usage_metrics = app.engine.get_metric_range(
        "memory_usage_percent", scrape_time - 61, scrape_time
    )
    memory_commit_metrics = app.engine.get_metric_range(
        "memory_commit_rate_percent", scrape_time - 61, scrape_time
    )
    disk_usage_metrics = app.engine.get_metric_range(
        "disk_io_util_percent", scrape_time - 61, scrape_time
    )
    network_usage_metrics = app.engine.get_metric_range(
        "network_speed_mbps", scrape_time - 61, scrape_time
    )
    logical_disk_total_metrics = app.engine.get_metric("logical_disk_size_bytes")
    logical_disk_free_metrics = app.engine.get_metric("logical_disk_free_bytes")
    gpu_usage_metrics = app.engine.get_metric_range(
        "gpu_usage_percent", scrape_time - 61, scrape_time
    )

    app.data_history.cpu_history = get_value_from_metric(cpu_usage_metrics)
    app.chart_manager.cpu_chart.update_values(
        app.data_history.cpu_history, scrape_time - 60, scrape_time
    )
    app.data_history.memory_history = get_value_from_metric(memory_usage_metrics)
    app.chart_manager.memory_chart.update_values(
        app.data_history.memory_history, scrape_time - 60, scrape_time
    )
    app.data_history.memory_commit_history = get_value_from_metric(
        memory_commit_metrics
    )
    app.chart_manager.memory_commit_chart.update_values(
        app.data_history.memory_commit_history, scrape_time - 60, scrape_time
    )
    app.data_history.disk0_history = get_value_from_metric(
        disk_usage_metrics, {"disk": "0"}
    )
    app.data_history.disk1_history = get_value_from_metric(
        disk_usage_metrics, {"disk": "1"}
    )
    app.chart_manager.disk0_chart.update_values(
        app.data_history.disk0_history, scrape_time - 60, scrape_time
    )
    app.chart_manager.disk1_chart.update_values(
        app.data_history.disk1_history, scrape_time - 60, scrape_time
    )
    app.data_history.network_history_received = get_value_from_metric(
        network_usage_metrics, {"direction": "received"}
    )
    app.chart_manager.network_chart_received.update_values(
        app.data_history.network_history_received, scrape_time - 60, scrape_time
    )
    app.data_history.network_history_sent = get_value_from_metric(
        network_usage_metrics, {"direction": "sent"}
    )
    app.chart_manager.network_chart_sent.update_values(
        app.data_history.network_history_sent, scrape_time - 60, scrape_time
    )

    logical_disk_space_values_map: dict[str, tuple[float, float]] = {}
    if logical_disk_total_metrics:
        for disk in logical_disk_total_metrics.samples:
            disk_name = disk.labels.get("volume", "")
            if not disk_name:
                continue
            logical_disk_space_values_map[disk_name] = (0, disk.value)
        for disk in logical_disk_free_metrics.samples:
            disk_name = disk.labels.get("volume", "")
            if disk_name not in logical_disk_space_values_map:
                continue
            logical_disk_space_values_map[disk_name] = (
                disk.value,
                logical_disk_space_values_map[disk_name][1],
            )
        app.data_history.logical_disk_space_values = [
            (disk_name, free_space, total_space)
            for disk_name, (
                free_space,
                total_space,
            ) in logical_disk_space_values_map.items()
        ]
        app.chart_manager.logical_disk_usage_chart.update_values(
            app.data_history.logical_disk_space_values
        )

    heatmap_map = get_value_from_metric_group_by(
        cpu_usage_metrics,
        ["core"],
    )

    # 处理 CPU 热力图数据
    def sort_key(item):
        x, y = map(int, item[0].split(","))
        return (x + 1) * y

    app.data_history.cpu_heatmap_history = [
        (timestamp, [value for _, value in sorted(values.items(), key=sort_key)])
        for timestamp, values in heatmap_map
    ]
    app.chart_manager.cpu_heatmap_chart.update_values(
        app.data_history.cpu_heatmap_history, scrape_time - 60, scrape_time
    )
    app.data_history.gpu_history = get_value_from_metric(
        gpu_usage_metrics, {"device": "0"}
    )
    app.chart_manager.gpu_chart.update_values(
        app.data_history.gpu_history, scrape_time - 60, scrape_time
    )
