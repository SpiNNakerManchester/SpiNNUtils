from __future__ import print_function
import argparse
import sys
import importlib
from .citation_updater_and_doi_generator import CitationUpdaterAndDoiGenerator
from .tool_citation_generation import CitationAggregator


def generate_aggregate(
        output_path, top_module, doi_title, zenodo_access_token, tools_doi,
        create_doi, publish_doi):
    """ Generates a single citation.cff from others

    :param output_path: Where to write the aggregate file
    :param top_module: the module to start aggregating the citation.cffs from
    :param doi_title: the title of the DOI
    :param zenodo_access_token: the access token for Zenodo
    :param tools_doi: the DOI of the tools
    :rtype: None
    """

    citation_aggregator = CitationAggregator()
    citation_aggregator.create_aggregated_citation_file(
        top_module, output_path)
    citation_updater_and_dio_generator = CitationUpdaterAndDoiGenerator()
    citation_updater_and_dio_generator.update_citation_file_and_create_doi(
        citation_file_path=output_path,
        update_version=False, version_number=None, version_month=None,
        version_year=None, version_day=None, doi_title=doi_title,
        create_doi=create_doi, publish_doi=publish_doi, previous_doi=tools_doi,
        is_previous_doi_sibling=True,
        zenodo_access_token=zenodo_access_token,
        module_path=output_path)


if __name__ == "__main__":
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
                        help="The DOI to attach the created DOI to")
    parser.add_argument("--zenodo_access_token",
                        help="Access token for Zenodo")

    args = parser.parse_args()
    error = False
    if args.create_doi:
        if not args.doi_title:
            print("--doi_title required when creating a DOI")
            error = True
        if not args.previous_doi:
            print("--previous_doi required when creating a DOI")
            error = True
        if not args.zenodo_access_token:
            print("--zenodo_access_token required when creating a DOI")
            error = True
    if args.publish_doi and not args.create_doi:
        print("Cannot publish DOI without creating one")
        error = True
    if error:
        parser.print_usage()
        sys.exit()

    top_module = importlib.import_module(args.top_module)

    generate_aggregate(
        parser.output_path, top_module, args.doi_title,
        args.zenodo_access_token, args.previous_doi, args.create_doi,
        args.publish_doi)
