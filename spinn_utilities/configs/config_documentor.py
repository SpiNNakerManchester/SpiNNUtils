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
from typing import Dict, List, Optional, TextIO

from spinn_utilities.config_holder import (
    get_default_cfgs)
from spinn_utilities.configs.camel_case_config_parser import (
    TypedConfigParser)


class _ConfigGroup(object):

    def __init__(self, title: str):
        self._doc: Optional[str] = None
        self.title = title
        self._cfg: Dict[str, str] = dict()

    def add_option(self, option: str, value: str) -> None:
        self._cfg[option] = value

    def has_path(self) -> bool:
        for option in self._cfg:
            if option.startswith("path_"):
                return True
        return False

    def paths(self) -> List[str]:
        paths = []
        for option, value in self._cfg.items():
            if option.startswith("path_"):
                paths.append(value)
        return paths

    def get_see(self) -> Optional[str]:
        for option in self._cfg:
            if option.startswith("@see"):
                return option
        return None

    def print_config(self) -> None:
        if self.title:
            print(f"\t{self.title}")
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

    def get_docs(self):
        keys = list(self._cfg.keys())
        for key in keys:
            if key.startswith("@"):
                if self._doc:
                    raise ValueError(f"{self.title} has multiple @ keys {keys}")
                self._doc = self._cfg[key]
                del self._cfg[key]

    def md_with_path(self, f: TextIO) -> None:
        t_keys = list()
        p_keys = list()
        for key in self._cfg:
            if key.startswith("path_"):
                p_keys.append(key)
            else:
                t_keys.append(key)

        if len(t_keys) == 1:
            f.write("#### Trigger\n")
            for key in t_keys:
                f.write(f"* key: {key} \n* value: {self._cfg[key]}\n")
        elif len(t_keys) > 1:
            f.write("#### Triggers\n")
            for key in t_keys:
                f.write(f"* key: {key} \n  * value: {self._cfg[key]}\n")

        if len(p_keys) == 1:
            f.write("#### Path\n")
            for key in p_keys:
                f.write(f"* key: {key} \n* value: {self._cfg[key]}\n")
        elif len(t_keys) > 1:
            f.write("#### Paths\n")
            for key in p_keys:
                f.write(f"* key: {key} \n  * value: {self._cfg[key]}\n")

    def md(self, f: TextIO) -> None:
        f.write(f'### <a name="{self.title}"></a> {self.title}\n')
        if self._doc:
            f.write(self._doc)
            f.write("\n")
        if self.has_path():
            self.md_with_path(f)
        else:
            for option, value in self._cfg.items():
                f.write(f"* key: {option} \n* value: {value}\n")


class ConfigMap(object):

    def __init__(self):
        self._sections: Dict[str, Dict[str, _ConfigGroup]] = defaultdict(dict)
        self._docs: Dict[str, str] = dict()
        config1 = TypedConfigParser()
        config1.read(get_default_cfgs())
        for section in config1:
            if section == "DEFAULT":
                continue
            for option in config1.options(section):
                value = config1.get(section, option)
                self._add_option(section, option, value)
        self._merge_see(config1)

    def _trim_title(self, title: str) -> str:
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

    def _add_option(self, section: str, option: str, value: str):
        groups = self._sections[section]
        title = self._trim_title(option)
        if title == "":  #  @
            self._docs[section] = value
        else:
            if title in groups:
                group = groups[title]
            else:
                group = _ConfigGroup(title)
                groups[title] = group
            group.add_option(option, value)

    def _merge_see(self, config: TypedConfigParser) -> None:
        for section in self._sections:
            # print(section)
            titles = list(self._sections[section])
            groups = self._sections[section]
            for check_title in titles:
                check_group = groups[check_title]
                see = check_group.get_see()
                if see:
                    value = config.get(section, see)
                    see_title = self._trim_title(value)
                    see_group = groups[see_title]
                    see_group.merge(check_group)
                    del groups[check_title]

        for groups in self._sections.values():
            for group in groups.values():
                group.get_docs()

    def print_section(self, section: str) -> None:
        print(section)
        if section in self._docs:
            print(f"\t{self._docs[section]}")
        titles = list(self._sections[section])
        titles.sort()
        groups = self._sections[section]
        for title in titles:
            group = groups[title]
            group.print_config()

    def print_configs(self) -> None:
        for section in self._sections:
            self.print_section(section)

    def debug(self) -> None:
        # print("*** Debug  ***")
        for section in self._sections:
            # print(section)
            for group in self._sections[section].values():
                group.debug()

    def _md_header(self, f: TextIO) -> None:
        f.write("---\n")
        f.write("title: SpiNNaker cfg settings\n")
        f.write("layout: default\n")
        f.write("published: true\n")
        f.write("---\n")

        f.write("This guide covers the cfg settings and the reports created\n")

    def _md_section(self, section: str, f: TextIO) -> None:
        f.write(f'# <a name="{section}"></a> {section}\n')
        if section in self._docs:
            f.write(f"{self._docs[section]}\n")
        titles = list(self._sections[section])
        titles.sort()
        for title in titles:
            f.write(f"* [{title}](#{title})\n")
        for title in titles:
            group = self._sections[section][title]
            group.md(f)

    def md_configs(self, filepath: str) -> None:
        with open(filepath, mode="w") as f:
            self._md_header(f)
            f.write(f"* CFG Sections\n")
            for section in self._sections:
                f.write(f"  * [{section}](#{section})\n")
            f.write("* [Report Files](#report_files})\n")

            for section in self._sections:
                self._md_section(section, f)

            f.write(f'# <a name="report_files"></a> Report Files\n')
            p_map = dict()
            for section in self._sections:
                for group in self._sections[section].values():
                    for path in group.paths():
                        p_map[path] = group.title
            p_map = dict(sorted(p_map.items()))
            for path, title in p_map.items():
                f.write(f"  * [{path}](#{title})\n")