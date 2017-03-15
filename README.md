[![Build Status](https://travis-ci.org/SpiNNakerManchester/SpiNNUtils.svg?branch=master)](https://travis-ci.org/SpiNNakerManchester/SpiNNUtils)

SpiNNUtils
==========
This provides basic utility functions and classes to other parts of SpiNNaker's
tooling. Nothing in here knows anything about SpiNNaker functionality.


Documentation
=============
[SpiNNUtils python documentation](http://spinnutils.readthedocs.io)

[Combined python documentation](http://spinnakermanchester.readthedocs.io)
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
