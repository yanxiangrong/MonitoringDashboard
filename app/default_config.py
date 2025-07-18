from app.config_types import AppConfig

DEFAULT_CONFIG: AppConfig = {
    "url": "http://localhost:9182/metrics",
    "fullscreen": False,
    "title": "Monitoring Dashboard",
    "refresh_interval": 1.0,  # Refresh interval in seconds
    "fetch_timeout": 0.5,  # Data fetch timeout in seconds
    "history_length": 600,  # History length in seconds
}
