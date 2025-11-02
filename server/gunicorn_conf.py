import multiprocessing
from config import settings

# Socket binding
bind = f"0.0.0.0:{settings.CLOUD_PORT}"

# Worker processes (оптимально для I/O bound приложений)
workers = multiprocessing.cpu_count() * 2

# Используем uvicorn workers для ASGI
worker_class = "uvicorn.workers.UvicornWorker"

# Performance settings
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 120
keepalive = 2

# Logging
accesslog = "/var/log/wakelink/access.log"
errorlog = "/var/log/wakelink/error.log"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "wakelink_cloud_server"