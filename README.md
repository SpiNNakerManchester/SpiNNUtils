
SpiNNUtils
==========
This provides basic utility functions and classes to other parts of SpiNNaker's
tooling. Nothing in here knows anything about SpiNNaker functionality.

Release Info
============
This release was tested with the following python versions installed.

- appdirs==1.4.4
- astroid==2.15.8
- attrs==23.1.0
- certifi==2023.7.22
- charset-normalizer==3.3.0
- contourpy==1.1.1
- coverage==7.3.1
- csa==0.1.12
- cycler==0.12.0
- dill==0.3.7
- ebrains-drive==0.5.1
- exceptiongroup==1.1.3
- execnet==2.0.2
- fonttools==4.43.0
- graphviz==0.20.1
- httpretty==1.1.4
- idna==3.4
- importlib-resources==6.1.0
- iniconfig==2.0.0
- isort==5.12.0
- jsonschema==4.19.1
- jsonschema-specifications==2023.7.1
- kiwisolver==1.4.5
- lazy-object-proxy==1.9.0
- lazyarray==0.5.2
- matplotlib==3.7.3
- mccabe==0.7.0
- mock==5.1.0
- MorphIO==6.6.8
- multiprocess==0.70.15
- neo==0.12.0
- numpy==1.24.4
- opencv-python==4.8.1.78
- packaging==23.2
- pathos==0.3.1
- Pillow==10.0.1
- pkgutil_resolve_name==1.3.10
- platformdirs==3.10.0
- pluggy==1.3.0
- pox==0.3.3
- ppft==1.7.6.7
- py==1.11.0
- pylint==2.17.7
- PyNN==0.12.1
- pyparsing==2.4.7
- pytest==7.4.2
- pytest-cov==4.1.0
- pytest-forked==1.6.0
- pytest-instafail==0.5.0
- pytest-progress==1.2.5
- pytest-timeout==2.1.0
- pytest-xdist==3.3.1
- python-coveralls==2.9.3
- python-dateutil==2.8.2
- PyYAML==6.0.1
- quantities==0.14.1
- referencing==0.30.2
- requests==2.31.0
- rpds-py==0.10.3
- scipy==1.10.1
- six==1.16.0
- spalloc==1!7.1.0
- SpiNNaker-PACMAN==1!7.1.0
- SpiNNakerGraphFrontEnd==1!7.1.0
- SpiNNakerTestBase==1!7.1.0
- SpiNNFrontEndCommon==1!7.1.0
- SpiNNMachine==1!7.1.0
- SpiNNMan==1!7.1.0
- SpiNNUtilities==1!7.1.0
- sPyNNaker==1!7.1.0
- testfixtures==7.2.0
- tomli==2.0.1
- tomlkit==0.12.1
- typing_extensions==4.8.0
- urllib3==2.0.5
- websocket-client==1.6.3
- wrapt==1.15.0
- zipp==3.17.0


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
[SpiNNUtils python documentation](http://spinnutils.readthedocs.io/en/7.1.0)

[Combined python documentation](http://spinnakermanchester.readthedocs.io/en/7.1.0)
