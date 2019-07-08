# Copyright (c) 2018-2019 The University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os
import yaml
import io
import importlib
import argparse
import sys

from spinn_utilities.citation import CitationUpdaterAndDoiGenerator

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


class CitationAggregator(object):
    """ Helper class for building a citation file which references all \
        dependencies
    """

    def __init__(self):
        pass

    def create_aggregated_citation_file(
            self, module_to_start_at, aggregated_citation_file):
        """ Entrance method for building the aggregated citation file

        :param module_to_start_at:\
            the top level module to figure out its citation file for
        :type module_to_start_at: python module
        :param aggregated_citation_file: file name of aggregated citation file
        :type file_path_of_aggregated_citation_file: str
        :rtype: None
        """

        # get the top citation file to add references to
        top_citation_file_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(module_to_start_at.__file__))), CITATION_FILE)
        modules_seen_so_far = list()
        with open(top_citation_file_path, 'r') as stream:
            top_citation_file = yaml.safe_load(stream)
        top_citation_file[REFERENCES_YAML_POINTER] = list()

        # get the dependency list
        requirements_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_to_start_at.__file__))), REQUIREMENTS_FILE)
        c_requirements_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_to_start_at.__file__))), C_REQUIREMENTS_FILE)

        # attempt to get python PYPI to import command map
        pypi_to_import_map_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_to_start_at.__file__))),
            PYPI_TO_IMPORT_FILE)
        pypi_to_import_map = None
        if os.path.isfile(pypi_to_import_map_file):
            pypi_to_import_map = self._read_pypi_import_map(
                pypi_to_import_map_file)

        if os.path.isfile(requirements_file_path):
            with open(requirements_file_path, "r") as r_file:
                for line in r_file:
                    module = line.strip()
                    if module.startswith("#"):
                        continue
                    if module not in modules_seen_so_far:
                        import_name = pypi_to_import_map.get(module, module)
                        try:
                            imported_module = importlib.import_module(
                                import_name)
                            self._handle_python_dependency(
                                top_citation_file, imported_module,
                                modules_seen_so_far,
                                pypi_to_import_map[module])
                        except Exception as e:  # pragma: no cover
                            print("Error handling python dependency {}: {}"
                                  .format(module, str(e)))

        if os.path.isfile(c_requirements_file_path):
            with open(c_requirements_file_path, "r") as r_file:
                for line in r_file:
                    module = line.strip()
                    if module.startswith("#"):
                        continue
                    if module not in modules_seen_so_far:
                        self._handle_c_dependency(
                            top_citation_file, module, modules_seen_so_far)

        # write citation file with updated fields
        with io.open(
                aggregated_citation_file, 'w', encoding='utf8') as outfile:
            yaml.dump(top_citation_file, outfile, default_flow_style=False,
                      allow_unicode=True)

    @staticmethod
    def _read_pypi_import_map(aggregated_citation_file):
        """ Read the PYPI to import name map

        :param aggregated_citation_file: file path to the PYPI map
        :return: map between PYPI names and import names
        """
        pypi_to_import_map = dict()
        for line in open(aggregated_citation_file, "r"):
            [pypi, import_command] = line.split(":")
            pypi_to_import_map[pypi] = import_command.split("\n")[0]
        return pypi_to_import_map

    def _handle_c_dependency(
            self, top_citation_file, module, modules_seen_so_far):
        """ Handle a c code dependency

        :param top_citation_file: YAML file for the top citation file
        :param module: module to find
        :type top_citation_file: YAML file
        :type module: str
        :return: None
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
            print("Could not find C dependency {}".format(module))

    @staticmethod
    def locate_path_for_c_dependency(true_software_name):
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
            self, reference_entry, software_path, modules_seen_so_far):
        """ Go though the top level path and tries to locate other cff \
            files that need to be added to the references pile

        :param reference_entry:\
            The reference entry to add new dependencies as references for.
        :param software_path: the path to search in
        :rtype: None
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
                modules_seen_so_far.append(
                    possible_extra_citation_file.split(".")[0])

    def _handle_python_dependency(
            self, top_citation_file, imported_module, modules_seen_so_far,
            module_name):
        """ Handle a python dependency

        :param top_citation_file: YAML file for the top citation file
        :type top_citation_file: YAML file
        :param imported_module: the actual imported module
        :type imported_module: ModuleType
        :param modules_seen_so_far: \
            list of names of dependencies already processed
        :type modules_seen_so_far: list
        :param module_name: the name of this module to consider as a dependency
        :type module_name: str
        :rtype: None
        """
        # get modules citation file
        citation_level_dir = os.path.abspath(imported_module.__file__)
        m_path = module_name.replace(".", os.sep)
        last_citation_level_dir = None
        while (not citation_level_dir.endswith(m_path) and
               last_citation_level_dir != citation_level_dir):
            last_citation_level_dir = citation_level_dir
            citation_level_dir = os.path.dirname(citation_level_dir)
        if citation_level_dir == last_citation_level_dir:  # pragma: no cover
            raise Exception("Folder for module {} not found".format(
                module_name))

        # get the reference data for the reference
        reference_entry = self._process_reference(
            citation_level_dir, imported_module, modules_seen_so_far,
            module_name)

        if reference_entry is not None:
            # append to the top citation file
            top_citation_file[REFERENCES_YAML_POINTER].append(reference_entry)

    def _process_reference(
            self, citation_level_dir, imported_module, modules_seen_so_far,
            module_name):
        """ Take a module level and tries to locate and process a citation file

        :param citation_level_dir: \
            the expected level where the CITATION.cff should be
        :type citation_level_dir: str
        :param imported_module: the module after being imported
        :type imported_module: python module
        :param modules_seen_so_far: list of dependencies already processed
        :type modules_seen_so_far: list
        :return: the reference entry in json format
        :rtype: dict
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

        modules_seen_so_far.append(imported_module)
        return reference_entry

    @staticmethod
    def _try_to_find_version(imported_module, module_name):
        """ Try to locate a version file or version data to auto-generate \
            minimal citation data.

        :param imported_module:\
            the module currently trying to find the version of
        :type imported_module: python module
        :return: reference entry for this python module
        :rtype: dict
        """
        reference_entry = dict()
        reference_entry[REFERENCES_TYPE_TYPE] = REFERENCES_SOFTWARE_TYPE
        reference_entry[REFERENCES_TITLE_TYPE] = module_name
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
            reference_entry[REFERENCES_VERSION_TYPE] = \
                imported_module._version
        return reference_entry

    @staticmethod
    def _read_and_process_reference_entry(dependency_citation_file_path):
        """ Read a CITATION.cff and makes it a reference for a higher level \
            citation file.

        :param dependency_citation_file_path: path to a CITATION.cff file
        :type dependency_citation_file_path: str
        :return: reference entry for the higher level citation.cff
        :rtype: dict
        """
        reference_entry = dict()

        with open(dependency_citation_file_path, 'r') as stream:
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


def generate_aggregate(arguments=None):
    """ Generates a single citation.cff from others

    :param output_path: Where to write the aggregate file
    :param top_module: the module to start aggregating the citation.cffs from
    :param doi_title: the title of the DOI
    :param zenodo_access_token: the access token for Zenodo
    :param tools_doi: the DOI of the tools
    :rtype: None
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
