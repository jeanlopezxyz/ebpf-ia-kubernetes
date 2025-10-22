# Gunicorn configuration for ML Detector with enhanced logging

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "gthread"
threads = 4
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = False
timeout = 30
keepalive = 2

# Logging
capture_output = True
enable_stdio_inheritance = True

# Log to stdout/stderr for Kubernetes
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Access log format (more detailed)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'ml-detector'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL (disabled for internal cluster communication)
keyfile = None
certfile = None

# Worker recycling
max_requests = 1000
max_requests_jitter = 50

# Debugging
reload = False
reload_engine = 'auto'
reload_extra_files = []
spew = False
check_config = False
print_config = False

# Process naming
proc_name = 'ml-detector-gunicorn'

def when_ready(server):
    """Called when the server is started."""
    server.log.info("🚀 ML Detector server is ready to accept connections")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info("👷 Worker %s received INT signal", worker.pid)

def pre_fork(server, worker):
    """Called before a worker is forked."""
    server.log.info("👶 About to fork worker %s", worker.pid)

def post_fork(server, worker):
    """Called after a worker is forked."""
    server.log.info("✅ Worker %s spawned", worker.pid)

def pre_exec(server):
    """Called before the master starts."""
    server.log.info("🎬 Master starting")

def on_exit(server):
    """Called when the master exits."""
    server.log.info("🛑 Master exiting")

def worker_abort(worker):
    """Called when a worker receives a SIGABRT signal."""
    worker.log.info("💥 Worker %s aborted", worker.pid)