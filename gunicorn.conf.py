import os

# ============================================================
# GUNICORN CONFIGURATION FOR KISANSATHI AI ON RENDER
# Designed to fit within Render Free/Starter Tier (512MB RAM)
# ============================================================

# Single worker process is MANDATORY for running TensorFlow on 512MB RAM.
# Multiple workers load duplicate copies of TensorFlow and weights,
# immediately exceeding RAM and triggering OS SIGKILL.
workers = 1

# Multi-threading allows the single worker to handle concurrent requests
# without spawning additional heavyweight Python processes.
threads = int(os.getenv("GUNICORN_THREADS", 2))

# Timeout in seconds. Deep learning model inference on shared vCPUs may take
# several seconds; 120s avoids premature worker restarts during inference.
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))

# Graceful worker recycling: restart worker after processing N requests
# to reclaim any fragmented memory or uncollected C++ tensor buffers.
max_requests = 100
max_requests_jitter = 20

# Port binding (Render sets PORT automatically)
port = os.getenv("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
capture_output = True
enable_stdio_inheritance = True
