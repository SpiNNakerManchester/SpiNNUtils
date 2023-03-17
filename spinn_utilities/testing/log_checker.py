# Copyright (c) 2017 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

_WRITE_LOGS_TO_STDOUT = True


def _assert_logs_contains(level, log_records, submessage):
    for record in log_records:
        if record.levelname == level and submessage in record.getMessage():
            return
    if _WRITE_LOGS_TO_STDOUT:  # pragma: no cover
        for record in log_records:
            print(record)
    raise AssertionError(f"\"{submessage}\" not found in any {level} logs")


def _assert_logs_not_contains(level, log_records, submessage):
    for record in log_records:
        if _WRITE_LOGS_TO_STDOUT:  # pragma: no cover
            print(record)
        if record.levelname == level and submessage in record.getMessage():
            raise AssertionError(
                f"\"{submessage}\" found in any {level} logs")


def assert_logs_contains_once(level, log_records, message):
    """
    Checks if the log records contain exactly one record at the given
    level with the given sub-message.

    .. note::
        While this code does not depend on testfixtures,
        you will need testfixtures to generate the input data

    :param level: The log level. Probably "INFO", "WARNING" or "ERROR".
    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of a log record
    :raises AssertionError: If the submessage is not present in the log
    """
    found = False
    for record in log_records:
        if record.levelname == level and message == record.getMessage():
            if found:
                if _WRITE_LOGS_TO_STDOUT:  # pragma: no cover
                    for a_record in log_records:
                        print(a_record)
                raise AssertionError(
                    f"\"{message}\" found twice in  {level} logs")
            found = True
    if not found:
        if _WRITE_LOGS_TO_STDOUT:  # pragma: no cover
            for record in log_records:
                print(record)
        raise AssertionError(f"\"{message}\" not found in any {level} logs")


def assert_logs_error_contains(log_records, submessage):
    """
    Checks it the log records contain an ERROR log with this sub-message

    .. note::
        While this code does not depend on testfixtures,
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an ERROR log
    :raises AssertionError: If the submessage is not present in the log
    """
    _assert_logs_contains('ERROR', log_records, submessage)


def assert_logs_warning_contains(log_records, submessage):
    """
    Checks it the log records contain an WARNING log with this sub-message

    .. note::
        While this code does not depend on testfixtures,
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an WARNING log
    :raises AssertionError: If the submessage is not present in the log
    """
    _assert_logs_contains('WARNING', log_records, submessage)


def assert_logs_info_contains(log_records, sub_message):
    """
    Checks it the log records contain an INFO log with this sub-message

    .. note::
        While this code does not depend on testfixtures,
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param sub_message: String which should be part of an INFO log
    :raises AssertionError: If the submessage is not present in the log
    """
    _assert_logs_contains('INFO', log_records, sub_message)


def assert_logs_error_not_contains(log_records, submessage):
    """
    Checks it the log records do not contain an ERROR log with this
    sub-message.

    .. note::
        While this code does not depend on testfixtures,
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an ERROR log
    :raises AssertionError: If the submessage is present in the log
    """
    _assert_logs_not_contains('ERROR', log_records, submessage)


def assert_logs_info_not_contains(log_records, submessage):
    """
    Checks it the log records do not contain an INFO log with this
    sub-message.

    .. note::
        While this code does not depend on testfixtures,
        you will need testfixtures to generate the input data

    :param log_records: list of log records returned by testfixtures.LogCapture
    :param submessage: String which should be part of an INFO log
    :raises AssertionError: If the submessage is present in the log
    """
    _assert_logs_not_contains('INFO', log_records, submessage)
