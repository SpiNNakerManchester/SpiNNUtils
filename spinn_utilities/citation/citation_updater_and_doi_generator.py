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

import yaml
import io
import requests
import zipfile
import unicodedata
import os
from time import strptime
from typing import Any, cast, Dict, List, Optional, Tuple, Union

from spinn_utilities.typing.json import JsonObject

CITATION_FILE_VERSION_FIELD = "version"
CITATION_FILE_DATE_FIELD = "date-released"
CITATION_AUTHORS_TYPE = "authors"
CITATION_AUTHOR_FIRST_NAME = "given-names"
CITATION_AUTHOR_SURNAME = "family-names"
CITATION_FILE_DESCRIPTION = "title"

ZENODO_RELATION_FIELD = "relation"
ZENODO_NEWER_VERSION_OF = 'isNewVersionOf'
ZENODO_SIBLING_OF = "cites"
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

# pylint: skip-file


class _ZenodoException(Exception):
    """
    Exception from a call to Zenodo.
    """

    def __init__(
            self, operation: str, expected: int, request: requests.Response):
        super().__init__(
            "don't know what went wrong. got wrong status code when trying "
            f"to {operation}. Got error code {request.status_code} "
            f"(when expecting {expected}) "
            f"with response content {request.content!r}")
        self.request = request
        self.expected = expected


class _Zenodo(object):
    """
    Manages low level access to Zenodo.
    """

    # pragma: no cover
    __slots__ = ("__zenodo_token", )

    _BASE_URI = "https://zenodo.org/api"
    _DEPOSIT_GET_URL = _BASE_URI + "/deposit/depositions"
    _DEPOSIT_PUT_URL = _BASE_URI + "/deposit/depositions/{}/files"
    _PUBLISH_URL = _BASE_URI + "/deposit/depositions/{}/actions/publish"
    _CONTENT_TYPE = "Content-Type"
    _JSON = "application/json"
    _ACCESS_TOKEN = 'access_token'
    _RELATED_IDENTIFIERS = 'related_identifiers'
    _VALID_STATUS_REQUEST_GET = 200
    _VALID_STATUS_REQUEST_POST = 201
    _VALID_STATUS_REQUEST_PUBLISH = 202

    def __init__(self, token: str):
        self.__zenodo_token = token

    @staticmethod
    def _json(r: requests.Response) -> Optional[JsonObject]:
        try:
            return r.json()
        except Exception:  # pylint: disable=broad-except
            return None

    def get_verify(
            self, related: List[Dict[str, str]]) -> Optional[JsonObject]:
        r = requests.get(
            self._DEPOSIT_GET_URL, timeout=10,
            params={self._ACCESS_TOKEN: self.__zenodo_token,
                    self._RELATED_IDENTIFIERS: str(related)},
            json={}, headers={self._CONTENT_TYPE: self._JSON})
        if r.status_code != self._VALID_STATUS_REQUEST_GET:
            raise _ZenodoException(
                "request a DOI", self._VALID_STATUS_REQUEST_GET, r)
        return self._json(r)

    def post_create(
            self, related: List[Dict[str, str]]) -> Optional[JsonObject]:
        r = requests.post(
            self._DEPOSIT_GET_URL, timeout=10,
            params={self._ACCESS_TOKEN: self.__zenodo_token,
                    self._RELATED_IDENTIFIERS: str(related)},
            json={}, headers={self._CONTENT_TYPE: self._JSON})
        if r.status_code != self._VALID_STATUS_REQUEST_POST:
            raise _ZenodoException(
                "get an empty upload", self._VALID_STATUS_REQUEST_POST, r)
        return self._json(r)

    def post_upload(
            self, deposit_id: str, data: Dict[str, Any],
            files: Dict[str, io.BufferedReader]) -> Optional[JsonObject]:
        r = requests.post(
            self._DEPOSIT_PUT_URL.format(deposit_id), timeout=10,
            params={self._ACCESS_TOKEN: self.__zenodo_token},
            data=data, files=files)
        if r.status_code != self._VALID_STATUS_REQUEST_POST:
            raise _ZenodoException(
                "to put files and data into the preallocated DOI",
                self._VALID_STATUS_REQUEST_POST, r)
        return self._json(r)

    def post_publish(self, deposit_id: str) -> Optional[JsonObject]:
        r = requests.post(
            self._PUBLISH_URL.format(deposit_id), timeout=10,
            params={self._ACCESS_TOKEN: self.__zenodo_token})
        if r.status_code != self._VALID_STATUS_REQUEST_PUBLISH:
            raise _ZenodoException(
                "publish the DOI", self._VALID_STATUS_REQUEST_PUBLISH, r)
        return self._json(r)


class CitationUpdaterAndDoiGenerator(object):
    def __init__(self) -> None:
        self.__zenodo: Optional[_Zenodo] = None

    def update_citation_file_and_create_doi(
            self, citation_file_path: str, doi_title: str, create_doi: bool,
            publish_doi: bool, previous_doi: str, zenodo_access_token: str,
            module_path: str) -> None:
        """
        Take a CITATION.cff file and updates the version and
        date-released fields, and rewrites the ``CITATION.cff`` file.

        :param citation_file_path: File path to the ``CITATION.cff`` file
        :param create_doi:
            Whether to use Zenodo DOI interface to grab a DOI
        :param zenodo_access_token: Access token for Zenodo
        :param publish_doi: Whether to publish the DOI on Zenodo
        :param previous_doi: DOI to append the created DOI to
        :param doi_title: Title for the created DOI
        :param module_path: Path to the module to zip up
        :param update_version:
            Whether we should update the citation version
        """
        self.__zenodo = _Zenodo(zenodo_access_token)

        # data holders
        deposit_id: Optional[str] = None

        # read in YAML file
        with open(citation_file_path, 'r', encoding="utf-8") as stream:
            yaml_file = yaml.safe_load(stream)

        # if creating a DOI, go and request one
        if create_doi:
            doi_id, deposit_id = self._request_doi(previous_doi)
            yaml_file[IDENTIFIER] = doi_id

        # rewrite citation file with updated fields
        with io.open(citation_file_path, 'w', encoding='utf8') as outfile:
            yaml.dump(yaml_file, outfile, default_flow_style=False,
                      allow_unicode=True)

        # if creating a DOI, finish the request and possibly publish it
        if create_doi:
            assert deposit_id is not None
            self._finish_doi(
                deposit_id, publish_doi, doi_title,
                yaml_file[CITATION_FILE_DESCRIPTION], yaml_file, module_path)

    def _request_doi(self, previous_doi: str) -> Tuple[bytes, Any]:
        """
        Go to Zenodo and requests a DOI.

        :param previous_doi: the previous DOI for this module, if exists
        :return: the DOI id, and deposit id
        """
        # create link to previous version (if applicable)
        related = list()
        related.append({
            ZENODO_RELATION_FIELD: ZENODO_NEWER_VERSION_OF,
            IDENTIFIER: previous_doi})

        # get a request for a DOI
        assert self.__zenodo is not None
        self.__zenodo.get_verify(related)

        # get empty upload
        request_data = self.__zenodo.post_create(related)
        assert request_data is not None

        # get DOI and deposit id
        metadata = cast(Dict[str, Dict[str, str]],
                        request_data[ZENODO_METADATA])
        doi_id = unicodedata.normalize(
            'NFKD',
            (metadata[ZENODO_PRE_RESERVED_DOI]
             [ZENODO_DOI_VALUE])).encode('ascii', 'ignore')
        deposition_id = request_data[ZENODO_DEPOSIT_ID]

        return doi_id, deposition_id

    def _finish_doi(
            self, deposit_id: str, publish_doi: bool, title: str,
            doi_description: str, yaml_file: Dict[str, Any],
            module_path: str) -> None:
        """
        Finishes the DOI on Zenodo.

        :param deposit_id: the deposit id to publish
        :param publish_doi: whether we should publish the DOI
        :param title: the title of this DOI
        :param doi_description: the description for the DOI
        :param yaml_file: the citation file after its been read it
        :param module_path: the path to the module to DOI
        """
        zipped_file = None
        assert self.__zenodo is not None
        try:
            zipped_file = self._zip_up_module(module_path)
            with open(zipped_file, "rb") as zipped_open_file:
                files = {ZENODO_FILE: zipped_open_file}
                data = self._fill_in_data(title, doi_description, yaml_file)
                self.__zenodo.post_upload(deposit_id, data, files)
        finally:
            if zipped_file:
                os.remove(zipped_file)

        # publish DOI
        if publish_doi:
            self.__zenodo.post_publish(deposit_id)

    def _zip_up_module(self, module_path: str) -> str:
        """
        Zip up a module.

        :param module_path: the path to the module to zip up
        :return: the filename to the zip file
        """
        if os.path.isfile('module.zip'):
            os.remove('module.zip')

        avoids = [".git", ".gitignore", ".gitattributes", ".travis.yml",
                  ".github", "model_binaries", "common_model_binaries",
                  ".coveragerc", ".idea"]

        with zipfile.ZipFile(
                'module.zip', 'w', zipfile.ZIP_DEFLATED) as module_zip_file:
            self._zip_walker(module_path, avoids, module_zip_file)
        return 'module.zip'

    @staticmethod
    def _zip_walker(module_path: str, avoids: List[str],
                    module_zip_file: zipfile.ZipFile) -> None:
        """
        Traverse the module and its sub-directories and only adds to the
        files to the zip which are not within a avoid directory that.

        :param module_path: the path to start the search at
        :param avoids: the set of avoids to avoid
        :param module_zip_file: the zip file to put into
        """
        for directory_path, _, files in os.walk(module_path):
            for directory_name in directory_path.split(os.sep):
                if directory_name in avoids:
                    break
            else:
                for potential_zip_file in files:
                    # if safe to zip, zip
                    if potential_zip_file not in avoids:
                        module_zip_file.write(
                            os.path.join(directory_path, potential_zip_file))

    @staticmethod
    def _fill_in_data(doi_title: str, doi_description: str,
                      yaml_file: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add in data to the Zenodo metadata.

        :param doi_title: the title of the DOI
        :param doi_description: the description of the DOI
        :param yaml_file: the citation file once read into the system
        :return: dict containing Zenodo metadata
        """
        # add basic meta data
        metadata: Dict[str, Any] = {
            ZENODO_METADATA_TITLE: doi_title,
            ZENODO_METATDATA_DESC: doi_description,
            ZENODO_METADATA_CREATORS: []
        }

        # get author data from the citation file
        for author in yaml_file[CITATION_AUTHORS_TYPE]:
            author_data = {
                ZENODO_AUTHOR_NAME: (
                    author[CITATION_AUTHOR_SURNAME] + ", " +
                    author[CITATION_AUTHOR_FIRST_NAME])
            }
            if AUTHOR_AFFILIATION in author:
                author_data[AUTHOR_AFFILIATION] = author[AUTHOR_AFFILIATION]
            if AUTHOR_ORCID in author:
                author_data[AUTHOR_ORCID] = author[AUTHOR_ORCID]
            metadata[ZENODO_METADATA_CREATORS].append(author_data)
        return {ZENODO_METADATA: metadata}

    @staticmethod
    def convert_text_date_to_date(
            version_month: Union[int, str], version_year: Union[int, str],
            version_day: Union[int, str]) -> str:
        """
        Convert the 3 components of a date into a CFF date.

        :param version_month: version month, in text form
        :param version_year: version year
        :param version_day: version day of month
        :return: the string representation for the CFF file
        """
        return "{}-{}-{}".format(
            version_year,
            CitationUpdaterAndDoiGenerator.convert_month_name_to_number(
                version_month),
            version_day)

    @staticmethod
    def convert_month_name_to_number(version_month: Union[int, str]) -> int:
        """
        Convert a python month in text form to a number form.

        :param version_month: the text form of the month
        :return: the month int value
        :raises ValueError: when the month name is not recognised
        """
        if isinstance(version_month, int):
            return version_month
        elif isinstance(version_month, str):
            try:
                return int(version_month)
            except ValueError as original:
                try:
                    return strptime(version_month, "%B").tm_mon
                except ValueError:
                    try:
                        return strptime(version_month, "%b").tm_mon
                    except ValueError:  # pragma: no cover
                        raise ValueError(
                            f"Value {version_month} not recognised"
                            " as a month") from original
        else:  # pragma: no cover
            raise ValueError(
                f"Value {version_month} not recognised as a month")
