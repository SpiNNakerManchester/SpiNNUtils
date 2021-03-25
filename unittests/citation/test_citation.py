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

from spinn_utilities.citation.citation_aggregator import generate_aggregate
import tempfile
import os
import yaml
import httpretty
from spinn_utilities.citation.citation_updater_and_doi_generator import (
    _Zenodo as Zenodo)


def test_generate_aggregate():
    with open("module.zip", "w") as f:
        f.write("test")
    deposit_id = 56789
    httpretty.register_uri(
        httpretty.GET, Zenodo._DEPOSIT_GET_URL,
        status=Zenodo._VALID_STATUS_REQUEST_GET)
    httpretty.register_uri(
        httpretty.POST, Zenodo._DEPOSIT_GET_URL,
        status=Zenodo._VALID_STATUS_REQUEST_POST,
        body=('{{"id": "{}", "metadata": {{'
              '"prereserve_doi": {{"doi": "12345"}}}}}}'.format(deposit_id)))
    httpretty.register_uri(
        httpretty.POST, Zenodo._DEPOSIT_PUT_URL.format(deposit_id),
        status=Zenodo._VALID_STATUS_REQUEST_POST)
    httpretty.register_uri(
        httpretty.POST, Zenodo._PUBLISH_URL.format(deposit_id),
        status=Zenodo._VALID_STATUS_REQUEST_PUBLISH)
    output_path = tempfile.mktemp(".cff")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + (
        os.path.dirname(__file__) + os.sep + "c_module")
    arguments = [output_path, "unittests.citation.package_1_folder.package_1",
                 "--create_doi", "--doi_title", "Test",
                 "--previous_doi", "25746", "--zenodo_access_token", "Test",
                 "--publish_doi"]
    httpretty.enable()
    generate_aggregate(arguments)
    httpretty.disable()
    assert os.path.isfile(output_path)
    with open(output_path, 'r') as stream:
        aggregate = yaml.safe_load(stream)

    authors = aggregate["authors"]
    references = aggregate["references"]
    assert len(authors) == 1
    assert authors[0]["email"] == "me@me.com"
    assert len(references) == 6
    assert len(references[0]["authors"]) == 1
    assert not references[1].get("authors")
    assert not references[2].get("authors")
    assert not references[3].get("authors")
    assert not references[4].get("authors")
    assert len(references[5]["authors"]) == 1
    assert references[0]["authors"][0]["email"] == "me_2@me.com"
    assert references[5]["authors"][0]["email"] == "me_c@me.com"
    assert references[1]["date-released"] == "2019-6-1"
    assert references[2]["date-released"] == "2019-6-1"
    assert references[3]["date-released"] == "2019-6-1"
    assert references[1]["version"] == "Test"
    assert references[2]["version"] == "Test"
    assert references[3]["version"] == "Test"
