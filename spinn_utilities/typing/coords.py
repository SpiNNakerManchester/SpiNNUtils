# Copyright (c) 2023 The University of Manchester
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

"""
Types for coordinates.
"""

from typing import Final, Tuple
from typing_extensions import TypeAlias

#: The type of X,Y pairs.
XY: Final['TypeAlias'] = Tuple[int, int]

#: The type of X,Y,P triples.
XYP: Final['TypeAlias'] = Tuple[int, int, int]
