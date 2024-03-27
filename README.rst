==========
tabularxls
==========


Convert a LaTeX tabular file to an xls file


Description
===========

With this tool you can convert LaTeX tabular files to Excel

------------
Installation
------------

Install the tool by::

    pip install tabular2xls

In case you want to include CBS color definitions, install with

    pip install tabular2xls[cbs]

or, alternatively, install the cbsplotlib package yourself::

    pip install cbsplotlib

-----
Usage
-----

Run the following command::

    tabular2xls tabular_file.tex

where the .tex file is a file containing a LaTeX tabular which is converted to an Excel file

---------
Full Help
---------

Get the full help by running::

    tabular2xls.exe --help

which  gives the following output::

    usage: tabular2xls [-h] [--version] [--output_filename OUTPUT_FILENAME] [--output_directory OUTPUT_DIRECTORY]
                       [--search_and_replace [SEARCH_AND_REPLACE ...]] [-v] [-vv] [--multi_index] [--encoding ENCODING]
                       FILENAME

    Tool to convert latex tabulars into xls files

    positional arguments:
      FILENAME              Tabular file name

    options:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --output_filename OUTPUT_FILENAME
                            Name of the xls output file. Must have extension .xlsx
      --output_directory OUTPUT_DIRECTORY
                            Name of the output directory. If not given, it is determined by the output file name
      --search_and_replace [SEARCH_AND_REPLACE ...]
                            Search en Replace patterns in case you want to change strings.By default, cdots en ast are
                            replaced by . and * vervangen, respectively
      -v, --verbose         set loglevel to INFO
      -vv, --debug          set loglevel to DEBUG
      --multi_index         Force a multiindex data frame
      --encoding ENCODING   Set the encoding of the text file. Default is utf-8

.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.0.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
