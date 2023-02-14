# Copyright (c) 2017-2019 The University of Manchester
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

_already_issued = set()


def warn_once(logger, msg):
    if msg in _already_issued:
        return
    _already_issued.add(msg)
    logger.warning(msg)


def error_once(logger, msg):
    if msg in _already_issued:
        return
    _already_issued.add(msg)
    logger.error(msg)


def reset():
    global _already_issued     # pylint: disable=global-statement
    _already_issued = set()
