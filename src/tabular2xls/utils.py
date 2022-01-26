import logging
import re
import pandas as pd

_logger = logging.getLogger(__name__)


# function to convert to superscript
def get_super(x):
    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)


def replace_textsuper(cell):
    if match := re.search("\\\\textsuperscript{(.*?)}", cell):
        content = match.group(1)
        content = clean_the_cells([content])[0]
        content = get_super(content)
        new_cell = re.sub("\\\\textsuperscript{(.*?)}", content, cell)
    else:
        new_cell = cell
    return new_cell


def get_multicolumns(clean_cell):
    if match := re.search("\\\\multicolumn{(.*?)}", clean_cell):
        n_col = int(match.group(1))
        new_match = re.sub("\\\\multicolumn{(.*?)}", "", clean_cell)
        cell_format, first_cell = get_new_command(new_match)
    else:
        first_cell = clean_cell
        n_col = None
    return first_cell, n_col


def get_new_command(line):
    parse_alias = True
    alias = list()
    pattern = list()
    curl_level = 0
    for char in list(line):
        if char == "{":
            curl_level += 1
        elif char == "}":
            curl_level -= 1

        if curl_level > 0:
            if parse_alias:
                alias.append(char)
            else:
                pattern.append(char)
        else:
            if alias:
                parse_alias = False

    alias = "".join(alias)
    pattern = "".join(pattern)

    clean_patterns = clean_the_cells([alias, pattern])

    return clean_patterns


def clean_the_cells(cells, aliases=None):
    """ remove all spurious latex code from cell contents """
    clean_cells = list()
    for cell in cells:

        clean_cell = replace_textsuper(cell)
        clean_cell, n_col = get_multicolumns(clean_cell)
        clean_cell = clean_cell.replace("\\rowcolor{white}", "")
        clean_cell = clean_cell.replace("\\cornercell{", "")
        clean_cell = clean_cell.replace("\\normalsize{", "")
        clean_cell = clean_cell.replace("\\textbf{", "")
        clean_cell = clean_cell.replace("\\emph{", "")
        clean_cell = clean_cell.replace("\\python{", "")
        clean_cell = clean_cell.replace("}", "")
        clean_cell = clean_cell.replace("{", "")
        clean_cell = clean_cell.replace("\\", "")
        clean_cell = clean_cell.replace("--", "-")

        if aliases is not None:
            for alias, pattern in aliases.items():
                if match := re.match(alias, clean_cell):
                    clean_cell = clean_cell.replace(alias, pattern)

        clean_cells.append(clean_cell.strip())
    return clean_cells


def parse_tabular(input_filename):
    """
    read the tabular file and convert contents to a data frame

    Parameters
    ----------
    input_filename: str or Path
        Name of the tex tabular file

    Returns
    -------
    tabular_df: pd.DataFrame
        Dataframe of the tabular
    """

    with open(input_filename, "r") as fp:
        lines = fp.readlines()
    rows = list()
    header_row = None

    aliases = dict()

    for line in lines:
        clean_line = line.strip()
        match = re.search("caption{(.*)}", clean_line)
        if match is not None:
            caption = match.group(1)
            _logger.debug(f"CAPTION : {caption}")

        match = re.search("newcommand", clean_line)
        if match is not None:
            alias, pattern = get_new_command(clean_line)
            aliases[alias] = pattern
            _logger.debug(f"alias {alias} -> {pattern}")

        cells = clean_line.split("&")
        if len(cells) > 1:
            clean_cells = clean_the_cells(cells, aliases)
            if header_row is None:
                header_row = clean_cells
            else:
                rows.append(clean_cells)
            _logger.debug(f"INSIDE : {clean_line}")
        else:
            _logger.debug(f"OUTSIZE : {clean_line}")

    first_col = header_row[0]
    table_df = pd.DataFrame.from_records(rows, columns=header_row)
    table_df.set_index(first_col, drop=True, inplace=True)

    for alias, pattern in aliases.items():
        for col_name in table_df.columns:
            try:
                alias_exact = "^" + alias + "$"
                table_df[col_name] = table_df[col_name].str.replace(alias_exact, pattern)
            except AttributeError:
                pass

    return table_df
