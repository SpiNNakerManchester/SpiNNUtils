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
import re
from typing import Dict, List, Optional, TextIO

from spinn_utilities.config_holder import (
    get_default_cfgs)
from spinn_utilities.configs.camel_case_config_parser import (
    TypedConfigParser)


def _make_link(title: str) -> str:
    if title.startswith("@"):
        raise ValueError(f"{title=} has a @")
    elif title.startswith("draw_"):
        title = title[5:]
    elif title.startswith("keep_"):
        title = title[5:]
    elif title.startswith("path_"):
        title = title[5:]
    elif title.startswith("tpath_"):
        title = title[6:]
    elif title.startswith("run_"):
        title = title[4:]
    elif title.startswith("write_"):
        title = title[6:]
    return title


def _md_write_doc(f: TextIO, raw: str) -> None:
    while "\\t*" in raw:
        raw = raw.replace("\\t*", "   *")
    while "\\t" in raw:
        raw = raw.replace("\\t", "&nbsp;&nbsp;")
    if raw[-2:] == "\\n":
        raw = raw[:-2] + "\n"
    raw = raw.replace("\\n\\n", "\n\n")
    raw = raw.replace("\\n\n", "  \n")

    link_match = re.search(r"\[(\w|\s)*\]\((\s|\w)*\)", raw)
    if link_match:
        start = raw.index("(", link_match.start()) + 1
        end = link_match.end() - 1
        link = raw[start:end]
        title = _make_link(link)
        if link != title:
            raw = raw[:start] + "title" + raw[end:]

    f.write(raw)
    f.write("\n")


class _ConfigGroup(object):

    def __init__(self, title: str):
        self._docs: Optional[str] = None
        self.title = title
        self._cfg: Dict[str, str] = dict()

    def add_option(self, option: str, value: str) -> None:
        self._cfg[option] = value

    def has_path(self) -> bool:
        for option in self._cfg:
            if option.startswith("path_"):
                return True
            if option.startswith("tpath_"):
                return True
        return False

    def paths(self) -> List[str]:
        paths = []
        for option, value in self._cfg.items():
            if option.startswith("path_"):
                paths.append(value)
            if option.startswith("tpath_"):
                paths.append(value)
        return paths

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
            if option.startswith("@group"):
                continue
            self.add_option(option, value)

    def add_doc(self, docs):
        if self._docs:
            raise ValueError(f"{self.title} already has a docs")
        self._docs = docs

    def missing_docs(self) -> bool:
        return self._docs is None

    def md_with_path(self, f: TextIO) -> None:
        t_keys = list()
        p_keys = list()
        for key in self._cfg:
            if key.startswith("path_") or key.startswith("tpath_"):
                p_keys.append(key)
            else:
                t_keys.append(key)

        f.write("#### Trigger\n")
        for key in t_keys:
            f.write(f"* key: {key} \n  * value: {self._cfg[key]}\n")

        f.write("#### Path\n")
        for key in p_keys:
            f.write(f"* key: {key} \n  * value: {self._cfg[key]}\n")

    def md(self, f: TextIO) -> None:
        f.write(f'### <a name="{_make_link(self.title)}"></a> {self.title}\n')

        if self._docs:
            _md_write_doc(f, self._docs)
            f.write("\n")
        if self.has_path():
            self.md_with_path(f)
        else:
            for option, value in self._cfg.items():
                f.write(f"* key: {option} \n  * value: {value}\n")


class ConfigDocumentor(object):

    def __init__(self):
        self._sections: Dict[str, Dict[str, _ConfigGroup]] = defaultdict(dict)
        self._docs: Dict[str, str] = dict()
        self._links: Dict[str, str] = dict()
        config1 = TypedConfigParser()
        config1.read(get_default_cfgs())
        for section in config1:
            if section == "DEFAULT":
                continue
            for option in config1.options(section):
                value = config1.get(section, option)
                self._add_option(section, option, value)
        self._process_special(config1)
        self._check_all_doced()

    def _add_option(self, section: str, option: str, value: str):
        groups = self._sections[section]
        if option.startswith("@"):
            return
        if option in groups:
            raise ValueError(f"{option=} used twice")
        else:
            group = _ConfigGroup(option)
            groups[option] = group
        group.add_option(option, value)
        link = _make_link(option)
        if link != option:
            self._links[link] = option

    def _get_linked(self, option: str) -> str:
        link = _make_link(option)
        if link == option:
            return option
        return self._links[link]

    def _process_special(self, config: TypedConfigParser) -> None:
        remove_titles = set()
        for section in config.sections():
            groups = self._sections[section]
            for title in config.options(section):
                if title.startswith("@"):
                    if title.startswith("@group"):
                        if title.startswith("@group_"):
                            group_title = title[7:]
                        else:
                            group_title = title[6:]
                        other_title = config.get(section, title)
                        groups[other_title].merge(groups[group_title])
                        remove_titles.add((section, group_title))
                    else:
                        if title == "@":
                            self._docs[section] = config.get(section, title)
                        else:
                            other_title = title[1:]
                            groups[other_title].add_doc(config.get(section, title))
                if title.startswith("path_") or title.startswith("tpath_"):
                    as_link = _make_link(title)
                    if as_link in self._links:
                        other_title = self._links[as_link]
                        groups[other_title].merge(groups[title])
                        remove_titles.add((section, title))

        for (section, group_title) in remove_titles:
            del self._sections[section][group_title]

    def _check_all_doced(self) -> None:
        for section in self._sections:
            if section not in self._docs:
                raise ValueError(f"{section=} has no doc")
            for title, group in self._sections[section].items():
                if group.missing_docs():
                    raise ValueError(f"{title=} has missing docs")

    def print_section(self, section: str) -> None:
        print(section)
        #if section in self._docs:
        #    print(f"\t{self._docs[section]}")
        titles = list(self._sections[section])
        titles.sort()
        #groups = self._sections[section]
        for title in titles:
            print("\t",title)
        #    group = groups[title]
        #    group.print_config()

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
        f.write("<!-- \n")
        f.write("This file is autogenerated do not edit!\n")
        f.write("Created by spinn_utilities/configs/config_documentor.py\n")
        f.write("Based on the default cfg files\n")
        f.write("See spinn_utilities/configs/notes.md\n")
        f.write("-->\n")

        f.write("This guide covers the cfg settings and the reports created\n")

    def _md_section(self, section: str, f: TextIO) -> None:
        f.write(f'# <a name="{section}"></a> {section}\n')
        if section in self._docs:
            _md_write_doc(f,self._docs[section])
        titles = list(self._sections[section])
        titles.sort()
        if section != "Mode":
            for title in titles:
                f.write(f"* [{title}](#{title})\n")
        for title in titles:
            group = self._sections[section][title]
            group.md(f)

    def md_reports(self, f: TextIO) -> None:
        f.write(f'# <a name="report_files"></a> Report Files\n')
        p_map = dict()
        for section in self._sections:
            for group in self._sections[section].values():
                for path in group.paths():
                    p_map[path] = group.title
        p_map = dict(sorted(p_map.items()))
        for path, title in p_map.items():
            f.write(f"  * [{path}](#{title})\n")

    def md_notes(self, f: TextIO) -> None:
        with open("/home/brenninc/spinnaker/SpiNNUtils/spinn_utilities/configs/notes.md") as notesfile:
            lines = notesfile.readlines()
            f.writelines(lines)

    def md_configs(self, filepath: str) -> None:
        with open(filepath, mode="w") as f:
            self._md_header(f)
            f.write(f"* CFG Sections\n")
            for section in self._sections:
                f.write(f"  * [{section}](#{section})\n")
            f.write("* [Report Files](#report_files)\n")
            f.write("* [Notes for Developers[(#notes)\n")

            for section in self._sections:
                self._md_section(section, f)
            self.md_reports(f)
            self.md_notes(f)
