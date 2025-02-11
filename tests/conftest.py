import pytest


@pytest.fixture
def sample_log_entries():
    """Fixture generates test data"""
    yield iter(
        [
            {
                "url": "/api/test",
                "count": 10,
                "count_perc": 50.0,
                "time_sum": 20.0,
                "time_perc": 40.0,
                "time_avg": 2.0,
                "time_max": 5.0,
                "time_med": 2.0,
            }
        ]
    )
