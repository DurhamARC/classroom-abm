import logging

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class TruncatedNormalGenerator:
    """
    Class to generate values from a truncated normal distribution with
    a given mean and standard deviation, capped by given lower and
    upper limits (or by the mean +/- 3 times the standard deviation if the
    limits are not specified).
    This can be used instead of a normal distribution in cases where e.g. you
    want to avoid using a negative value, or you need be sure the value will
    be in a particular range, or when standard deviation is updated due convergence of random variables after a given convergence_rate period
    """

    def __init__(self, mean, sd, lower=None, upper=None, rng=None, batch_size=1000, convergence_rate=0):
        self.mean = mean
        self.sd = sd
        self.lower = lower
        self.upper = upper
        self.convergence_rate = convergence_rate

        # Quick fix for 0 SD - just use a very small value
        if self.sd == 0:
            self.sd = 0.000001

        if lower is None:
            self.lower = self.mean - 3 * self.sd
        if upper is None:
            self.upper = self.mean + 3 * self.sd

        self.rng = rng or np.random.default_rng()
        self.tn_gen = stats.truncnorm(
            (self.lower - self.mean) / self.sd, (self.upper - self.mean) / self.sd, loc=self.mean, scale=self.sd
        )
        self.batch_size = batch_size
        self._generate_values()

    def _generate_values(self, batch_size=0):
        logger.debug("Generating new values, batch size: %s, mean: %s, standard deviation: %s, convergence rate %s", self.batch_size, self.mean, self.sd, self.convergence_rate)
        self.values = self.tn_gen.rvs(self.batch_size, random_state=self.rng)
        self.iterator = np.nditer(self.values)
        if self.convergence_rate > 0 and self.convergence_rate <= 1:
        #    if batch_size > 0:
        #       self.batch_size = batch_size
            self.sd = self.sd * (1 - self.convergence_rate)
        #   if self.sd < min_similarity_threshold:
        ##       self.sd = min_similarity_threshold
            self.tn_gen = stats.truncnorm(
                (self.lower - self.mean) / self.sd, (self.upper - self.mean) / self.sd, loc=self.mean, scale=self.sd
            )

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
