# Copyright (c) 2018 The University of Manchester
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

from .citation_updater_and_doi_generator import CitationUpdaterAndDoiGenerator
from .citation_aggregator import (
    CitationAggregator, generate_aggregate)

__all__ = [
    "CitationAggregator", "CitationUpdaterAndDoiGenerator",
    "generate_aggregate"]
