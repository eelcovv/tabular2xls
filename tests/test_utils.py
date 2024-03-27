from pathlib import Path
import pandas as pd
import numpy as np
import pandas.testing as pt
import numpy.testing as nt

from tabular2xls.utils import get_super, replace_textsuper


def test_get_super():

    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"

    for normal_char, expected_super_char in zip(list(normal), list(super_s)):
        super_char = get_super(normal_char)
        assert super_char == expected_super_char


def test_replace_test_super():

    assert "This cell contains a superᵃ" == replace_textsuper(
        r"This cell contains a super\textsuperscript{a}"
    )
    assert "Also check thisˢᵘᵖᵉʳ" == replace_textsuper(
        r"Also check this\textsuperscript{super}"
    )
