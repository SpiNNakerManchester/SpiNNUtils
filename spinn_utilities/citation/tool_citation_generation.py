import os
import yaml
import io
import importlib

from spinn_utilities.citation.citation_and_doi_updater import \
    CitationUpdaterAndDoiGenerator

REQUIREMENTS_FILE = "requirements.txt"
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

AGGREGATE_FILE_NAME = CITATION_FILE


class CitationAggregator(object):
    """ helper class for building a citation file which references all \
        dependencies
    """

    def __init__(self):
        pass

    @staticmethod
    def locate_citation_doi(module_to_start_at):
        top_citation_file = None
        top_citation_file_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(module_to_start_at.__file__))), CITATION_FILE)
        with open(top_citation_file_path, 'r') as stream:
            try:
                top_citation_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return top_citation_file[CITATION_DOI_TYPE]

    def create_aggregated_citation_file(
            self, module_to_start_at, file_path_of_aggregated_citation_file):
        """ entrance method for building the aggregated citation file

        :param module_to_start_at: the top level module to figure out its \
        citation file for
        :type module_to_start_at: python module
        :param file_path_of_aggregated_citation_file: location where to put \
        the aggregated citation file
        :type file_path_of_aggregated_citation_file: filepath
        :rtype: None
        """

        # get the top citation file to add references to
        top_citation_file_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(module_to_start_at.__file__))), CITATION_FILE)
        top_citation_file = None
        modules_seen_so_far = list()
        with open(top_citation_file_path, 'r') as stream:
            try:
                top_citation_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        top_citation_file[REFERENCES_YAML_POINTER] = list()

        # get the dependency list
        requirements_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_to_start_at.__file__))),
            REQUIREMENTS_FILE)

        # attempt to get python pypi to import command map
        pypi_to_import_map_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(
                module_to_start_at.__file__))),
            PYPI_TO_IMPORT_FILE)
        pypi_to_import_map = None
        if os.path.isfile(pypi_to_import_map_file):
            pypi_to_import_map = self._read_pypi_import_map(
                pypi_to_import_map_file)

        if os.path.isfile(requirements_file_path):
            for line in open(requirements_file_path, "r"):
                module_to_get_requirements_for = line.split(" ")[0]
                module_to_get_requirements_for = \
                    module_to_get_requirements_for.split("\n")[0]
                if module_to_get_requirements_for not in modules_seen_so_far:
                    self._handle_dependency(
                        top_citation_file, module_to_get_requirements_for,
                        pypi_to_import_map, modules_seen_so_far)

        # write citation file with updated fields
        aggregated_citation_file = os.path.join(
            file_path_of_aggregated_citation_file, AGGREGATE_FILE_NAME)
        with io.open(
                aggregated_citation_file, 'w', encoding='utf8') as outfile:
            yaml.dump(top_citation_file, outfile, default_flow_style=False,
                      allow_unicode=True)

    @staticmethod
    def _read_pypi_import_map(aggregated_citation_file):
        """ reads the pypi to import name map

        :param aggregated_citation_file: file path to the pypi map
        :return: map between pypi names and import names
        """
        pypi_to_import_map = dict()
        for line in open(aggregated_citation_file, "r"):
            [pypi, import_command] = line.split(":")
            pypi_to_import_map[pypi] = import_command.split("\n")[0]
        return pypi_to_import_map

    # noinspection PyBroadException
    def _handle_dependency(
            self, top_citation_file, module_to_get_requirements_for,
            pypi_to_import_map, modules_seen_so_far):
        """ handles a dependency, assumes its either python or c code

        :param top_citation_file: yaml file for the top citation file
        :param module_to_get_requirements_for: module to import
        :type top_citation_file: yaml file
        :type module_to_get_requirements_for: str
        :param pypi_to_import_map: map between pypi name and the python import
        :type pypi_to_import_map: dict
        :param modules_seen_so_far:
        :type modules_seen_so_far:
        :return: None
        """

        # determine name for import
        if module_to_get_requirements_for in pypi_to_import_map:
            import_name = pypi_to_import_map[module_to_get_requirements_for]
        else:
            import_name = module_to_get_requirements_for
        try:
            imported_module = importlib.import_module(import_name)
            self._handle_python_dependency(
                top_citation_file, imported_module, modules_seen_so_far,
                pypi_to_import_map[module_to_get_requirements_for])
        except ImportError:
            # assume now that its a c code module.
            self._handle_c_dependency(
                top_citation_file, module_to_get_requirements_for,
                modules_seen_so_far)
        except Exception:
            print("not handling this dependency")

    def _handle_c_dependency(
            self, top_citation_file, module_to_get_requirements_for,
            modules_seen_so_far):
        """ handles a c code dependency

        :param top_citation_file: yaml file for the top citation file
        :param module_to_get_requirements_for: module to import
        :type top_citation_file: yaml file
        :type module_to_get_requirements_for: str
        :return: None
        """

        true_software_name = module_to_get_requirements_for.split("#")[1]
        cleaned_path = self.locate_path_for_c_dependency(true_software_name)
        if cleaned_path is not None:
            # process reference
            reference_entry = self._process_reference(
                cleaned_path, None, modules_seen_so_far)

            # append to the top citation file
            top_citation_file[REFERENCES_YAML_POINTER].append(
                reference_entry)
            self._search_for_other_c_references(
                reference_entry, cleaned_path, modules_seen_so_far)
        else:
            raise Exception("no idea what to do here")

    @staticmethod
    def locate_path_for_c_dependency(true_software_name):
        environment_path_variable = os.environ.get('PATH')
        if environment_path_variable is not None:
            software_paths = environment_path_variable.split(":")
            for software_path in software_paths:
                # clear path to have repo name at end
                last_version = None
                cleaned_path = software_path
                while ((cleaned_path != last_version) and (
                        not (cleaned_path.split(os.sep)[-1] ==
                             true_software_name))):
                    last_version = cleaned_path
                    cleaned_path = os.path.dirname(cleaned_path)

                if cleaned_path != last_version:
                    # add the ; bit back in.
                    cleaned_path = \
                        software_path.split(os.pathsep)[1] + ":" + cleaned_path
                    return cleaned_path
        return None

    def _search_for_other_c_references(
            self, reference_entry, software_path, modules_seen_so_far):
        """ goes though the top level path and tries to locate other cff \
        files that need to be added to the references pile

        :param reference_entry: The reference entry to add new dependencies \
        as references for.
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
        """ handles a python dependency

        :param top_citation_file: yaml file for the top citation file
        :type top_citation_file: yaml file
        :param imported_module: the actual imported module
        :type imported_module: ModuleType
        :param modules_seen_so_far: list of names of dependencies already \
        processed
        :type modules_seen_so_far: list
        :param module_name: the name of this module to consider as a dependency
        :type module_name: str
        :rtype: None
        """
        # get modules citation file
        citation_level_dir = os.path.abspath(imported_module.__file__)
        while (not citation_level_dir.split(os.sep)[-1].split(".")[0] ==
               module_name):
            citation_level_dir = os.path.dirname(citation_level_dir)

        # get the reference data for the reference
        reference_entry = self._process_reference(
            citation_level_dir, imported_module, modules_seen_so_far)

        if reference_entry is not None:
            # append to the top citation file
            top_citation_file[REFERENCES_YAML_POINTER].append(reference_entry)

    def _process_reference(
            self, citation_level_dir, imported_module, modules_seen_so_far):
        """ takes a module level and tries to locate and process a citation file

        :param citation_level_dir: the expected level where the CITATION.cff \
        should be
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

        # check that the file isnt one above (not installed, but developer
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
            reference_entry = self._try_to_find_version(imported_module)

        modules_seen_so_far.append(imported_module)
        return reference_entry

    @staticmethod
    def _try_to_find_version(imported_module):
        """ tries to locate a version file or version data to auto-generate \
        minimal citation data.

        :param imported_module: the module currently trying to find the \
        version of
        :type imported_module: python module
        :return: reference entry for this python module
        :rtype: dict
        """
        calls = ["_version", "version", "__version__"]
        reference_entry = dict()
        for call in calls:
            try:
                version = getattr(imported_module, call)
                reference_entry[REFERENCES_TYPE_TYPE] = (
                    REFERENCES_SOFTWARE_TYPE)
                if (hasattr(version, "__version_day__") and
                        hasattr(version, "__version_month__") and
                        hasattr(version, "__version_year__")):
                    reference_entry[REFERENCES_DATE_TYPE] = \
                        CitationUpdaterAndDoiGenerator.\
                        convert_text_date_to_date(
                            version_day=version.__version_day__,
                            version_month=version.__version_month__,
                            version_year=version.__version_year__)
                if hasattr(version, "__version__"):
                    reference_entry[REFERENCES_VERSION_TYPE] = (
                        version.__version__)
                reference_entry[REFERENCES_TITLE_TYPE] = imported_module
                return reference_entry
            except AttributeError:
                pass
            except Exception:
                "no idea what to do here, going to ignore it and go for"
                " basic entry"
        reference_entry[REFERENCES_TYPE_TYPE] = REFERENCES_SOFTWARE_TYPE
        reference_entry[REFERENCES_TITLE_TYPE] = imported_module
        return reference_entry

    @staticmethod
    def _read_and_process_reference_entry(dependency_citation_file_path):
        """ reads a CITATION.cff and makes it a reference for a higher level \
        citation file.

        :param dependency_citation_file_path: path to a CITATION.cff file
        :type dependency_citation_file_path: str
        :return: reference entry for the higher level citation.cff
        :rtype: dict
        """
        dependency_citation_file = None
        reference_entry = dict()

        with open(dependency_citation_file_path, 'r') as stream:
            try:
                dependency_citation_file = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

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
