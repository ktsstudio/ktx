import importlib.util

has_open_telemetry = importlib.util.find_spec("opentelemetry") is not None
has_sentry = importlib.util.find_spec("sentry_sdk") is not None
