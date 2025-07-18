from app.config_types import AppConfig

DEFAULT_CONFIG: AppConfig = {
    "url": "http://localhost:9182/metrics",
    "fullscreen": False,
    "title": "Monitoring Dashboard",
    "refresh_interval": 5.0,  # Refresh interval in seconds
    "fetch_timeout": 0.5,  # Data fetch timeout in seconds
}
