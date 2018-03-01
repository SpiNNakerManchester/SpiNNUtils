import logging
import inspect
import re

logger = logging.getLogger(__name__)
FINISHED_FILENAME = "finished"
try:
    _str_class = basestring
except NameError:
    _str_class = str


def get_valid_components(module, terminator):
    """ Get possible components, stripping the given suffix from their\
        class names.

    :param module: The module containing the classes to obtain.
    :param terminator: \
        Regular expression string to match the suffix. Anchoring not required.
    :return: mapping from (shortened) name to class
    :rtype: dict(str -> class)
    """
    terminator_re = re.compile(terminator + '$')
    return {terminator_re.sub('', name): router
            for name, router in inspect.getmembers(module, inspect.isclass)}


def is_singleton(value):
    """ Tests whether the value is a singleton. Singleton types are integers,\
        booleans, floats, and strings.
    """
    return isinstance(value, (int, float, _str_class))
