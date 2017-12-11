import logging
import inspect
import re

logger = logging.getLogger(__name__)
FINISHED_FILENAME = "finished"


def get_valid_components(module, terminator):
    """ Get possible components

    :param module:
    :param terminator:
    :rtype: dict
    """
    terminator = re.compile(terminator + '$')
    return dict(map(lambda (name, router): (terminator.sub('', name), router),
                inspect.getmembers(module, inspect.isclass)))
