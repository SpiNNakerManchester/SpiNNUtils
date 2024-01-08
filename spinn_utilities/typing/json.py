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
Types for JSON.
"""

from typing import Dict, List, Union
from typing_extensions import TypeAlias

#: The type of JSON values.
JsonValue: TypeAlias = Union[int, float, str, None, "JsonObject", "JsonArray"]
# NB: The above type is mutually recursive with the definitions below.

#: The type of JSON objects.
JsonObject: TypeAlias = Dict[str, JsonValue]

#: The type of JSON arrays.
JsonArray: TypeAlias = List[JsonValue]

#: The type of JSON arrays of objects. Used for casting.
JsonObjectArray: TypeAlias = List[JsonObject]
