"""
tool om latex tabular files in xls om te zetten
"""

import argparse
import logging
import sys
from pathlib import Path

from tabular2xls import __version__
from tabular2xls.utils import parse_tabular, write_data_to_sheet_multiindex

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(description="Tool om latex tabulars in xls files om te zetten")
    parser.add_argument(
        "--version",
        action="version",
        version="tabular2xls {ver}".format(ver=__version__),
    )
    parser.add_argument("filename", help="Tabular file name", metavar="FILENAME")
    parser.add_argument("--output_filename",
                        help="Naam van de xls output file. Moet extensie .xlsx "
                             "hebben", metavar="OUTPUT_FILENAME")
    parser.add_argument("--output_directory",
                        help="Naam van de output directory. Als niet gegeven wordt het"
                             "door de output filenaam bepaald", metavar="OUTPUT_DIRECTORY")
    parser.add_argument("--search_and_replace",
                        help="Search en Replace patterns als je nog string wilt veranderen."
                             "Default worden cdots en ast naar resp . en * vervangen",
                        nargs="*", action="append")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
        default=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--debug",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    parser.add_argument(
        "--multi_index",
        help="Forceer een multiindex dataframe",
        action="store_true",
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat='%(asctime)s %(filename)25s[%(lineno)4s] - %(levelname)-8s : %(message)s'
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


def main(args):
    """Wrapper allowing :func:`fib` to be called with string arguments in a CLI fashion

    Instead of returning the value from :func:`fib`, it prints the result to the
    ``stdout`` in a nicely formated message.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--verbose", "42"]``).
    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    filename = Path(args.filename)

    search_and_replace = {
        r"\$cdot\$": ".",
        r"\$ast\$": "*",
    }
    if args.search_and_replace is not None:
        for k, v in args.search_and_replace.items():
            search_and_replace[k] = v

    if args.output_filename is None:
        xls_filename = filename.with_suffix(".xlsx")
    else:
        xls_filename = Path(args.output_filename)

    if args.output_directory is not None:
        output_directory = Path(args.output_directory)
        xls_file_base = xls_filename.stem + xls_filename.suffix
        xls_filename = output_directory / Path(xls_file_base)

    if ".xlsx" not in xls_filename.suffix:
        raise ValueError("Output filename does not have .xlsx extension. Please correct")

    _logger.info(f"Converting {filename} ->> {xls_filename}")
    tabular_df = parse_tabular(input_filename=filename, multi_index=args.multi_index,
                               search_and_replace=search_and_replace)

    xls_filename.parent.mkdir(exist_ok=True, parents=True)
    _logger.debug(f"Writing to {xls_filename}")
    write_data_to_sheet_multiindex(tabular_df, xls_filename)
    _logger.info(f"Done!")


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
