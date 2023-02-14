# Copyright (c) 2018 The University of Manchester
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

import inspect
from spinn_utilities.overrides import overrides
_introspector = inspect.getfullargspec


class see(overrides):
    """ A decorator for indicating that the documentation of the method\
        is provided by another method with exactly the same arguments.

    .. note::
        This has the same effect as overrides in reality, but is provided
        to show that the method doesn't actually override
    """

    def __init__(
            self, documentation_method, extend_doc=True,
            additional_arguments=None, extend_defaults=False):
        super().__init__(
            documentation_method, extend_doc=extend_doc,
            additional_arguments=additional_arguments,
            extend_defaults=extend_defaults)

        # Same as overrides, except name doesn't have to match
        self._relax_name_check = True

        # Give the errors a better name
        self._override_name = "documentation method"
