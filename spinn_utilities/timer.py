import datetime


class Timer(object):
    """ A timer used for performance measurements
    """

    __slots__ = [

        # The start time when the timer was set off
        "_start_time",

        # The time in the measured section
        "_measured_section_interval"
    ]

    def __init__(self):
        self._start_time = None
        self._measured_section_interval = None

    def start_timing(self):
        self._start_time = datetime.datetime.now()

    def take_sample(self):
        time_now = datetime.datetime.now()
        diff = time_now - self._start_time
        return diff

    def __enter__(self):
        self.start_timing()
        return self

    def __exit__(self, *args):
        self._measured_section_interval = self.take_sample()
        return False

    @property
    def measured_interval(self):
        return self._measured_section_interval
