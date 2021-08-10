import numpy as np
from scipy import stats


class TruncatedNormalGenerator:
    """
    Class to generate values from a truncated normal distribution with
    a given mean and standard deviation, capped by given lower and
    upper limits (or by the mean +/- 3 times the standard deviation if the
    limits are not specified).
    This can be used instead of a normal distribution in cases where e.g. you
    want to avoid using a negative value, or you need be sure the value will
    be in a particular range.
    """

    def __init__(self, mean, sd, lower=None, upper=None, rng=None, batch_size=1000):
        if lower is None:
            lower = mean - 3 * sd
        if upper is None:
            upper = mean + 3 * sd

        self.rng = rng or np.random.default_rng()
        self.tn_gen = stats.truncnorm(
            (lower - mean) / sd, (upper - mean) / sd, loc=mean, scale=sd
        )
        self.batch_size = batch_size
        self._generate_values()

    def _generate_values(self):
        self.values = self.tn_gen.rvs(self.batch_size, random_state=self.rng)
        self.iterator = np.nditer(self.values)

    def get_value(self):
        """
        Return a single value from the truncated normal distribution
        """
        if self.iterator.finished:
            self._generate_values()

        val = self.iterator[0].item()
        self.iterator.iternext()
        return val

    def __getstate__(self):
        # Override getstate to remove the unpickleable iterator
        state = self.__dict__.copy()
        # Save the iterator index
        state["iterindex"] = self.iterator.iterindex
        # Remove the unpicklable entries.
        del state["iterator"]
        return state

    def __setstate__(self, state):
        # Pop iterindex to remove from state
        iterindex = state.pop("iterindex")
        # Restore instance attributes
        self.__dict__.update(state)
        # Recreate the iterator and reset its index
        self.iterator = np.nditer(self.values)
        self.iterator.iterindex = iterindex

    @staticmethod
    def get_single_value(mean, sd, lower=None, upper=None, rng=None):
        """
        Get a single value from a truncated normal distribution.
        N.B. This method is inefficient if generating multiple values with the
        parameters; in that case create a `TruncatedNormalGenerator` instance
        and use `get_value`
        """
        tng = TruncatedNormalGenerator(mean, sd, lower, upper, rng, batch_size=1)
        return tng.get_value()
