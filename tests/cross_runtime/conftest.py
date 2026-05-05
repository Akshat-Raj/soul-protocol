def pytest_configure(config):
    config.addinivalue_line("markers", "cross_runtime: marks tests for .soul round-trip")