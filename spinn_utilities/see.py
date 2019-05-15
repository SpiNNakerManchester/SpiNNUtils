# Copyright (c) 2018 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect
from spinn_utilities.overrides import overrides

try:
    # pylint: disable=no-member
    _introspector = inspect.getfullargspec  # @UndefinedVariable
except AttributeError:
    _introspector = inspect.getargspec


class see(overrides):
    """ A decorator for indicating that the documentation of the method\
        is provided by another method with exactly the same arguments.  Note\
        that this has the same effect as overrides in reality, but is provided\
        to show that the method doesn't actually override
    """

    def __init__(
        self, documentation_method, extend_doc=True,
            additional_arguments=None, extend_defaults=False):
        super(see, self).__init__(
            documentation_method, extend_doc=extend_doc,
            additional_arguments=additional_arguments,
            extend_defaults=extend_defaults)

        # Same as overrides, except name doesn't have to match
        self._relax_name_check = True

        # Give the errors a better name
        self._override_name = "documentation method"
