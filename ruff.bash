#!/bin/bash

# Copyright (c) 2024 The University of Manchester
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

# This bash assumes that other repositories are installed in parallel
# Runs based on the lowest python version supported.
# Can be run by any python that or higher

if [ "$#" -eq  "0" ]
  then
    echo "Using previous setup. Provide an argument to run setup"
    source ../SupportScripts/venv/ruff_runner/bin/activate
else
  python3 -m venv ../SupportScripts/venv/ruff_runner
  source ../SupportScripts/venv/ruff_runner/bin/activate
  pip3 install --upgrade ../SpiNNUtils[test]
  python3 -m pip install --upgrade ruff
fi

ruff check spinn_utilities unittests --target-version py310 --config ../SupportScripts/actions/ruff/ruff.toml
ruff check spinn_utilities unittests --target-version py310 --config ../SupportScripts/actions/ruff/ruff_up.toml
