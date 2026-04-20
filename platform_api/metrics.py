from prometheus_client import Counter, Histogram, CollectorRegistry

metrics_registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "platform_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
    registry=metrics_registry,
)

REQUEST_LATENCY = Histogram(
    "platform_request_duration_seconds",
    "HTTP request latency in seconds",
    ["path"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
    registry=metrics_registry,
)
