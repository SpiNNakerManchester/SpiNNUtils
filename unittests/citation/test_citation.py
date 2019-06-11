from spinn_utilities.citation.citation_aggregator import generate_aggregate
import tempfile
import os
import yaml


def test_generate_aggregate():
    output_path = tempfile.mktemp(".cff")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + (
        os.path.dirname(__file__) + os.sep + "c_module")
    arguments = [output_path, "unittests.citation.package_1_folder.package_1"]
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
