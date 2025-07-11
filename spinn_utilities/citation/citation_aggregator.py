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

import os
import yaml
import io
import importlib
import argparse
from types import ModuleType
from typing import Any, Dict, List, Optional, Set, Union
import sys
from .citation_updater_and_doi_generator import CitationUpdaterAndDoiGenerator

ENCODING = "utf-8"

REQUIREMENTS_FILE = "requirements.txt"
C_REQUIREMENTS_FILE = "c_requirements.txt"
CITATION_FILE = "CITATION.cff"
PYPI_TO_IMPORT_FILE = "pypi_to_import"

REFERENCES_YAML_POINTER = "references"
REFERENCE_TYPE = "software"
REFERENCES_AUTHORS_TYPE = "authors"
REFERENCES_TITLE_TYPE = "title"
REFERENCES_VERSION_TYPE = "version"
REFERENCES_DATE_TYPE = "date-released"
REFERENCES_URL_TYPE = "url"
REFERENCES_REPO_TYPE = "repository"
REFERENCES_CONTACT_TYPE = "contact"
REFERENCES_TYPE_TYPE = "type"
REFERENCES_SOFTWARE_TYPE = "software"

CITATION_DOI_TYPE = 'identifier'

# pylint: skip-file

_SEEN_TYPE = Set[Union[ModuleType, str, None]]


class CitationAggregator(object):
    """
    Helper class for building a citation file which references all
    dependencies.
    """

    def create_aggregated_citation_file(
            self, module_to_start_at: ModuleType,
            aggregated_citation_file: str) -> None:
        """
        Entrance method for building the aggregated citation file.

        :param module_to_start_at:
            the top level module to figure out its citation file for
        :param aggregated_citation_file:
            file name of aggregated citation file
        """
        # get the top citation file to add references to
        module_file: Optional[str] = module_to_start_at.__file__
        assert module_file is not None
        top_citation_file_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(module_file))), CITATION_FILE)
        modules_seen_so_far: _SEEN_TYPE = set()
        modules_seen_so_far.add("")
        with open(top_citation_file_path, encoding=ENCODING) as stream:
            top_citation_file: Dict[str, Any] = yaml.safe_load(
                stream)
        top_citation_file[REFERENCES_YAML_POINTER] = list()

        # get the dependency list
        requirements_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_file))), REQUIREMENTS_FILE)
        c_requirements_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_file))), C_REQUIREMENTS_FILE)

        # attempt to get python PYPI to import command map
        pypi_to_import_map_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_file))), PYPI_TO_IMPORT_FILE)
        pypi_to_import_map = None
        if os.path.isfile(pypi_to_import_map_file):
            pypi_to_import_map = self._read_pypi_import_map(
                pypi_to_import_map_file)

        if os.path.isfile(requirements_file_path):
            with open(requirements_file_path, encoding="utf-8") as r_file:
                for line in r_file:
                    module = line.strip()
                    if module.startswith("#"):
                        continue
                    if module not in modules_seen_so_far:
                        assert pypi_to_import_map is not None
                        import_name = pypi_to_import_map.get(module, module)
                        #  pylint: disable=broad-except
                        try:
                            imported_module = importlib.import_module(
                                import_name)
                            self._handle_python_dependency(
                                top_citation_file, imported_module,
                                modules_seen_so_far,
                                pypi_to_import_map[module])
                        except Exception as e:  # pragma: no cover
                            print("Error handling python dependency "
                                  f"{module}: {e}")

        if os.path.isfile(c_requirements_file_path):
            with open(c_requirements_file_path, encoding=ENCODING) as r_file:
                for line in r_file:
                    module = line.strip()
                    if module.startswith("#"):
                        continue
                    if module not in modules_seen_so_far:
                        self._handle_c_dependency(
                            top_citation_file, module, modules_seen_so_far)

        # write citation file with updated fields
        with io.open(
                aggregated_citation_file, 'w', encoding=ENCODING) as outfile:
            yaml.dump(top_citation_file, outfile, default_flow_style=False,
                      allow_unicode=True)

    @staticmethod
    def _read_pypi_import_map(aggregated_citation_file: str) -> Dict[str, str]:
        """
        Read the PYPI to import name map.

        :param aggregated_citation_file: path to the PYPI map file
        :return: map between PYPI names and import names
        """
        pypi_to_import_map: Dict[str, str] = dict()
        with open(aggregated_citation_file, encoding=ENCODING) as f:
            for line in f:
                [pypi, import_command] = line.split(":")
                pypi_to_import_map[pypi] = import_command.split("\n")[0]
        return pypi_to_import_map

    def _handle_c_dependency(
            self, top_citation_file:  Dict[str, Any], module: str,
            modules_seen_so_far: _SEEN_TYPE) -> None:
        """
        Handle a C code dependency.

        :param top_citation_file: YAML file for the top citation file
        :param module: module to find
        :param modules_seen_so_far:
        """
        cleaned_path = self.locate_path_for_c_dependency(module)
        if cleaned_path is not None:
            # process reference
            reference_entry = self._process_reference(
                cleaned_path, None, modules_seen_so_far, module)

            # append to the top citation file
            top_citation_file[REFERENCES_YAML_POINTER].append(
                reference_entry)
            self._search_for_other_c_references(
                reference_entry, cleaned_path, modules_seen_so_far)
        else:
            print(f"Could not find C dependency {module}")

    @staticmethod
    def locate_path_for_c_dependency(true_software_name: str) -> Optional[str]:
        """
        Tries to find the software in the environment PATH (s)

        :returns: Path to the software if found
        """
        environment_path_variable = os.environ.get('PATH')
        if environment_path_variable is not None:
            software_paths = environment_path_variable.split(":")
            for software_path in software_paths:
                # clear path to have repository name at end
                last_version = None
                cleaned_path = software_path
                while ((cleaned_path != last_version) and (
                        not (cleaned_path.split(os.sep)[-1] ==
                             true_software_name))):
                    last_version = cleaned_path
                    cleaned_path = os.path.dirname(cleaned_path)

                if cleaned_path != last_version:
                    return cleaned_path
        return None

    def _search_for_other_c_references(
            self, reference_entry:  Dict[str, Any], software_path: str,
            modules_seen_so_far: _SEEN_TYPE) -> None:
        """
        Go through the top level path and tries to locate other CFF
        files that need to be added to the references pile.

        :param reference_entry:
            The reference entry to add new dependencies as references for.
        :param software_path: the path to search in
        :param modules_seen_so_far:
        """
        for possible_extra_citation_file in os.listdir(software_path):
            if possible_extra_citation_file.endswith(".cff"):
                dependency_reference_entry = \
                    self._read_and_process_reference_entry(
                        os.path.join(software_path,
                                     possible_extra_citation_file))
                reference_entry[REFERENCES_YAML_POINTER] = list()
                reference_entry[REFERENCES_YAML_POINTER].append(
                    dependency_reference_entry)
                modules_seen_so_far.add(
                    possible_extra_citation_file.split(".")[0])

    def _handle_python_dependency(
            self, top_citation_file: Dict[str, Any],
            imported_module: ModuleType, modules_seen_so_far: _SEEN_TYPE,
            module_name: str) -> None:
        """
        Handle a python dependency.

        :param top_citation_file:
            YAML file for the top citation file
        :param imported_module: the actual imported module
        :param modules_seen_so_far:
            list of names of dependencies already processed
        :param module_name:
            the name of this module to consider as a dependency
        :raises FileNotFoundError:
        """
        # get modules citation file
        module_path = imported_module.__file__
        assert module_path is not None
        citation_level_dir = os.path.abspath(module_path)
        m_path = module_name.replace(".", os.sep)
        last_citation_level_dir = None
        while (not citation_level_dir.endswith(m_path) and
               last_citation_level_dir != citation_level_dir):
            last_citation_level_dir = citation_level_dir
            citation_level_dir = os.path.dirname(citation_level_dir)
        if citation_level_dir == last_citation_level_dir:  # pragma: no cover
            raise FileNotFoundError(
                f"Folder for module {module_name} not found")

        # get the reference data for the reference
        reference_entry = self._process_reference(
            citation_level_dir, imported_module, modules_seen_so_far,
            module_name)

        if reference_entry is not None:
            # append to the top citation file
            top_citation_file[REFERENCES_YAML_POINTER].append(reference_entry)

    def _process_reference(
            self, citation_level_dir: str,
            imported_module: Optional[ModuleType],
            modules_seen_so_far: _SEEN_TYPE,
            module_name: str) -> Dict[str, Any]:
        """
        Take a module level and tries to locate and process a citation file.

        :param citation_level_dir:
            the expected level where the ``CITATION.cff`` should be
        :param imported_module: the module after being imported
        :param modules_seen_so_far:
            list of dependencies already processed
        :return: the reference entry in JSON format
        """
        # if it exists, add it as a reference to the top one
        if os.path.isfile(os.path.join(citation_level_dir, CITATION_FILE)):
            reference_entry = self._read_and_process_reference_entry(
                os.path.join(citation_level_dir, CITATION_FILE))

        # check that the file isn't one above (not installed, but developer
        # mode)
        elif os.path.isfile(os.path.join(os.path.dirname(
                os.path.abspath(citation_level_dir)), CITATION_FILE)):
            reference_entry = self._read_and_process_reference_entry(
                os.path.join(os.path.dirname(
                    os.path.abspath(citation_level_dir)), CITATION_FILE))

        # if no citation file exists, do an attempt to find a version to build
        # from
        else:
            # one from version
            reference_entry = self._try_to_find_version(
                imported_module, module_name)

        modules_seen_so_far.add(imported_module)
        return reference_entry

    @staticmethod
    def _try_to_find_version(
            imported_module: Optional[ModuleType],
            module_name: str) -> Dict[str, Any]:
        """
        Try to locate a version file or version data to auto-generate
        minimal citation data.

        :param imported_module:
            the module currently trying to find the version of
        :return: reference entry for this python module
        """
        reference_entry: Dict[str, Any] = dict()
        reference_entry[REFERENCES_TYPE_TYPE] = REFERENCES_SOFTWARE_TYPE
        reference_entry[REFERENCES_TITLE_TYPE] = module_name
        if imported_module is None:
            return reference_entry
        if (hasattr(imported_module, "__version_day__") and
                hasattr(imported_module, "__version_month__") and
                hasattr(imported_module, "__version_year__")):
            reference_entry[REFERENCES_DATE_TYPE] = \
                CitationUpdaterAndDoiGenerator.\
                convert_text_date_to_date(
                    version_day=imported_module.__version_day__,
                    version_month=imported_module.__version_month__,
                    version_year=imported_module.__version_year__)
        if hasattr(imported_module, "__version__"):
            reference_entry[REFERENCES_VERSION_TYPE] = \
                imported_module.__version__
        elif hasattr(imported_module, "version"):
            reference_entry[REFERENCES_VERSION_TYPE] = \
                imported_module.version
        elif hasattr(imported_module, "_version"):
            # pylint: disable=protected-access
            reference_entry[REFERENCES_VERSION_TYPE] = \
                imported_module._version
        return reference_entry

    @staticmethod
    def _read_and_process_reference_entry(
            dependency_citation_file_path: str) -> Dict[str, Any]:
        """
        Read a ``CITATION.cff`` and makes it a reference for a higher
        level citation file.

        :param dependency_citation_file_path:
            path to a `CITATION.cff` file
        :return: reference entry for the higher level `CITATION.cff`
        """
        reference_entry = dict()

        with open(dependency_citation_file_path, 'r', encoding="utf-8") \
                as stream:
            dependency_citation_file = yaml.safe_load(stream)

            reference_entry[REFERENCES_TYPE_TYPE] = REFERENCES_SOFTWARE_TYPE
            reference_entry[REFERENCES_AUTHORS_TYPE] = \
                dependency_citation_file[REFERENCES_AUTHORS_TYPE]
            reference_entry[REFERENCES_TITLE_TYPE] = \
                dependency_citation_file[REFERENCES_TITLE_TYPE]
            reference_entry[REFERENCES_CONTACT_TYPE] = \
                dependency_citation_file[REFERENCES_CONTACT_TYPE]
            reference_entry[REFERENCES_VERSION_TYPE] = \
                dependency_citation_file[REFERENCES_VERSION_TYPE]
            reference_entry[REFERENCES_DATE_TYPE] = \
                dependency_citation_file[REFERENCES_DATE_TYPE]
            reference_entry[REFERENCES_URL_TYPE] = \
                dependency_citation_file[REFERENCES_URL_TYPE]
            reference_entry[REFERENCES_REPO_TYPE] = \
                dependency_citation_file[REFERENCES_REPO_TYPE]
        return reference_entry


def generate_aggregate(arguments: Optional[List[str]] = None) -> None:
    """
    Command-line tool to generate a single ``citation.cff`` from others.

    :param arguments: Command line arguments.

        * ``--output_path``: \
            Where to write the aggregate file
        * ``--top_module``: \
            The module to start aggregating the ``citation.cff``\\s from
        * ``--doi_title``: \
            The title of the DOI
        * ``--zenodo_access_token``: \
            The access token for Zenodo
        * ``--tools_doi``: \
            The DOI of the tools
    """
    parser = argparse.ArgumentParser(description="Aggregate Citations")
    parser.add_argument("output_path", help="The file to store the result in")
    parser.add_argument("top_module", help="The module to start with")
    parser.add_argument("--create_doi", action="store_true",
                        help="Create a DOI from the resulting citation"
                             " on Zenodo")
    parser.add_argument("--publish_doi", action="store_true",
                        help="Publish the DOI created")
    parser.add_argument("--doi_title",
                        help="The title to give the created DOI")
    parser.add_argument("--previous_doi",
                        help="The DOI this is a newer version of")
    parser.add_argument("--zenodo_access_token",
                        help="Access token for Zenodo")

    args = parser.parse_args(arguments)
    error = False
    if args.create_doi:  # pragma: no cover
        if not args.doi_title:
            print("--doi_title required when creating a DOI")
            error = True
        if not args.previous_doi:
            print("--previous_doi required when creating a DOI")
            error = True
        if not args.zenodo_access_token:
            print("--zenodo_access_token required when creating a DOI")
            error = True
    if args.publish_doi and not args.create_doi:  # pragma: no cover
        print("Cannot publish DOI without creating one")
        error = True
    if error:  # pragma: no cover
        parser.print_usage()
        sys.exit()

    top_module = importlib.import_module(args.top_module)

    citation_aggregator = CitationAggregator()
    citation_aggregator.create_aggregated_citation_file(
        top_module, args.output_path)
    citation_updater_and_dio_generator = CitationUpdaterAndDoiGenerator()
    citation_updater_and_dio_generator.update_citation_file_and_create_doi(
        citation_file_path=args.output_path,
        doi_title=args.doi_title,
        create_doi=args.create_doi, publish_doi=args.publish_doi,
        previous_doi=args.previous_doi,
        zenodo_access_token=args.zenodo_access_token,
        module_path=os.path.dirname(top_module.__path__[0]))


if __name__ == "__main__":
    generate_aggregate()  # pragma: no cover
