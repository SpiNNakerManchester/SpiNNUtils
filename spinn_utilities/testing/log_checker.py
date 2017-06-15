def assert_logs_contains(level_name, log_records, sub_message):
    for record in log_records:
        if record.levelname == level_name:
            if sub_message in record.msg:
                return
    for record in log_records:
        print record
    msg = "\"{}\" not found in any {} logs".format(sub_message, level_name)
    raise AssertionError(msg)


def assert_logs_contains_once(level_name, log_records, message):
    found = False
    for record in log_records:
        if record.levelname == level_name:
            if message == record.msg:
                if found:
                    for a_record in log_records:
                        print a_record
                    msg = "\"{}\" found twice in  {} logs" \
                          "".format(message, level_name)
                    raise AssertionError(msg)
                found = True
    if not found:
        for record in log_records:
            print record
        msg = "\"{}\" not found in any {} logs".format(message, level_name)
        raise AssertionError(msg)


def assert_logs_error_contains(log_records, sub_message):
    """
    Checks it the log records contain an ERROR log with this sub message

    Note: While this code does not depend on testfixtures
        you will need testfixtures to generate the input data
    :param log_records: list of log records returned bu testfixtures.LogCapture
    :param sub_message: String which should be part of an ERROR log
    :rasies: AssertionError
    """
    assert_logs_contains('ERROR', log_records, sub_message)


def assert_logs_info_contains(log_records, sub_message):
    """
    Checks it the log records contain an INFO log with this sub message

    Note: While this code does not depend on testfixtures
        you will need testfixtures to generate the input data
    :param log_records: list of log records returned bu testfixtures.LogCapture
    :param sub_message: String which should be part of an INFO log
    :rasies: AssertionError
    """
    assert_logs_contains('INFO', log_records, sub_message)


def assert_logs_not_contains(level_name, log_records, sub_message):
    for record in log_records:
        print record
        if record.levelname == level_name:
            if sub_message in record.msg:
                msg = "\"{}\" found in any {} logs".format(sub_message,
                                                           level_name)
                raise AssertionError(msg)


def assert_logs_error_not_contains(log_records, sub_message):
    """
    Checks it the log records do not contain an ERROR log with this sub message

    Note: While this code does not depend on testfixtures
        you will need testfixtures to generate the input data
    :param log_records: list of log records returned bu testfixtures.LogCapture
    :param sub_message: String which should be part of an ERROR log
    :rasies: AssertionError
    """
    assert_logs_not_contains('ERROR', log_records, sub_message)


def assert_logs_info_not_contains(log_records, sub_message):
    """
    Checks it the log records do not contain an INFO log with this sub message

    Note: While this code does not depend on testfixtures
        you will need testfixtures to generate the input data
    :param log_records: list of log records returned bu testfixtures.LogCapture
    :param sub_message: String which should be part of an INFO log
    :rasies: AssertionError
    """
    assert_logs_not_contains('INFO', log_records, sub_message)
