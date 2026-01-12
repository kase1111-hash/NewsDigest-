"""
Metrics and Telemetry Collection for NewsDigest.

This module provides a flexible metrics collection system supporting:
- Counter metrics (monotonically increasing values)
- Gauge metrics (point-in-time values)
- Histogram metrics (distribution of values)
- Timer metrics (duration measurements)

Backends:
- InMemoryBackend: For testing and development
- LoggingBackend: Outputs metrics to logger
- StatsD/Prometheus: Can be added via custom backends

Usage:
    from newsdigest.utils.metrics import get_metrics, MetricsConfig

    # Initialize with configuration
    config = MetricsConfig(enabled=True, prefix="newsdigest")
    metrics = get_metrics(config)

    # Record metrics
    metrics.increment("extractions.total")
    metrics.gauge("queue.size", 42)
    metrics.timing("extraction.duration_ms", 150.5)

    # Use timer context manager
    with metrics.timer("operation.duration"):
        do_something()

    # Use decorator
    @metrics.timed("function.duration")
    def my_function():
        pass
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class MetricType(Enum):
    """Types of metrics supported."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """Container for a metric value with metadata."""

    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict[str, str] = field(default_factory=dict)
    unit: str | None = None


@dataclass
class HistogramBuckets:
    """Histogram bucket configuration."""

    buckets: list[float] = field(
        default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    )
    count: int = 0
    total: float = 0.0
    bucket_counts: dict[float, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize bucket counts."""
        self.bucket_counts = {b: 0 for b in self.buckets}
        self.bucket_counts[float("inf")] = 0

    def observe(self, value: float) -> None:
        """Record an observation."""
        self.count += 1
        self.total += value
        for bucket in self.buckets:
            if value <= bucket:
                self.bucket_counts[bucket] += 1
        self.bucket_counts[float("inf")] += 1


@dataclass
class MetricsConfig:
    """Configuration for metrics collection."""

    enabled: bool = True
    prefix: str = "newsdigest"
    default_tags: dict[str, str] = field(default_factory=dict)
    flush_interval_seconds: float = 60.0
    enable_runtime_metrics: bool = True
    histogram_buckets: list[float] = field(
        default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
    )


class MetricsBackend(ABC):
    """Abstract base class for metrics backends."""

    @abstractmethod
    def record(self, metric: MetricValue) -> None:
        """Record a metric value."""

    @abstractmethod
    def flush(self) -> None:
        """Flush any buffered metrics."""

    def close(self) -> None:
        """Close the backend and release resources."""


class InMemoryBackend(MetricsBackend):
    """In-memory metrics backend for testing and development."""

    def __init__(self) -> None:
        self._metrics: list[MetricValue] = []
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, HistogramBuckets] = {}
        self._lock = threading.Lock()

    def record(self, metric: MetricValue) -> None:
        """Record a metric value."""
        with self._lock:
            self._metrics.append(metric)
            if metric.metric_type == MetricType.COUNTER:
                self._counters[metric.name] += metric.value
            elif metric.metric_type == MetricType.GAUGE:
                self._gauges[metric.name] = metric.value
            elif metric.metric_type in (MetricType.HISTOGRAM, MetricType.TIMER):
                if metric.name not in self._histograms:
                    self._histograms[metric.name] = HistogramBuckets()
                self._histograms[metric.name].observe(metric.value)

    def flush(self) -> None:
        """No-op for in-memory backend."""

    def get_counter(self, name: str) -> float:
        """Get current counter value."""
        with self._lock:
            return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float | None:
        """Get current gauge value."""
        with self._lock:
            return self._gauges.get(name)

    def get_histogram(self, name: str) -> HistogramBuckets | None:
        """Get histogram data."""
        with self._lock:
            return self._histograms.get(name)

    def get_all_metrics(self) -> list[MetricValue]:
        """Get all recorded metrics."""
        with self._lock:
            return list(self._metrics)

    def clear(self) -> None:
        """Clear all stored metrics."""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


class LoggingBackend(MetricsBackend):
    """Metrics backend that logs to Python logger."""

    def __init__(self, logger_name: str = "newsdigest.metrics") -> None:
        self._logger = logging.getLogger(logger_name)
        self._buffer: list[MetricValue] = []
        self._lock = threading.Lock()

    def record(self, metric: MetricValue) -> None:
        """Record a metric by logging it."""
        with self._lock:
            self._buffer.append(metric)

    def flush(self) -> None:
        """Flush buffered metrics to log."""
        with self._lock:
            for metric in self._buffer:
                tags_str = ",".join(f"{k}={v}" for k, v in metric.tags.items())
                unit_str = f" {metric.unit}" if metric.unit else ""
                self._logger.info(
                    "metric.%s: %s=%s%s [%s] tags={%s}",
                    metric.metric_type.value,
                    metric.name,
                    metric.value,
                    unit_str,
                    metric.timestamp.isoformat(),
                    tags_str,
                )
            self._buffer.clear()


class CompositeBackend(MetricsBackend):
    """Backend that forwards metrics to multiple backends."""

    def __init__(self, backends: list[MetricsBackend]) -> None:
        self._backends = backends

    def record(self, metric: MetricValue) -> None:
        """Record metric to all backends."""
        for backend in self._backends:
            backend.record(metric)

    def flush(self) -> None:
        """Flush all backends."""
        for backend in self._backends:
            backend.flush()

    def close(self) -> None:
        """Close all backends."""
        for backend in self._backends:
            backend.close()


class NoOpBackend(MetricsBackend):
    """No-operation backend when metrics are disabled."""

    def record(self, metric: MetricValue) -> None:
        """No-op."""

    def flush(self) -> None:
        """No-op."""


class MetricsCollector:
    """Main metrics collection interface."""

    def __init__(
        self,
        config: MetricsConfig | None = None,
        backend: MetricsBackend | None = None,
    ) -> None:
        self._config = config or MetricsConfig()
        self._backend = backend or (
            InMemoryBackend() if self._config.enabled else NoOpBackend()
        )
        self._start_time = time.monotonic()

    @property
    def enabled(self) -> bool:
        """Check if metrics collection is enabled."""
        return self._config.enabled

    @property
    def backend(self) -> MetricsBackend:
        """Get the metrics backend."""
        return self._backend

    def _make_name(self, name: str) -> str:
        """Create full metric name with prefix."""
        if self._config.prefix:
            return f"{self._config.prefix}.{name}"
        return name

    def _make_tags(self, tags: dict[str, str] | None = None) -> dict[str, str]:
        """Merge default tags with provided tags."""
        result = dict(self._config.default_tags)
        if tags:
            result.update(tags)
        return result

    def increment(
        self,
        name: str,
        value: float = 1.0,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Increment a counter metric."""
        if not self._config.enabled:
            return
        metric = MetricValue(
            name=self._make_name(name),
            value=value,
            metric_type=MetricType.COUNTER,
            tags=self._make_tags(tags),
        )
        self._backend.record(metric)

    def decrement(
        self,
        name: str,
        value: float = 1.0,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Decrement a counter (records negative increment)."""
        self.increment(name, -value, tags)

    def gauge(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        unit: str | None = None,
    ) -> None:
        """Set a gauge metric."""
        if not self._config.enabled:
            return
        metric = MetricValue(
            name=self._make_name(name),
            value=value,
            metric_type=MetricType.GAUGE,
            tags=self._make_tags(tags),
            unit=unit,
        )
        self._backend.record(metric)

    def histogram(
        self,
        name: str,
        value: float,
        tags: dict[str, str] | None = None,
        unit: str | None = None,
    ) -> None:
        """Record a histogram observation."""
        if not self._config.enabled:
            return
        metric = MetricValue(
            name=self._make_name(name),
            value=value,
            metric_type=MetricType.HISTOGRAM,
            tags=self._make_tags(tags),
            unit=unit,
        )
        self._backend.record(metric)

    def timing(
        self,
        name: str,
        value_ms: float,
        tags: dict[str, str] | None = None,
    ) -> None:
        """Record a timing metric in milliseconds."""
        if not self._config.enabled:
            return
        metric = MetricValue(
            name=self._make_name(name),
            value=value_ms,
            metric_type=MetricType.TIMER,
            tags=self._make_tags(tags),
            unit="ms",
        )
        self._backend.record(metric)

    @contextmanager
    def timer(
        self,
        name: str,
        tags: dict[str, str] | None = None,
    ) -> Generator[None, None, None]:
        """Context manager for timing operations."""
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.timing(name, elapsed_ms, tags)

    def timed(
        self,
        name: str,
        tags: dict[str, str] | None = None,
    ) -> Callable[[F], F]:
        """Decorator for timing function execution."""

        def decorator(func: F) -> F:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.timer(name, tags):
                    return func(*args, **kwargs)

            return wrapper  # type: ignore[return-value]

        return decorator

    def record_extraction(
        self,
        url: str,
        duration_ms: float,
        success: bool,
        word_count: int = 0,
        source_type: str = "unknown",
    ) -> None:
        """Record metrics for an extraction operation."""
        tags = {"source_type": source_type, "success": str(success).lower()}
        self.increment("extractions.total", tags=tags)
        self.timing("extractions.duration", duration_ms, tags=tags)
        if success:
            self.increment("extractions.success", tags={"source_type": source_type})
            self.histogram("extractions.word_count", word_count, tags=tags)
        else:
            self.increment("extractions.failure", tags={"source_type": source_type})

    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        """Record metrics for an API request."""
        tags = {
            "endpoint": endpoint,
            "method": method,
            "status_code": str(status_code),
        }
        self.increment("api.requests.total", tags=tags)
        self.timing("api.requests.duration", duration_ms, tags=tags)
        if 200 <= status_code < 300:
            self.increment("api.requests.success", tags={"endpoint": endpoint})
        elif status_code >= 400:
            self.increment("api.requests.error", tags=tags)

    def record_error(
        self,
        error_type: str,
        component: str = "unknown",
    ) -> None:
        """Record an error occurrence."""
        self.increment(
            "errors.total",
            tags={"error_type": error_type, "component": component},
        )

    def get_uptime_seconds(self) -> float:
        """Get application uptime in seconds."""
        return time.monotonic() - self._start_time

    def record_runtime_metrics(self) -> None:
        """Record runtime metrics (memory, uptime, etc.)."""
        if not self._config.enable_runtime_metrics:
            return

        self.gauge("runtime.uptime_seconds", self.get_uptime_seconds())

        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            self.gauge("runtime.memory.max_rss_bytes", usage.ru_maxrss * 1024)
            self.gauge("runtime.cpu.user_time_seconds", usage.ru_utime)
            self.gauge("runtime.cpu.system_time_seconds", usage.ru_stime)
        except (ImportError, AttributeError):
            pass

    def flush(self) -> None:
        """Flush any buffered metrics."""
        self._backend.flush()

    def close(self) -> None:
        """Close the metrics collector."""
        self.flush()
        self._backend.close()


# Global metrics instance
_metrics_instance: MetricsCollector | None = None
_metrics_lock = threading.Lock()


def get_metrics(config: MetricsConfig | None = None) -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _metrics_instance
    with _metrics_lock:
        if _metrics_instance is None:
            _metrics_instance = MetricsCollector(config)
        return _metrics_instance


def configure_metrics(
    config: MetricsConfig | None = None,
    backend: MetricsBackend | None = None,
) -> MetricsCollector:
    """Configure and return the global metrics collector."""
    global _metrics_instance
    with _metrics_lock:
        if _metrics_instance is not None:
            _metrics_instance.close()
        _metrics_instance = MetricsCollector(config, backend)
        return _metrics_instance


def reset_metrics() -> None:
    """Reset the global metrics collector (useful for testing)."""
    global _metrics_instance
    with _metrics_lock:
        if _metrics_instance is not None:
            _metrics_instance.close()
        _metrics_instance = None


# Convenience functions using global metrics
def increment(
    name: str,
    value: float = 1.0,
    tags: dict[str, str] | None = None,
) -> None:
    """Increment a counter using global metrics."""
    get_metrics().increment(name, value, tags)


def gauge(
    name: str,
    value: float,
    tags: dict[str, str] | None = None,
) -> None:
    """Set a gauge using global metrics."""
    get_metrics().gauge(name, value, tags)


def timing(
    name: str,
    value_ms: float,
    tags: dict[str, str] | None = None,
) -> None:
    """Record timing using global metrics."""
    get_metrics().timing(name, value_ms, tags)


@contextmanager
def timer(
    name: str,
    tags: dict[str, str] | None = None,
) -> Generator[None, None, None]:
    """Timer context manager using global metrics."""
    with get_metrics().timer(name, tags):
        yield


def timed(
    name: str,
    tags: dict[str, str] | None = None,
) -> Callable[[F], F]:
    """Timer decorator using global metrics."""
    return get_metrics().timed(name, tags)
