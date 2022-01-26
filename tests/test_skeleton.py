import pytest
import pandas as pd

from tabular2xls.tabular_convert_tool import parse_tabular

__author__ = "EVLT"
__copyright__ = "EVLT"
__license__ = "MIT"


def test_tabular_1():
    """API Tests"""
    pass
    tabular_df = parse_tabular(input_filename='tabular_1.tex')

    assert  1 == 2


