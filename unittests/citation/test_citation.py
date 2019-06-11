from spinn_utilities.citation.citation_aggregator import generate_aggregate
import tempfile
import importlib
import os
import yaml


def test_generate_aggregate():
    output_path = tempfile.mktemp(".cff")
    top_module = importlib.import_module(
        "unittests.citation.package_1_folder.package_1")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + (
        os.path.dirname(__file__) + os.sep + "c_module")
    generate_aggregate(
        output_path, top_module, doi_title=None, zenodo_access_token=None,
        tools_doi=None, create_doi=False, publish_doi=False)
    assert os.path.isfile(output_path)
    with open(output_path, 'r') as stream:
        aggregate = yaml.safe_load(stream)

    authors = aggregate["authors"]
    references = aggregate["references"]
    assert len(authors) == 1
    assert authors[0]["email"] == "me@me.com"
    assert len(references) == 2
    assert len(references[0]["authors"]) == 1
    assert len(references[1]["authors"]) == 1
    assert references[0]["authors"][0]["email"] == "me_2@me.com"
    assert references[1]["authors"][0]["email"] == "me_c@me.com"
