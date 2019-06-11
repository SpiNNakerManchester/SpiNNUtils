from spinn_utilities.citation.citation_aggregator import generate_aggregate
import tempfile
import os
import yaml
import httpretty
from spinn_utilities.citation.citation_updater_and_doi_generator import (
    ZENODO_DEPOSIT_GET_URL, ZENODO_VALID_STATUS_REQUEST_GET,
    ZENODO_VALID_STATUS_REQUEST_POST, ZENODO_PUBLISH_URL,
    ZENODO_VALID_STATUS_REQUEST_PUBLISH, ZENODO_DEPOSIT_PUT_URL)


def test_generate_aggregate():
    with open("module.zip", "w") as f:
        f.write("test")
    deposit_id = 56789
    httpretty.register_uri(
        httpretty.GET, ZENODO_DEPOSIT_GET_URL,
        status=ZENODO_VALID_STATUS_REQUEST_GET)
    httpretty.register_uri(
        httpretty.POST, ZENODO_DEPOSIT_GET_URL,
        status=ZENODO_VALID_STATUS_REQUEST_POST,
        body=('{{"id": "{}", "metadata": {{'
              '"prereserve_doi": {{"doi": "12345"}}}}}}'.format(deposit_id)))
    httpretty.register_uri(
        httpretty.POST, ZENODO_DEPOSIT_PUT_URL.format(deposit_id),
        status=ZENODO_VALID_STATUS_REQUEST_POST)
    httpretty.register_uri(
        httpretty.POST, ZENODO_PUBLISH_URL.format(deposit_id),
        status=ZENODO_VALID_STATUS_REQUEST_PUBLISH)
    output_path = tempfile.mktemp(".cff")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + (
        os.path.dirname(__file__) + os.sep + "c_module")
    arguments = [output_path, "unittests.citation.package_1_folder.package_1",
                 "--create_doi", "--doi_title", "Test",
                 "--previous_doi", "25746", "--zenodo_access_token", "Test",
                 "--publish_doi"]
    httpretty.enable()
    generate_aggregate(arguments)
    assert os.path.isfile(output_path)
    with open(output_path, 'r') as stream:
        aggregate = yaml.safe_load(stream)

    authors = aggregate["authors"]
    references = aggregate["references"]
    assert len(authors) == 1
    assert authors[0]["email"] == "me@me.com"
    assert len(references) == 3
    assert len(references[0]["authors"]) == 1
    assert not references[1].get("authors")
    assert len(references[2]["authors"]) == 1
    assert references[0]["authors"][0]["email"] == "me_2@me.com"
    assert references[2]["authors"][0]["email"] == "me_c@me.com"
