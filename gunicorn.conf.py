import os

# Configuración optimizada para Railway
bind = "0.0.0.0:" + str(os.environ.get("PORT", 8080))
workers = 1
timeout = 120  # 2 minutos de timeout
keepalive = 5
worker_class = "sync"
preload_app = True  # ✅ CRÍTICO: Precarga la app antes del fork
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"