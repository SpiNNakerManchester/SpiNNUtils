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

from collections import defaultdict
import logging
import os
from typing import List, Optional

from spinn_utilities.log import FormatAdapter
from spinn_utilities.ordered_set import OrderedSet

logger = FormatAdapter(logging.getLogger(__file__))


class ExecutableFinder(object):
    """
    Manages a set of folders in which to search for binaries,
    and allows for binaries to be discovered within this path.
    """
    __slots__ = [
        "_binary_search_paths",
        "_binary_log",
        "_paths_log"]

    def __init__(self) -> None:
        # not using UtilsDataView due to circular import
        global_reports = os.environ.get("GLOBAL_REPORTS", None)
        if global_reports:
            if not os.path.exists(global_reports):
                # It might now exist if run in parallel
                try:
                    os.makedirs(global_reports)
                except FileExistsError:
                    pass
            self._paths_log: Optional[str] = os.path.join(
                global_reports, "binary_paths_used.log")
            self._binary_log: Optional[str] = os.path.join(
                global_reports, "binary_files_used.log")

        else:
            self._paths_log = None
            self._binary_log = None

        self._binary_search_paths: OrderedSet[str] = OrderedSet()

    def add_path(self, path: str) -> None:
        """
        Adds a path to the set of folders to be searched.  The path is
        added to the end of the list, so it is searched after all the
        paths currently in the list.

        :param path: The path to add
        """
        self._binary_search_paths.add(path)
        if self._paths_log:
            with open(self._paths_log, "a", encoding="utf-8") as log_file:
                log_file.write(path)
                log_file.write("\n")

    @property
    def binary_paths(self) -> str:
        """
        The set of folders to search for binaries, as a printable
        colon-separated string.
        """
        return " : ".join(self._binary_search_paths)

    def check_executable_path(self, executable_name: str) -> bool:
        """
        Checks for an executable within the set of folders.

        Unlike get_executable_path(s) does not log the path as used.

        :param executable_name: The name of the executable to find
        :return: True if found. Ie get_executable_path would return work
        """
        # Loop through search paths
        for path in self._binary_search_paths:
            # Rebuild filename
            potential_filename = os.path.join(path, executable_name)

            # If this filename exists, return it
            if os.path.isfile(potential_filename):
                return True
        return False

    def get_executable_path(self, executable_name: str) -> str:
        """
        Finds an executable within the set of folders. The set of folders
        is searched sequentially and the first match is returned.

        :param executable_name: The name of the executable to find
        :return: The full path of the discovered executable
        :raises KeyError: If no executable was found in the set of folders
        """
        # Loop through search paths
        for path in self._binary_search_paths:
            # Rebuild filename
            potential_filename = os.path.join(path, executable_name)

            # If this filename exists, return it
            if os.path.isfile(potential_filename):
                if self._binary_log and "unittests" not in potential_filename:
                    with open(self._binary_log, "a", encoding="utf-8") \
                            as log_file:
                        log_file.write(potential_filename)
                        log_file.write("\n")
                return potential_filename

        # No executable found
        raise KeyError(f"Executable {executable_name} not found in paths "
                       f"f{list(self._binary_search_paths)}")

    def get_executable_paths(self, executable_names: str) -> List[str]:
        """
        Finds each executable within the set of folders.

        The names are assumed to be comma separated
        The set of folders is searched sequentially
        and the first match for each name is returned.

        Names not found are ignored and not added to the list.

        :param executable_names: The name of the executable to find.
            Assumed to be comma separated.
        :return:
            The full path of the discovered executable, or ``None`` if no
            executable was found in the set of folders
        """
        results = list()
        for name in executable_names.split(","):
            try:
                results.append(self.get_executable_path(name))
            except KeyError:
                pass
        return results

    def print_files_by_directory(self, files: List[str]) -> None:
        """
        Prints the files sorted by directory

        :param files: List of full paths to the files
        """
        if len(files) == 0:
            return

        if len(files) == 1:
            print(files[0])
            return

        files.sort()

        # Find a shared parent to remove
        directory = os.path.dirname(files[0])
        parent = os.path.dirname(directory)

        # Find the path part common to all
        c_pref = os.path.commonprefix(files)
        while len(c_pref) > 0 and c_pref[len(c_pref) - 1] != os.sep:
            c_pref = c_pref[:-1]

        # cut either the common part or the parent plus the file divider
        cut = min(len(c_pref), len(parent)+1)

        # group files by directory
        files_by_dir = defaultdict(list)
        for binary in files:
            directory, file = os.path.split(binary[cut:])
            files_by_dir[directory].append(file)

        for directory in files_by_dir:
            print(directory)
            for file in files_by_dir[directory]:
                print(f"\t{file}")

    def check_logs(self) -> None:
        """
        Compares the aplx files used against the ones available for use

        Reports the aplx files never used.
        """
        if not self._paths_log:
            print("environ GLOBAL_REPORTS not set!")
            return

        folders = set()
        with open(self._paths_log, "r", encoding="utf-8") as log_file:
            for line in log_file:
                folders.add(line.strip())

        in_folders = set()
        for folder in folders:
            try:
                for file_name in os.listdir(folder):
                    if file_name.endswith(".aplx"):
                        in_folders.add(os.path.join(folder, file_name))
            except FileNotFoundError:
                logger.info(f"Directory {folder} not found")

        used_binaries = set()
        if self._binary_log:
            with open(self._binary_log, "r", encoding="utf-8") as log_file:
                for line in log_file:
                    used_binaries.add(line.strip())

        missing = in_folders - used_binaries
        print(f"{len(used_binaries)} binaries asked for. "
              f"{len(missing)} binaries never asked for.")
        print("Used binaries:")
        self.print_files_by_directory(list(used_binaries))
        print("Binaries not tested:")
        self.print_files_by_directory(list(missing))

    def clear_logs(self) -> None:
        """
        Deletes log files from previous runs
        """
        if not self._paths_log:
            print("environ GLOBAL_REPORTS not set!")
            return
        if self._paths_log and os.path.isfile(self._paths_log):
            os.remove(self._paths_log)
        if self._binary_log and os.path.isfile(self._binary_log):
            os.remove(self._binary_log)


if __name__ == '__main__':
    executable_finder = ExecutableFinder()
    executable_finder.check_logs()
    executable_finder.clear_logs()
