"""
tool om latex tabular files in xls om te zetten
"""

import argparse
import logging
import sys
from pathlib import Path

from tabular2xls import __version__
from tabular2xls.utils import parse_tabular

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
    parser.add_argument("filename", help="Tabular file name", metavar="STR")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--debug",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
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

    if args.output_directory is None:
        out_dir = filename.parent
    else:
        out_dir = Path(args.output_directory)

    if args.xls_filename is None:
        xls_filename = filename.with_suffix(".xlsx").stem
    else:
        xls_filename = Path(args.xls_filename)

    if ".xlsx" not in xls_filename.suffix:
        raise ValueError("Output filename does not have .xlsx extension. Please correct")

    tabular_df = parse_tabular(input_filename=filename)

    table_file = out_dir / xls_filename
    table_file.parent.mkdir(exist_ok=True, parents=True)
    _logger.info(f"Writing to {table_file}")
    tabular_df.to_excel(table_file)


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
