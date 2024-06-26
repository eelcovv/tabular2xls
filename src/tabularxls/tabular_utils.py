# -*- coding: utf-8 -*-
"""
Helper functions and classes for working with tabular data
"""
import logging
import re
import pandas as pd
from pandas import DataFrame
from pandas.io.formats.excel import ExcelFormatter
import matplotlib.colors as mlc
from pathlib import Path
from typing import Union

try:
    import cbsplotlib
except ImportError:
    cbsplotlib = None
else:
    import cbsplotlib.colors as cbc

_logger = logging.getLogger(__name__)


def get_color_names(min_color_length=2):
    """
    Get the color name definitions obtained from the matplot default list

    Args:
        min_color_length (int):  minimum length of the color names

    Notes:
        * By default, all matlotlib colors are taken
        * In case cbsplotlib is installed, also all CBS color definitions are taken

    Returns:
        list: All the default color names
    """

    colors = [c.replace("xkcd:", "") for c in mlc.get_named_colors_mapping().keys()]
    if cbsplotlib is not None:
        cbs_colors = [c.replace("cbs:", "") for c in cbc.CBS_COLORS.keys()]
        colors.extend(cbs_colors)
    defaults_colors = [c for c in colors if len(c) > min_color_length]

    return defaults_colors


def get_color_code(color_name: str):
    """
    Get the code belonging to a color name

    Args:
        color_name (str):  Name of the color

    Returns:
        str: Color code
    """

    color_code = None

    if cbsplotlib is not None:
        # in case cbsplotlib is imported, first try to obtain the CBS color definition
        try:
            color_code = cbc.CBS_COLORS_HEX[color_name]
        except KeyError:
            try:
                color_code = cbc.CBS_COLORS_HEX["cbs:" + color_name]
            except KeyError:
                pass

    if color_code is None:
        # if no color code has been found yet, try to obtain it from the matplotlib color definitions
        try:
            color_code = mlc.get_named_colors_mapping()[color_name]
        except KeyError:
            _logger.info(f"Could find a value for the color name  '{color_name}'")

    return color_code


def get_super(content):
    """
    Convert normal characters to superscript codes

    Args:
        content (str): The string for which all characters need to be converted

    Returns:
        superscript_content (str): New string in only superscript characters
    """

    normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-=()"
    super_s = "ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶᴷᴸᴹᴺᴼᴾQᴿˢᵀᵁⱽᵂˣʸᶻᵃᵇᶜᵈᵉᶠᵍʰᶦʲᵏˡᵐⁿᵒᵖ۹ʳˢᵗᵘᵛʷˣʸᶻ⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾"
    translations = content.maketrans("".join(normal), "".join(super_s))
    superscript_content = content.translate(translations)
    return superscript_content


def replace_textsuper(cell):
    """
    Replace LaTeX textsuperscript characters with superscript characters

    Args:
        cell (str): Cell contents for which the textsuperscript needs to be translated into superscript

    Notes:
        * Superscript in LaTeX is given with the *\\textsuperscript{}* command

    Returns:
        new_cell (str): Cell contents with all superscript translated into superscript characters

    """
    if match := re.search("\\\\textsuperscript{(.*?)}", cell):
        content = match.group(1)
        content = clean_the_cells([content])[0]
        content = get_super(content)
        new_cell = re.sub("\\\\textsuperscript{(.*?)}", content, cell)
    else:
        new_cell = cell
    return new_cell


def get_multicolumns(clean_cell):
    """
    Get the cell contents of a multicolumn cell

    Args:
        clean_cell (str):  Cell contents of a multicolumn cell

    Returns:
        first_cell (str), n_col (int): The contents of the first cell and the number of following multicolumn cells
    """
    if match := re.search("\\\\multicolumn{(.*?)}", clean_cell):
        n_col = int(match.group(1))
        new_match = re.sub("\\\\multicolumn{(.*?)}", "", clean_cell)
        cell_format, first_cell = get_new_command(new_match)
    else:
        first_cell = clean_cell
        n_col = None
    return first_cell, n_col


def get_new_command(line):
    """
    Get the contents of a LaTeX newcommand definition

    Args:
        line (str):  Line potentially containing a newcommand definition

    Returns:

    """

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
    """
    Remove all spurious latex code from cell contents

    Args:
        cells (list): List of cells containing strings to be cleaned
        aliases (dict, optional): If aliases are passed (default None), all strings will be cleaned with the
            replacements defined in the aliases

    Returns:
        list: The new cell contents
    """

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
        clean_cell = clean_cell.replace("\\textemdash", "-")
        clean_cell = clean_cell.replace("\\textendash", "-")
        clean_cell = clean_cell.replace("\\numprint{", "")
        clean_cell = re.sub(r"\\hspace{.*?}", "", clean_cell)
        clean_cell = re.sub(r"\\vspace{.*?}", "", clean_cell)
        clean_cell = clean_cell.replace("}", "")
        clean_cell = clean_cell.replace("{", "")
        clean_cell = clean_cell.replace("\\", "")
        clean_cell = clean_cell.replace("--", "-")

        if aliases is not None:
            for alias, pattern in aliases.items():
                if match := re.match(alias, clean_cell):
                    clean_cell = clean_cell.replace(alias, pattern)

        clean_cells.append(clean_cell.strip())
        if n_col is not None and n_col > 1:
            for ii in range(1, n_col):
                clean_cells.append("")

    return clean_cells


def parse_tabular(
    input_filename: Union[str, Path],
    multi_index: bool = False,
    search_and_replace: Union[dict, None] = None,
    encoding: str = "utf-8",
    top_row_merge: bool = False
) -> DataFrame:
    """
    Read the tabular file and convert contents to a data frame

    Args:
        input_filename (str or Path): Name of the LaTeX tabular file.
        multi_index (bool, optional): Convert the index into a multi index based on the first 2 columns. Defaults to
            False.
        search_and_replace (dict, optional): The search and replace strings stored in a dictionary. Defaults to None.
        encoding (str, optional): Encoding of the input file. Defaults to "utf-8"
        top_row_merge (bool, optional). Merge the top rows in the rows are multirow headers

    Returns:
        DataFrame: The cleaned tubular data stored in a dataframe
    """

    _logger.debug(f"Reading file {input_filename}")
    with open(input_filename, encoding=encoding) as fp:
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

        # hyperref halen we weg
        # de pattern '\\hyperref[mijnref]{content cell}' vervangen we met 'content cell'
        clean_line = re.sub(r"\\hyperref\[.*\]{(.*)}", r"\1", clean_line)

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

    index_columns = header_row[0]
    empty_column_names = False
    if multi_index:
        if header_row[0] == "":
            header_row[0] = "l1"
        if header_row[1] == "":
            header_row[1] = "l2"
        table_df = pd.DataFrame.from_records(rows, columns=header_row)
        index_columns = ["l1", "l2"]
        empty_column_names = True
    else:
        table_df = pd.DataFrame.from_records(rows, columns=header_row)

    if top_row_merge:
        # De eerste rij beschouwen als een multi column. Fix dat
        table_df = table_df.T.reset_index()
        first_two_columns = table_df.columns[:2].to_list()
        table_df = table_df.set_index(first_two_columns)
        table_df.index = table_df.index.rename(["", ""])
        table_df = table_df.T
        first_single_col = table_df.columns[:1].to_list()
        name = first_single_col[0][1]
        table_df.set_index(first_single_col, drop=True, inplace=True)
        table_df.index = table_df.index.rename(name)
        top_name = table_df.columns[0][0]
        new_columns = ["/".join([top_name, mc[1]]) for mc in table_df.columns]
        table_df.columns = new_columns
    else:
        table_df.set_index(index_columns, drop=True, inplace=True)
        if empty_column_names:
            table_df.index = table_df.index.rename(["", ""])

    for alias, pattern in aliases.items():
        for col_name in table_df.columns:
            try:
                alias_exact = "^" + alias + "$"
                table_df[col_name] = table_df[col_name].str.replace(
                    alias_exact, pattern, regex=True
                )
            except AttributeError:
                pass

    if search_and_replace is not None:
        for search, replace in search_and_replace.items():
            table_df.replace(search, replace, regex=True, inplace=True)

    return table_df


class WorkBook:
    """
    This class is responsible for working with Excel data
    Args:
        workbook:  Excel workbook object to modify

    Attributes:
        left_align_italic (workbook format or None)
        left_align_italic_large (workbook format or None)
        left_align_italic_large_ul (workbook format or None) : setup for workbook
        left_align_helvetica (workbook format or None) : setup for workbook
        left_align_helvetica_bold (workbook format or None) : setup for workbook
        left_align_bold (workbook format or None) : setup for workbook
        left_align_bold_large (workbook format or None) : setup for workbook
        left_align_bold_larger (workbook format or None) : setup for workbook
        left_align (workbook format or None) : setup for workbook
        left_align_large_wrap (workbook format or None) : setup for workbook
        left_align_large_wrap_top (workbook format or None) : setup for workbook
        left_align_wrap (workbook format or None) : setup for workbook
        left_align_large (workbook format or None) : setup for workbook
        right_align (workbook format or None) : setup for workbook
        header_format (workbook format or None) : setup for workbook
        title_format (workbook format or None) : setup for workbook
        section_heading (workbook format or None) : setup for workbook
        footer_format (workbook format or None) : setup for workbook
    """

    def __init__(self, workbook):
        """
        Constructor of the Workbook class
        """

        self.workbook = workbook
        self.left_align_italic = None
        self.left_align_italic_large = None
        self.left_align_italic_large_ul = None
        self.left_align_helvetica = None
        self.left_align_helvetica_bold = None
        self.left_align_bold = None
        self.left_align_bold_large = None
        self.left_align_bold_larger = None
        self.left_align = None
        self.left_align_large_wrap = None
        self.left_align_large_wrap_top = None
        self.left_align_wrap = None
        self.left_align_large = None
        self.right_align = None
        self.header_format = None
        self.title_format = None
        self.section_heading = None
        self.footer_format = None
        self.add_styles()

    def add_styles(self):
        """
        Add all the styles to this workbook
        """
        self.left_align_helvetica = self.workbook.add_format(
            {"font": "helvetica", "align": "left", "font_size": 8, "border": 0}
        )
        self.left_align_helvetica_bold = self.workbook.add_format(
            {
                "font": "helvetica",
                "bold": True,
                "align": "left",
                "font_size": 8,
                "border": 0,
            }
        )
        self.left_align_italic = self.workbook.add_format(
            {
                "font": "arial",
                "italic": True,
                "align": "left",
                "font_size": 8,
                "border": 0,
            }
        )
        self.left_align_italic_large = self.workbook.add_format(
            {
                "font": "arial",
                "italic": True,
                "align": "left",
                "font_size": 10,
                "border": 0,
            }
        )
        self.left_align_italic_large_ul = self.workbook.add_format(
            {
                "font": "arial",
                "italic": True,
                "align": "left",
                "underline": True,
                "font_size": 10,
                "border": 0,
            }
        )
        self.left_align_bold = self.workbook.add_format(
            {
                "font": "arial",
                "bold": True,
                "align": "left",
                "font_size": 8,
                "border": 0,
            }
        )
        self.left_align_bold_large = self.workbook.add_format(
            {
                "font": "arial",
                "bold": True,
                "align": "left",
                "font_size": 10,
                "border": 0,
            }
        )
        self.left_align_bold_larger = self.workbook.add_format(
            {
                "font": "arial",
                "bold": True,
                "align": "left",
                "font_size": 12,
                "border": 0,
            }
        )
        self.left_align = self.workbook.add_format(
            {"font": "arial", "align": "left", "font_size": 8, "border": 0}
        )
        self.left_align_large_wrap = self.workbook.add_format(
            {
                "font": "arial",
                "align": "left",
                "text_wrap": True,
                "font_size": 10,
                "border": 0,
            }
        )
        self.left_align_large_wrap_top = self.workbook.add_format(
            {
                "font": "arial",
                "align": "left",
                "valign": "top",
                "text_wrap": True,
                "font_size": 10,
                "border": 0,
            }
        )
        self.left_align_large = self.workbook.add_format(
            {"font": "arial", "align": "left", "font_size": 10, "border": 0}
        )
        self.right_align = self.workbook.add_format(
            {"font": "arial", "align": "right", "font_size": 8, "border": 0}
        )
        self.header_format = self.workbook.add_format(
            {
                "font": "arial",
                "bold": True,
                "italic": True,
                "text_wrap": True,
                "align": "left",
                "font_size": 8,
            }
        )
        self.header_format.set_bottom()
        self.header_format.set_top()

        self.title_format = self.workbook.add_format(
            {
                "font": "arial",
                "bold": True,
                "italic": False,
                "text_wrap": True,
                "align": "centre",
                "font_size": 12,
            }
        )
        self.section_heading = self.workbook.add_format(
            {
                "font": "arial",
                "bold": True,
                "italic": True,
                "text_wrap": True,
                "align": "left",
                "font_size": 11,
            }
        )

        self.footer_format = self.workbook.add_format(
            {
                "font": "arial",
                "align": "left",
                "font_size": 8,
            }
        )
        self.footer_format.set_top()

    def set_format(self, color_name):
        """
        Add color codes to the workbook style

        Args:
            color_name (str):  Name of the color to add to this workbook

        Returns:
            str: Cell format with the color code definition assigned to it

        """

        color_code = get_color_code(color_name)

        if color_code is not None:
            # a color code was found. add it as a definition to the work book
            cell_format = self.workbook.add_format({"font_size": 8})
            cell_format.set_font_color(color_code)

        else:
            cell_format = None

        return cell_format


def update_width(label, max_width=None):
    """
    Update the width of the current max_width based on the contents of the label

    Args:
        label (str): Label to check if its width a wider than max_width
        max_width (int or None): Current maximum width

    Returns:
        int: Maximum width encountered so far
    """

    width = len(label)
    if max_width is None or width > max_width:
        max_width = width
    return max_width


def get_max_width(input_data, name, column_index=None):
    """
    Determine the maximum string in an index or column of a Dataframe

    Args:
        input_data (DataFrame):  The dataframe to check
        name (str): Name of the column to check
        column_index (int or None): Index of the column to check

    Returns:
        int: The maximum width of this column or index

    """
    max_col_width = len(name)
    if column_index is None:
        # get the values of the column based on the name of the column
        values = input_data[name]
    else:
        # get the values of the column based on the index of the column
        values = input_data.iloc[:, column_index]
    for value in values:
        col_width = len(str(value))
        if col_width > max_col_width:
            max_col_width = col_width

    return max_col_width


def find_color_name(line: str, minimal_color_length=2):
    """
    Find the color name of a str

    Args:
        line (str): Line in which to find the color name
        minimal_color_length (int): Minimum color length

    Returns:
        str: The color found int the line

    """
    found_color = None
    default_colors = get_color_names(min_color_length=minimal_color_length)
    for color_name in default_colors:
        if line.startswith(color_name):
            found_color = color_name
            break
    return found_color


def write_data_to_sheet_multiindex(
    data_df: DataFrame, file_name: str | Path, sheet_name="Sheet"
):
    """
    Write the data to Excel file with format

     Args:
         data_df (DataFrame): The dataframe to write to Excel
         file_name (str): Name of the Excel file with format
         sheet_name (str): Name of the sheet to write to

    """

    with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:

        data_df.to_excel(excel_writer=writer, sheet_name=sheet_name)

        ExcelFormatter.header_style = None

        workbook = writer.book
        worksheet = writer.sheets[sheet_name]

        wb = WorkBook(workbook=workbook)

        # we now just reset the index such that we loop over column only
        data_df.reset_index(inplace=True, allow_duplicates=True)

        character_width = 1
        start_row = 0

        for col_idx, column_name in enumerate(data_df.columns):
            col_width = get_max_width(input_data=data_df, name=column_name, column_index=col_idx)
            _logger.info(f"Adjusting {column_name}/{col_idx} with width {col_width}")
            align = wb.left_align
            worksheet.set_column(
                col_idx, col_idx, col_width * character_width, cell_format=align
            )
            worksheet.write(start_row, col_idx, column_name, wb.header_format)

            for idx, value in enumerate(data_df[column_name]):
                found_color_name = find_color_name(value)
                if found_color_name is not None:
                    _logger.debug(f"Going to set {value} {found_color_name}")
                    cell_format = wb.set_format(found_color_name)
                    new_value = value.replace(found_color_name, "")
                    if cell_format is not None:
                        worksheet.write(idx + 1, col_idx, new_value, cell_format)
                    else:
                        _logger.debug("No color found")
                        worksheet.write(idx + 1, col_idx, new_value)

    _logger.debug("Done")
