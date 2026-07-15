def pytest_configure(config):
    config.addinivalue_line("markers", "slow: exercises the AMPL/CPLEX solver (skip with -m 'not slow')")
