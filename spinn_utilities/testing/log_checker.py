from __future__ import print_function

_WRITE_LOGS_TO_STDOUT = True


def _assert_logs_contains(level, log_records, submessage):
    for record in log_records:
        if record.levelname == level and submessage in record.getMessage():
            return
    if _WRITE_LOGS_TO_STDOUT:
        for record in log_records:
            print(record)
    raise AssertionError(
        "\"{}\" not found in any {} logs".format(submessage, level))


def _assert_logs_not_contains(level, log_records, submessage):
    for record in log_records:
        if _WRITE_LOGS_TO_STDOUT:
            print(record)
        if record.levelname == level and submessage in record.getMessage():
            raise AssertionError(
                "\"{}\" found in any {} logs".format(submessage, level))


def assert_logs_contains_once(level, log_records, message):
    """ Checks if the log records contain exactly one record at the given\
        level with the given sub-message.

    .. note::
        While this code does not depend on testfixtures,\
        you will need testfixtures to generate the input data

    :param level: The log level. Probably "INFO", "WARNING" or "ERROR".
    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of a log record
    :rtype: None
    :raises AssertionError: If the submessage is not present in the log
    """
    found = False
    for record in log_records:
        if record.levelname == level and message == record.getMessage():
            if found:
                if _WRITE_LOGS_TO_STDOUT:
                    for a_record in log_records:
                        print(a_record)
                raise AssertionError(
                    "\"{}\" found twice in  {} logs".format(message, level))
            found = True
    if not found:
        if _WRITE_LOGS_TO_STDOUT:
            for record in log_records:
                print(record)
        raise AssertionError(
            "\"{}\" not found in any {} logs".format(message, level))


def assert_logs_error_contains(log_records, submessage):
    """ Checks it the log records contain an ERROR log with this sub-message

    .. note::
        While this code does not depend on testfixtures,\
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an ERROR log
    :rtype: None
    :raises AssertionError: If the submessage is not present in the log
    """
    _assert_logs_contains('ERROR', log_records, submessage)


def assert_logs_info_contains(log_records, sub_message):
    """ Checks it the log records contain an INFO log with this sub-message

    .. note::
        While this code does not depend on testfixtures,\
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param sub_message: String which should be part of an INFO log
    :rtype: None
    :raises AssertionError: If the submessage is not present in the log
    """
    _assert_logs_contains('INFO', log_records, sub_message)


def assert_logs_error_not_contains(log_records, submessage):
    """ Checks it the log records do not contain an ERROR log with this\
        sub-message

    .. note::
        While this code does not depend on testfixtures,\
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an ERROR log
    :rtype: None
    :raises AssertionError: If the submessage is present in the log
    """
    _assert_logs_not_contains('ERROR', log_records, submessage)


def assert_logs_info_not_contains(log_records, submessage):
    """ Checks it the log records do not contain an INFO log with this\
        sub-message

    .. note::
        While this code does not depend on testfixtures,\
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an INFO log
    :rtype: None
    :raises AssertionError: If the submessage is present in the log
    """
    _assert_logs_not_contains('INFO', log_records, submessage)
