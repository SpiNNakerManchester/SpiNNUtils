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

from typing import Any
from spinn_utilities.abstract_base import (
    AbstractBase, abstractmethod)


class AbstractHasConstraints(object, metaclass=AbstractBase):
    """ Represents an object with constraints
    """

    __slots__ = ()

    @abstractmethod
    def add_constraint(self, constraint: Any) -> None:
        """ Add a new constraint to the collection of constraints

        :param constraint: constraint to add
        :raise pacman.exceptions.PacmanInvalidParameterException:
            If the constraint is not valid
        """

    @property
    @abstractmethod
    def constraints(self) -> Any:
        """ An iterable of constraints

        :return: iterable of constraints
        """
