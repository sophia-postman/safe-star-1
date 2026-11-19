"""
In-memory data store for SafeStar Service API.
"""

# Driver safety profiles keyed by driver id (int)
driver_profiles = {}

# Vehicle safety profiles keyed by vehicle id (int)
vehicle_profiles = {}

# Safety scan runs keyed by run id (int)
runs = {}

# Diagnostic reports keyed by diagnostic id (int)
diagnostics = {}

# Auto-incrementing counters
_run_counter = 0
_diagnostic_counter = 0


def next_run_id():
    global _run_counter
    _run_counter += 1
    return _run_counter


def next_diagnostic_id():
    global _diagnostic_counter
    _diagnostic_counter += 1
    return _diagnostic_counter
