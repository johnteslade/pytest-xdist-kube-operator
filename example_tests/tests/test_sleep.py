import time

import pytest


@pytest.mark.parametrize("num", range(5))
def test_sleep(num):
    time.sleep(10)
