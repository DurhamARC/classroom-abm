import pickle
import time

from model.truncated_normal_generator import TruncatedNormalGenerator


def _check_values_in_range(tng, lower, upper, n_vals=1000):
    prev = lower - 1
    for i in range(n_vals):
        val = tng.get_value()
        assert type(val) == float
        assert val != prev
        assert val >= lower
        assert val <= upper
        prev = val


def test_simple():
    # Check values are in given range
    tng = TruncatedNormalGenerator(5, 10, 1, 8)
    _check_values_in_range(tng, 1, 8)

    # Check range is set to mean += 3 * sd
    tng = TruncatedNormalGenerator(10, 2)
    _check_values_in_range(tng, 4, 16)


def test_small_batch():
    # Check generating new batches of numbers works
    tng = TruncatedNormalGenerator(10, 2, batch_size=10)
    _check_values_in_range(tng, 4, 16)


def test_large_batch():
    # Check it doesn't take too long to generate 5m vals
    n_vals = 5000000
    start_time = time.time()
    tng = TruncatedNormalGenerator(10, 2, batch_size=n_vals)
    _check_values_in_range(tng, 4, 16, n_vals)
    end_time = time.time()
    assert end_time - start_time < 20


def test_get_single_value():
    prev = -1
    for i in range(1000):
        val = TruncatedNormalGenerator.get_single_value(5, 10, 1, 8)
        assert type(val) == float
        assert val != prev
        assert val >= 1
        assert val <= 8

    for i in range(100):
        val = TruncatedNormalGenerator.get_single_value(10, 2)
        assert type(val) == float
        assert val != prev
        assert val >= 4
        assert val <= 16


def test_pickle():
    tng = TruncatedNormalGenerator(10, 2)
    tng.get_value()
    tng.get_value()
    assert tng.iterator.iterindex == 2

    new_tng = pickle.loads(pickle.dumps(tng))
    assert new_tng.iterator.iterindex == 2
    new_tng.get_value()
    assert new_tng.iterator.iterindex == 3
