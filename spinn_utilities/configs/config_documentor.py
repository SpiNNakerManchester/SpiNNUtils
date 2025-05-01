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
import os
import re
import sys
from typing import Dict, List, Optional, Set, TextIO

from spinn_utilities.config_holder import (
    get_default_cfgs)
from spinn_utilities.configs.camel_case_config_parser import (
    TypedConfigParser)


def _make_name(option: str) -> str:
    """
    Converts an option to a possibly shortened name string

    This will no include a leading #

    This is used for cfg options that may be automatically group.
    So that either can be used in a link.

    :return: Possibly shortened option name
    """
    # take the link marker out
    if option.startswith("#"):
        option = option[1:]
    if option.startswith("@"):
        raise ValueError(f"{option=} has a @")
    elif option.startswith("draw_"):
        option = option[5:]
    elif option.startswith("keep_"):
        option = option[5:]
    elif option.startswith("path_"):
        option = option[5:]
    elif option.startswith("tpath_"):
        option = option[6:]
    elif option.startswith("run_"):
        option = option[4:]
    elif option.startswith("write_"):
        option = option[6:]
    ' put the link marker back'
    return option


def _make_link(option: str) -> str:
    """
    Converts an option to a possibly shortened link string

    This will include a leading #

    see _ make_name

    :return: Possibly shortened option link
    """
    return "#" + _make_name(option)


def _md_write_doc(f: TextIO, raw: str) -> None:
    """
    Writes the raw (document text) with some minor corrections.

    See
    https://github.com/SpiNNakerManchester/SpiNNUtils/spinn_utilities/configs/notes.md
    for the changes that will be made.
    """
    while "\\t*" in raw:
        raw = raw.replace("\\t*", "   *")
    while "\\t" in raw:
        raw = raw.replace("\\t", "&nbsp;&nbsp;")
    if raw[-2:] == "\\n":
        raw = raw[:-2] + "\n"
    raw = raw.replace("\\n\\n", "\n\n")
    raw = raw.replace("\\n\n", "  \n")

    pointers = []
    pointer_matchs = re.finditer(r"\[(\w|\s|\(|\))*\]\((\s|\w)*\)", raw)
    for pointer_match in pointer_matchs:
        pointers.append(raw[pointer_match.start():pointer_match.end()])
    for pointer in pointers:
        start = pointer.index("]", ) + 2
        raw_link = pointer[start:-1]
        link = _make_link(raw_link)
        if link != raw_link:
            fixed = pointer[:start] + link + ")"
            raw = raw.replace(pointer, fixed)

    f.write(raw)
    f.write("\n\n")


class _ConfigGroup(object):
    """
    Hold the values for one cfg key plus its docs and any grouped ones.
    """

    def __init__(self, option: str, value: str):
        self._docs: Optional[str] = None
        self.title = option
        self._cfg: Dict[str, str] = dict()
        self._cfg[option] = value

    def paths(self) -> List[str]:
        """
        Gets a list of the cfg settings in the group that point to a path.

        Path cfg options are those which start with path_ or tpath_
        """
        paths = []
        for option, value in self._cfg.items():
            if option.startswith("path_"):
                paths.append(value)
            if option.startswith("tpath_"):
                paths.append(value)
        return paths

    def print_config(self) -> None:
        """
        Prints the keys and Values in this cfg group.

        This is mainly for debugging so can change without notice.
        """
        if len(self._cfg) == 1:
            for option, value in self._cfg.items():
                print(f"\t{option}: {value}")
        else:
            print(f"\t{self.title}")
            for option, value in self._cfg.items():
                print(f"\t\t{option}: {value}")

    def merge(self, other: "_ConfigGroup") -> None:
        """
        Merges the option form the other into this group.
        """
        for option, value in other._cfg.items():
            if option in self._cfg:
                raise ValueError(f"{option} already exists in group")
            self._cfg[option] = value

    def add_doc(self, docs):
        """
        Adds the docs (marked with @) into this group
        """
        if self._docs:
            raise ValueError(f"{self.title} already has a docs")
        self._docs = docs

    def missing_docs(self) -> bool:
        """
        Returns True if this group does not have any docs
        """
        return self._docs is None

    def _md_value(self, value: str) -> str:
        """
        Writes the value adding a pointer to mode if applicable.
        """
        if value.lower() in ["debug", "info"]:
            if self.title == "default":
                # special case [Logging]default
                return value
            else:
                return f"[{value}](#mode)"
        else:
            return value

    def md(self, f: TextIO) -> None:
        """
        Writes a markdown version of this group to the file.
        """
        f.write(f'### <a name="{_make_name(self.title)}"></a> {self.title}\n')
        if len(self._cfg) == 1:
            value = next(iter(self._cfg.values()))
            f.write(f"Default: __{self._md_value(value)}__\n")
        else:
            for option, value in self._cfg.items():
                f.write(f"* key: {option} \n")
                f.write(f"  * value: {self._md_value(value)}\n")
        f.write("\n")
        _md_write_doc(f, self._docs)


class ConfigDocumentor(object):
    """
    This class will document all the default configs.

    This can be called at any level but will only work with the
    default cfg files set. (Typically up to that level)
    """

    def __init__(self):
        self._sections: Dict[str, Dict[str, _ConfigGroup]] = defaultdict(dict)
        self._docs: Dict[str, str] = dict()
        self._names: Dict[str, str] = dict()
        config1 = TypedConfigParser()
        config1.read(get_default_cfgs())
        for section in config1:
            if section == "DEFAULT":
                continue
            for option in config1.options(section):
                value = config1.get(section, option)
                self._add_option(section, option, value)
        self._process_special(config1)
        self._merge_paths()
        self.check()

    def _add_option(self, section: str, option: str, value: str):
        """
        Adds a cfg option.

        Ignores the special ones (@) at this time.
        """
        groups = self._sections[section]
        if option.startswith("@"):
            return
        if option in groups:
            raise ValueError(f"{option=} used twice")
        else:
            group = _ConfigGroup(option, value)
            groups[option] = group
        name = _make_name(option)
        if name != option:
            if option.startswith("path_") or option.startswith("tpath_"):
                return
            if name in self._names:
                raise ValueError(f"Both {option} and {self._names[name]}"
                                 f" have the same link.")
            self._names[name] = option

    def _process_special(self, config: TypedConfigParser) -> None:
        """
        This pass processes all the special (start with @) cfg keys.

        See
        https://github.com/SpiNNakerManchester/SpiNNUtils/spinn_utilities/configs/notes.md
        """
        for section in config.sections():
            groups = self._sections[section]
            for option in config.options(section):
                if option.startswith("@"):
                    if option.startswith("@group"):
                        if option.startswith("@group_"):
                            group_option = option[7:]
                        else:
                            group_option = option[6:]
                        other_option = config.get(section, option)
                        groups[other_option].merge(groups[group_option])
                        del self._sections[section][group_option]
                    else:
                        if option == "@":
                            self._docs[section] = config.get(section, option)
                        else:
                            other_option = option[1:]
                            groups[other_option].add_doc(config.get(
                                section, option))

    def _merge_paths(self) -> None:
        """
        Merges groups with path and similar option names.

        See
        https://github.com/SpiNNakerManchester/SpiNNUtils/spinn_utilities/configs/notes.md
        """
        for groups in self._sections.values():
            remove_options = set()
            for option in groups:
                if option.startswith("path_") or option.startswith("tpath_"):
                    as_link = _make_name(option)
                    if as_link in self._names:
                        other_option = self._names[as_link]
                        groups[other_option].merge(groups[option])
                        remove_options.add(option)
            for option in remove_options:
                del groups[option]

    def check(self) -> None:
        """
        Runs the checks that the cfg will work as markdown.

        Expects all sections and not grouped (including by path name) options
        to have docs (@)

        Expects all  sections and not grouped options to generate unique links.
        """
        names: Set[str] = set()
        for section in self._sections:
            if section in names:
                raise ValueError(f"{section=} has a duplicate name")
            else:
                names.add(section)
            if section not in self._docs:
                raise ValueError(f"{section=} has no doc")
            for title, group in self._sections[section].items():
                name = _make_name(title)
                if name in names:
                    raise ValueError(
                        f"{name=} from {title=} has a duplicate link")
                else:
                    names.add(name)
                if group.missing_docs():
                    raise ValueError(f"{title=} has missing docs")

    def print_section(self, section: str) -> None:
        """
        Prints this section.

        This is mainly for debugging so can change without notice.
        """
        print(section)
        print(f"\t{self._docs[section]}")
        titles = list(self._sections[section])
        titles.sort()
        groups = self._sections[section]
        for title in titles:
            group = groups[title]
            group.print_config()

    def print_configs(self) -> None:
        """
        Prints all configs.

        This is mainly for debugging so can change without notice.
        """

        for section in self._sections:
            self.print_section(section)

    def _md_header(self, f: TextIO) -> None:
        """
        Write the mark down header section.
        """
        f.write("---\n")
        f.write("option: SpiNNaker cfg settings\n")
        f.write("layout: default\n")
        f.write("published: true\n")
        f.write("---\n")
        f.write("CFG Settings and Reports\n")
        f.write("========================\n")
        f.write("<!-- \n")
        f.write("This file is autogenerated do not edit!\n")
        f.write("Created by spinn_utilities/configs/config_documentor.py\n")
        f.write("Based on the default cfg files\n")
        f.write("See notes section at the bottom of this file.\n")
        f.write("-->\n")
        f.write("This guide covers the cfg settings "
                "and the reports created.\n")

    def _md_section(self, section: str, f: TextIO) -> None:
        """
        Writes the markdown for one section.
        """
        f.write(f'# <a name="{section}"></a> {section}\n')
        if section in self._docs:
            _md_write_doc(f, self._docs[section])
        titles = list(self._sections[section])
        titles.sort()
        for title in titles:
            f.write(f"* [{title}](#{title})\n")
        for title in titles:
            group = self._sections[section][title]
            group.md(f)

    def md_reports(self, f: TextIO) -> None:
        """
        Writes in markdown format a list of links from paths to cfg options.
        """
        f.write('# <a name="report_files"></a> Report Files\n')
        p_map = dict()
        for section in self._sections:
            for group in self._sections[section].values():
                for path in group.paths():
                    p_map[path] = _make_link(group.title)
        p_map = dict(sorted(p_map.items()))
        for path, title in p_map.items():
            f.write(f"  * [{path}](#{title})\n")
        f.write("\n\n")

    def md_notes(self, f: TextIO) -> None:
        """
        Copied the notes file into this markdown file
        """
        class_file = sys.modules[self.__module__].__file__
        assert class_file is not None
        abs_class_file = os.path.abspath(class_file)
        class_dir = os.path.dirname(abs_class_file)
        notes_path = os.path.join(class_dir, 'notes.md')
        with open(notes_path, encoding="utf-8") as notesfile:
            lines = notesfile.readlines()
            f.writelines(lines)

    def md_configs(self, filepath: str) -> None:
        """
        Converts the cfg files into markdown at the path specified.
        """
        with open(filepath, mode="w", encoding="utf-8") as f:
            self._md_header(f)
            f.write("* CFG Sections\n")
            for section in self._sections:
                f.write(f"  * [{section}](#{section})\n")
            f.write("* [Report Files](#report_files)\n")
            f.write("* [Notes for Developers](#notes)\n")

            for section in self._sections:
                self._md_section(section, f)
            self.md_reports(f)
            self.md_notes(f)
