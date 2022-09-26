from .truncated_normal_generator import TruncatedNormalGenerator


class TeacherVariable:
    """Class representing a teacher variable, e.g. quality or control.
    The base value is randomly generated (using a truncnorm distribution)
    from `mean` and `sd`; the current value is generated from the base
    value and `variation_sd`.

    :param float mean: mean for the base value
    :param float sd: SD for the base value
    :param float variation_sd: SD for the current value
    :param numpy.random.Generator rng: random number generator to use
    :param batch_size: number of values to generate at once
    :param convergence_rate: how fast teacher variables converge towards their mean value in one school
    :param teacher_factor: an experimental factor to modify the current value depending on current dynamics (for example, of pupils' progress)
    :attr current_value: current value of the variable
    """

    def __init__(
        self,
        mean,
        sd,
        variation_sd,
        rng,
        batch_size,
        convergence_rate,
        teacher_factor=0,
    ):
        self.mean = mean
        self.sd = sd
        self.variation_sd = variation_sd
        self.convergence_rate = convergence_rate
        self.convergence_factor = 1.0
        self.teacher_factor = teacher_factor

        if self.sd > 0:
            self.base_value = TruncatedNormalGenerator.get_single_value(
                mean,
                sd,
                lower=0,
                rng=rng,
            )
        else:
            self.base_value = mean

        if variation_sd > 0:
            self.tng = TruncatedNormalGenerator(
                self.base_value,
                variation_sd,
                lower=0,
                rng=rng,
                batch_size=batch_size,
            )
        else:
            self.tng = None

        self.current_value = self.base_value
        self.update_current_value()

    def update_convergence_factor(self):
        """Updates the convergence factors"""
        if self.convergence_factor > 0.1:
            self.convergence_factor *= 1 - self.convergence_rate

    def update_current_value(self, convergence_rate=0, diff=0):
        """Updates the instance's current_values"""
        if self.tng:
            next_value = self.tng.get_value()
            next_value = self.mean + self.convergence_factor * (next_value - self.mean)
            self.current_value = (
                next_value
                + self.convergence_factor
                * self.variation_sd
                * self.teacher_factor
                * diff
            )
