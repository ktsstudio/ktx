import importlib.util
import sys

PY311 = sys.version_info >= (3, 11)
has_sentry = importlib.util.find_spec("sentry_sdk") is not None
