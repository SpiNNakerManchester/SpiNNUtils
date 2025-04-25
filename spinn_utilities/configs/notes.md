 # <a name="notes"></a> Notes for Developers
<!-- Copied from spinn_utilities/configs/notes.md -->
This section is aimed at developers writing code that uses cfg settings or adding new ones
* cfg rules
  * In code all options names must be exact matches (case and underscores)
  * Any cfg option used must be declared in the default files
  * All cfg options declared must be used
  * All cfg options must only be declared in one default file
  * All cfg options keys should be unique even between sections and not be section names.
    * "mode" is a handled exception.
* Documentation options
  * @: Adds documentation for this section
  * @(option): Adds documentation for this option
  * @group_(another_option): Groups this option with the other one. Can also be used to group under a different title.

* Start of option keys with special meanings. Will always be removed and auto grouped.
  * draw_: Flag to say file(s) should be created
  * keep_: Flag to say if files should be kept at the end of the run. These ffiles may still be created.
  * path_: Path to a file to be placed in the run folder
  * run_: Flag to say something should run which may create files
  * tpath_: Path to a file to be placed in the timestamp folder
  * write_: Flag to say file/report should be written

* Notes on cfg documentation.
  * Should be designed for an md file.
  * Can be multline. Just indent from the key.
  * Indent is stripped out.
  * Newlines are kept but remember are often ignored in md files
  * Use \n at the end of a line if a new line is really wanted. (Adds 2 spaces)
  * Use \t* to add a sub bullet. (Will replace \t(s) with spaces)
  * Use \t (without the *) for a real none bullet indent. (Will replace \t with \&nbsp;\&nbsp;)
  * Supports md links in the \[Title\]\(Link\) format. 
      Link can be any cfg option key except those tagged with @group.
      Link can be an external url.

