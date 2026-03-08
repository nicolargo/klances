from importlib.metadata import PackageNotFoundError, version

try:
    KLANCES_VERSION = version("klances")
except PackageNotFoundError:
    KLANCES_VERSION = "unknown"

API_VERSION = "1"
