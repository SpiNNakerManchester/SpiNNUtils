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

_already_issued = set()


def warn_once(logger, msg):
    """
    Write a warning message to the given logger where that message should only
    be written to the logger once.

    :param logger: The logger to write to.
    :param msg: The message to write.

        .. note::
            This must be a substitution-free message.
    """
    if msg in _already_issued:
        return
    _already_issued.add(msg)
    logger.warning(msg)


def error_once(logger, msg):
    """
    Write an error message to the given logger where that message should only
    be written to the logger once.

    :param logger: The logger to write to.
    :param msg: The message to write.

        .. note::
            This must be a substitution-free message.
    """
    if msg in _already_issued:
        return
    _already_issued.add(msg)
    logger.error(msg)


def reset():
    """
    Clear the store of what messages have already been seen.

    .. note::
        Only normally needed by test code.
    """
    global _already_issued     # pylint: disable=global-statement
    _already_issued = set()
