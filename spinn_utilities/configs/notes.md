 # <a name="notes"></a> Notes for Developers
<!-- Copied from spinn_utilities/configs/notes.md -->
This section is aimed at developers writing code that uses cfg settings or adding new ones
* cfg rules
  * Section names are case-sensitive with the recommend format being a single Capitalized word.
  * Option names for users are not case or underscore sensitive. 
  * In code all options names must be exact matches (case and underscores). 
      The recommended format is all lower with words seperated by underscore.
  * Any cfg option used must be declared in the default files
  * All cfg options declared must be used
  * All cfg options must only be declared in one default file
  * All cfg options keys should be unique even between sections and not be section names.
    * Section "Mode" and option "mode" are a handled exception. 
* Special @ options
  * @: Adds documentation for this section
  * @(option): Adds documentation for this option
  * @group_(source_option) = target_option: The key and value of the source_option 
    will be grouped with the target_option. This can be N - N,
    but transative is not supported. 

* Start of option keys with special meanings.
    (t)path ones will be removed and auto grouped with the matching one.
    If and only if the part after the first underscore is an exact match.
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
  * Use \</br> at the end of a line (or leave a blank line) if a new line is needed.
  * Use \t* to add a sub bullet. (Will replace \t(s) with spaces)
  * Use \t (without the *) for a real none bullet indent. (Will replace \t with \&nbsp;\&nbsp;)
  * Supports md links in the \[Title\]\(Link\) format. 
      * Link can be any cfg option key except those tagged with @group.
      * The # reguired by markdown will be added if needed.
      * Where keys are auto grouped any of these can be used.
      * Link can be an external url.

