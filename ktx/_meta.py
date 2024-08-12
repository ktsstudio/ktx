import importlib.util
import sys

PY311 = sys.version_info >= (3, 11)
has_open_telemetry = importlib.util.find_spec("opentelemetry") is not None
has_sentry = importlib.util.find_spec("sentry_sdk") is not None
