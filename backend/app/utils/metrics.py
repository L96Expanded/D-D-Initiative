"""Prometheus metrics middleware and endpoint."""
from fastapi import APIRouter, Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from starlette.middleware.base import BaseHTTPMiddleware
from time import time
import psutil
import os

# Create a custom registry
registry = CollectorRegistry()

# Define metrics
request_count = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

request_latency = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    registry=registry
)

request_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint'],
    registry=registry
)

error_count = Counter(
    'http_errors_total',
    'Total number of HTTP errors',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

# Application metrics
app_info = Gauge(
    'app_info',
    'Application information',
    ['version'],
    registry=registry
)

# System metrics
cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'Current CPU usage percentage',
    registry=registry
)

memory_usage = Gauge(
    'system_memory_usage_bytes',
    'Current memory usage in bytes',
    registry=registry
)

# Database metrics
db_connections = Gauge(
    'database_connections_active',
    'Number of active database connections',
    registry=registry
)

# Set app info
VERSION = os.getenv("APP_VERSION", "1.0.0")
app_info.labels(version=VERSION).set(1)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for all requests."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics."""
        # Skip metrics endpoint itself
        if request.url.path == "/api/metrics":
            return await call_next(request)
        
        method = request.method
        path = request.url.path
        
        # Track request in progress
        request_in_progress.labels(method=method, endpoint=path).inc()
        
        # Track request latency
        start_time = time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Track request completion
            request_count.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            # Track errors (4xx and 5xx)
            if status_code >= 400:
                error_count.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()
            
            return response
            
        except Exception as e:
            # Track exceptions as 500 errors
            error_count.labels(
                method=method,
                endpoint=path,
                status_code=500
            ).inc()
            raise e
            
        finally:
            # Record latency
            duration = time() - start_time
            request_latency.labels(method=method, endpoint=path).observe(duration)
            
            # Decrement in-progress counter
            request_in_progress.labels(method=method, endpoint=path).dec()
            
            # Update system metrics
            try:
                cpu_usage.set(psutil.cpu_percent())
                memory_usage.set(psutil.Process().memory_info().rss)
            except:
                pass  # Ignore if psutil is not available


# Router for metrics endpoint
router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Exposes application metrics in Prometheus format.
    """
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )
