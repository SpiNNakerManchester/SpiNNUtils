
SpiNNUtils
==========
This provides basic utility functions and classes to other parts of SpiNNaker's
tooling. Nothing in here knows anything about SpiNNaker functionality.


`spinn_utilities.abstract_base`
-------------------------------
Provides a simplified (and faster) version of the standard Python Abstract
Base Class functionality.

`spinn_utilities.conf_loader`
-----------------------------
The structure to handle loading of SpiNNaker-style configuration files.

`spinn_utilities.executable_finder`
-----------------------------------
Utility for discovering executables to load onto SpiNNaker nodes.

`spinn_utilities.helpful_functions`
-----------------------------------
Miscellaneous bits.

`spinn_utilities.ordered_set`
-----------------------------
A set class where the elements have an order defined by when they were
inserted.

`spinn_utilities.overrides`
---------------------------
Decorator for declaring where a method overrides another method.

`spinn_utilities.progress_bar`
------------------------------
Generalised progress bar printer.

`spinn_utilities.socket_address`
--------------------------------
Holder for the locations of network resources.

`spinn_utilities.timer`
-----------------------
General code timer utility.

Generating Aggregated Citation Files
====================================
The `spinn_utilities.citation.citation_aggregator` module can be executed to generate a .cff file consisting of the Citation.cff file from the given top-level module, plus references made up from the dependencies of the top-level module.  If these dependencies have .cff files themselves, the references will contain the information from those files, otherwise it will use the version number and name of the module as a reference.  The tool can also create a DOI for the version of the tools in use which can then be cited.  This makes use of the Zenodo service.

To use the tool, run the following after installing SpiNNUtils:

```
python -m spinn_utilities.citation.citation_aggregator [-h] [--create_doi] [--publish_doi] [--doi_title DOI_TITLE] [--previous_doi PREVIOUS_DOI] [--zenodo_access_token ZENODO_ACCESS_TOKEN] output_path top_module

positional arguments:
  output_path           The file to store the result in
  top_module            The module to start with

optional arguments:
  -h, --help                                 show this help message and exit
  --create_doi                               Create a DOI from the resulting citation on Zenodo
  --publish_doi                              Publish the DOI created
  --doi_title DOI_TITLE                      The title to give the created DOI
  --previous_doi PREVIOUS_DOI                The DOI this is a newer version of
  --zenodo_access_token ZENODO_ACCESS_TOKEN  Access token for Zenodo
```

Documentation
=============
[SpiNNUtils python documentation](http://spinnutils.readthedocs.io)

[Combined python documentation](http://spinnakermanchester.readthedocs.io)
