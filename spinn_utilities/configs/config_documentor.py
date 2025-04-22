# Copyright (c) 2025 The University of Manchester
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

from collections import defaultdict
from typing import Dict, Optional

from spinn_utilities.config_holder import (
    get_default_cfgs)
from spinn_utilities.configs.camel_case_config_parser import (
    TypedConfigParser)


class ConfigGroup(object):

    def __init__(self, title: str):
        self._title = title
        self._cfg: Dict[str, str] = dict()

    def add_option(self, option: str, value: str) -> None:
        self._cfg[option] = value

    def has_path(self) -> bool:
        for option in self._cfg:
            if option.startswith("path_"):
                return True
        return False

    def get_see(self) -> Optional[str]:
        for option in self._cfg:
            if option.startswith("@see"):
                return option
        return None

    def print_config(self) -> None:
        print(f"\t{self._title}")
        for option, value in self._cfg.items():
            print(f"\t\t{option}: {value}")

    def debug(self):
        if len(self._cfg) > 1:
            return
        keys = list(self._cfg.keys())
        key = keys[0]
        if key.startswith("path"):
            print("\t", key, self._cfg[key])

    def merge(self, other: "ConfigGroup") -> None:
        for option, value in other._cfg.items():
            if option.startswith("@see"):
                continue
            self.add_option(option, value)

class ConfigMap(object):

    def __init__(self):
        self._sections: Dict[str, Dict[str, ConfigGroup]] = defaultdict(dict)

    def trim_title(self, title: str) -> str:
        if title.startswith("@"):
            if title.startswith("@see"):
                if title.startswith("@see_"):
                    title = title[5:]
                else:
                    title = title[4:]
            elif title.startswith("@_"):
                title = title[2:]
            else:
                title = title[1:]

        if title.startswith("draw_"):
            title = title[5:]
        elif title.startswith("keep_"):
            title = title[5:]
        elif title.startswith("path_"):
            title = title[5:]
        elif title.startswith("run_"):
            title = title[4:]
        elif title.startswith("write_"):
            title = title[6:]

        return title

    def add_option(self, section: str, option: str, value: str):
        groups = self._sections[section]
        title = self.trim_title(option)
        if title in groups:
            group = groups[title]
        else:
            group = ConfigGroup(title)
            groups[title] = group
        group.add_option(option, value)

    def merge_see(self, config: TypedConfigParser) -> None:
        for section in self._sections:
            # print(section)
            titles = list(self._sections[section])
            groups = self._sections[section]
            for check_title in titles:
                check_group = groups[check_title]
                see = check_group.get_see()
                if see:
                    value = config.get(section, see)
                    see_title = self.trim_title(value)
                    see_group = groups[see_title]
                    see_group.merge(check_group)
                    del groups[check_title]

    def print_config(self) -> None:
        for section in self._sections:
            print(section)
            titles = list(self._sections[section])
            titles.sort()
            groups = self._sections[section]
            for title in titles:
                group = groups[title]
                group.print_config()

    def debug(self) -> None:
        # print("*** Debug  ***")
        for section in self._sections:
            # print(section)
            for group in self._sections[section].values():
                group.debug()

def print_configs() -> None:
    """
    :return:
    """
    config1 = TypedConfigParser()
    config_map = ConfigMap()
    print(config_map)
    config1.read(get_default_cfgs())
    for section in config1:
        if section == "DEFAULT":
            continue
        for option in config1.options(section):
            value = config1.get(section, option)
            config_map.add_option(section, option, value)
    config_map.merge_see(config1)
    config_map.print_config()
    config_map.debug()
