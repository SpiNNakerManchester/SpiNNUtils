import logging
import inspect
import re

logger = logging.getLogger(__name__)
FINISHED_FILENAME = "finished"


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
