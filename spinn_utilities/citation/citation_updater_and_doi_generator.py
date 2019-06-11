import yaml
import io
import requests
import zipfile
import unicodedata
import os
from time import strptime

CITATION_FILE_VERSION_FIELD = "version"
CITATION_FILE_DATE_FIELD = "date-released"
CITATION_AUTHORS_TYPE = "authors"
CITATION_AUTHOR_FIRST_NAME = "given-names"
CITATION_AUTHOR_SURNAME = "family-names"
CITATION_FILE_DESCRIPTION = "title"

ZENODO_DEPOSIT_GET_URL = "https://zenodo.org/api/deposit/depositions"
ZENODO_DEPOSIT_PUT_URL = \
    'https://zenodo.org/api/deposit/depositions/{}/files'
ZENODO_PUBLISH_URL = \
    'https://zenodo.org/api/deposit/depositions/{}/actions/publish'

ZENODO_RELATION_FIELD = "relation"
ZENODO_NEWER_VERSION_OF = 'isNewVersionOf'
ZENODO_SIBLING_OF = "cites"
ZENODO_ACCESS_TOKEN = 'access_token'
ZENODO_RELATED_IDENTIFIERS = 'related_identifiers'
ZENODO_CONTENT_TYPE = "Content-Type"
ZENODO_METADATA = 'metadata'
ZENODO_PRE_RESERVED_DOI = "prereserve_doi"
ZENODO_DOI_VALUE = "doi"
ZENODO_DEPOSIT_ID = 'id'
ZENODO_METADATA_TITLE = "title"
ZENODO_METATDATA_DESC = "description"
ZENODO_METADATA_CREATORS = "creators"
ZENODO_FILE = "file"
ZENODO_AUTHOR_NAME = "name"

AUTHOR_AFFILIATION = "affiliation"
AUTHOR_ORCID = "orcid"
IDENTIFIER = 'identifier'

ZENODO_VALID_STATUS_REQUEST_GET = 200
ZENODO_VALID_STATUS_REQUEST_POST = 201
ZENODO_VALID_STATUS_REQUEST_PUBLISH = 202


class CitationUpdaterAndDoiGenerator(object):

    def __init__(self):
        pass

    def update_citation_file_and_create_doi(
            self, citation_file_path, doi_title, create_doi, publish_doi,
            previous_doi, zenodo_access_token, module_path):
        """ Take a CITATION.cff file and updates the version and \
            date-released fields, and rewrites the CITATION.cff file.

        :param citation_file_path: The file path to the CITATION.cff file
        :param create_doi: \
            bool flag for using Zenodo DOI interface to grab a DOI
        :type create_doi: bool
        :param zenodo_access_token: the access token for Zenodo
        :type zenodo_access_token: str
        :param publish_doi: bool flag to publish the DOI on Zenodo
        :type publish_doi: bool
        :param previous_doi: the DOI to append the created DOI to
        :type previous_doi: str
        :param doi_title: the title for the created DOI
        :type doi_title: str
        :param module_path: path to the module to zip up
        :type module_path: str
        :param update_version:\
            bool for if we should update the citation version
        :type update_version: bool
        :rtype: None
        """

        # data holders
        deposit_id = None

        # read in YAML file
        with open(citation_file_path, 'r') as stream:
            yaml_file = yaml.safe_load(stream)

        # if creating a DOI, go and request one
        if create_doi:
            doi_id, deposit_id = self._request_doi(
                zenodo_access_token, previous_doi)
            yaml_file[IDENTIFIER] = doi_id

        # rewrite citation file with updated fields
        with io.open(citation_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(yaml_file, outfile, default_flow_style=False,
                      allow_unicode=True)

        # if creating a DOI, finish the request and possibly publish it
        if create_doi:
            self._finish_doi(
                deposit_id, zenodo_access_token, publish_doi, doi_title,
                yaml_file[CITATION_FILE_DESCRIPTION], yaml_file, module_path)

    def _request_doi(self, zenodo_access_token, previous_doi):
        """ Go to zenodo and requests a DOI

        :param zenodo_access_token: zenodo access token
        :type zenodo_access_token: str
        :param previous_doi: the previous DOI for this module, if exists
        :type previous_doi: str
        :param module_path: the path to the module to create a DOI for
        :return: the DOI id, and deposit id
        :rtype: str, str
        """

        # create link to previous version (if applicable)
        related = list()
        related.append({
            ZENODO_RELATION_FIELD: ZENODO_NEWER_VERSION_OF,
            IDENTIFIER: previous_doi})

        # get a request for a DOI
        request = requests.get(
            ZENODO_DEPOSIT_GET_URL,
            params={ZENODO_ACCESS_TOKEN: zenodo_access_token,
                    ZENODO_RELATED_IDENTIFIERS: related},
            json={}, headers={ZENODO_CONTENT_TYPE: "application/json"})

        # verify the DOI is valid
        if (request.status_code !=
                ZENODO_VALID_STATUS_REQUEST_GET):  # pragma: no cover
            raise Exception(
                "don't know what went wrong. got wrong status code when "
                "trying to request a DOI. Got error code {} with response "
                "content {}".format(request.status_code, request.content))

        # get empty upload
        request = requests.post(
            ZENODO_DEPOSIT_GET_URL,
            params={ZENODO_ACCESS_TOKEN: zenodo_access_token,
                    ZENODO_RELATED_IDENTIFIERS: related},
            json={}, headers={ZENODO_CONTENT_TYPE: "application/json"})

        # verify the DOI is valid
        if (request.status_code !=
                ZENODO_VALID_STATUS_REQUEST_POST):  # pragma: no cover
            raise Exception(
                "don't know what went wrong. got wrong status code when "
                "trying to get a empty upload. Got error code {} with response"
                " content {}".format(request.status_code, request.content))

        # get DOI and deposit id
        doi_id = unicodedata.normalize(
            'NFKD',
            (request.json()[ZENODO_METADATA][ZENODO_PRE_RESERVED_DOI]
             [ZENODO_DOI_VALUE])).encode('ascii', 'ignore')
        deposition_id = request.json()[ZENODO_DEPOSIT_ID]

        return doi_id, deposition_id

    def _finish_doi(
            self, deposit_id, access_token, publish_doi, title,
            doi_description, yaml_file, module_path):
        """ Finishes the DOI on zenodo

        :param deposit_id: the deposit id to publish
        :param access_token: the access token needed to publish
        :param title: the title of this DOI
        :param doi_description: the description for the DOI
        :param yaml_file: the citation file after its been read it
        :param publish_doi: bool flagging if we should publish the DOI
        :param files: the zipped up file for the zenodo DOI request
        :param module_path: the path to the module to DOI
        :rtype: None
        """

        zipped_file = self._zip_up_module(module_path)
        zipped_open_file = open(zipped_file, "rb")
        files = {ZENODO_FILE: zipped_open_file}

        data = self._fill_in_data(title, doi_description, yaml_file)

        r = requests.post(
            ZENODO_DEPOSIT_PUT_URL.format(deposit_id),
            params={ZENODO_ACCESS_TOKEN: access_token}, data=data, files=files)
        zipped_open_file.close()
        os.remove('module.zip')

        if (r.status_code !=
                ZENODO_VALID_STATUS_REQUEST_POST):  # pragma: no cover
            raise Exception(
                "don't know what went wrong. got wrong status code when "
                "trying to put files and data into the pre allocated DOI. "
                "Got error code {} with response content {}".format(
                    r.status_code, r.content))

        # publish DOI
        if publish_doi:
            request = requests.post(
                ZENODO_PUBLISH_URL.format(deposit_id),
                params={ZENODO_ACCESS_TOKEN: access_token})
            if (request.status_code !=
                    ZENODO_VALID_STATUS_REQUEST_PUBLISH):  # pragma: no cover
                raise Exception(
                    "don't know what went wrong. got wrong status code when "
                    "trying to publish the DOI")

    def _zip_up_module(self, module_path):
        """ Zip up a module

        :param module_path: the path to the module to zip up
        :return: a opened reader for the zip file generated
        """
        if os.path.isfile('module.zip'):
            os.remove('module.zip')

        avoids = [".git", ".gitignore", ".gitattributes", ".travis.yml",
                  ".github", "model_binaries", "common_model_binaries",
                  ".coveragerc", ".idea"]

        module_zip_file = zipfile.ZipFile(
            'module.zip', 'w', zipfile.ZIP_DEFLATED)
        self._zip_walker(module_path, avoids, module_zip_file)
        module_zip_file.close()
        return 'module.zip'

    @staticmethod
    def _zip_walker(module_path, avoids, module_zip_file):
        """ Traverse the module and its subdirectories and only adds to the \
            files to the zip which are not within a avoid directory that.

        :param module_path: the path to start the search at
        :param avoids: the set of avoids to avoid
        :param module_zip_file: the zip file to put into
        :rtype: None
        """

        for directory_path, _, files in os.walk(module_path):
            avoid = False
            for directory_name in directory_path.split(os.sep):
                if directory_name in avoids:
                    avoid = True
                    break
            if not avoid:
                for potential_zip_file in files:
                    # if safe to zip, zip
                    if potential_zip_file not in avoids:
                        module_zip_file.write(
                            os.path.join(directory_path, potential_zip_file))

    @staticmethod
    def _fill_in_data(doi_title, doi_description, yaml_file):
        """ Add in data to the Zenodo metadata

        :param doi_title: the title of the DOI
        :type doi_title: str
        :param doi_description: the description of the DOI
        :type doi_description: str
        :param yaml_file: the citation file once read into the system
        :type yaml_file: dict
        :return: dict containing zenodo metadata
        :rtype: dict
        """
        data = dict()
        data[ZENODO_METADATA] = dict()

        # add basic meta data
        data[ZENODO_METADATA][ZENODO_METADATA_TITLE] = doi_title
        data[ZENODO_METADATA][ZENODO_METATDATA_DESC] = doi_description
        data[ZENODO_METADATA][ZENODO_METADATA_CREATORS] = list()

        # get author data from the citation file
        for author in yaml_file[CITATION_AUTHORS_TYPE]:
            author_data = dict()
            author_data[ZENODO_AUTHOR_NAME] = (
                author[CITATION_AUTHOR_SURNAME] + ", " +
                author[CITATION_AUTHOR_FIRST_NAME] + ", ")
            if AUTHOR_AFFILIATION in author:
                author_data[AUTHOR_AFFILIATION] = author[AUTHOR_AFFILIATION]
            if AUTHOR_ORCID in author:
                author_data[AUTHOR_ORCID] = author[AUTHOR_ORCID]
            data[ZENODO_METADATA][ZENODO_METADATA_CREATORS].append(author_data)
        return data

    @staticmethod
    def convert_text_date_to_date(
            version_month, version_year, version_day):
        """ Convert the 3 components of a date into a CFF date

        :param version_month: version month, in text form
        :type version_month: text or int
        :param version_year: version year
        :type version_year: int
        :param version_day: version day of month
        :type version_day: int
        :return: the string representation for the cff file
        """
        return "{}-{}-{}".format(
            version_year,
            CitationUpdaterAndDoiGenerator.convert_month_name_to_number(
                version_month),
            version_day)

    @staticmethod
    def convert_month_name_to_number(version_month):
        """ Convert a python month in text form to a number form

        :param version_month: the text form of the month
        :type version_month: string or int
        :return: the month int value
        :rtype: int
        :raises: Exception when the month name is not recognised
        """
        if isinstance(version_month, int):
            return version_month
        elif isinstance(version_month, str):
            try:
                return int(version_month)
            except ValueError:
                try:
                    return strptime(version_month, "%B").tm_mon
                except ValueError:
                    try:
                        return strptime(version_month, "%b").tm_mon
                    except ValueError:  # pragma: no cover
                        raise Exception("Value {} not recognised as a month"
                                        .format(version_month))
        else:  # pragma: no cover
            raise Exception("Value {} not recognised as a month".format(
                version_month))
