# Copyright (c) 2022 The University of Manchester
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

from datetime import datetime
from typing import List, Optional, Tuple
from .abstract_base import abstractmethod


class LogStore(object):
    """
    API supported by classes that can store logs for later retrieval.
    """

    @abstractmethod
    def store_log(self, level: int, message: str,
                  timestamp: Optional[datetime] = None):
        """
        Writes the log message for later retrieval.

        :param int level: The logging level.
        :param str message: The logged message.
        :param timestamp: The time-stamp of the message.
        :type timestamp: ~datetime.datetime or None
        """
        raise NotImplementedError

    @abstractmethod
    def retreive_log_messages(
            self, min_level: int = 0) -> List[Tuple[int, str]]:
        """
        Retrieves all log messages at or above the `min_level`.

        :param int min_level:
            Constraint on the minimum logging level to retrieve.
        :return:
            A list of messages that satisfy the constraint.
        :rtype: list(tuple(int, str))
        """
        raise NotImplementedError

    @abstractmethod
    def get_location(self) -> str:
        """
        Retrieves the location of the log store.

        :rtype: str
        """
        raise NotImplementedError
