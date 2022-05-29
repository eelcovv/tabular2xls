import logging
import re
import pandas as pd
from pandas.io.formats.excel import ExcelFormatter
import cbsplotlib.colors as cbc
import matplotlib.colors as mlc

_logger = logging.getLogger(__name__)

CBS_COLORS = [c.replace("cbs:", "") for c in cbc.CBS_COLORS.keys()]
MTL_COLORS = [c.replace("xkcd:", "") for c in mlc.get_named_colors_mapping().keys()]
MIN_COLOR_LENGTH = 2
# neem alleen de kleurennamen met minimaal 3 characters
ALL_COLORS = [c for c in CBS_COLORS + MTL_COLORS if len(c) > MIN_COLOR_LENGTH]


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


def parse_tabular(input_filename, multi_index=False, search_and_replace=None):
    """
    read the tabular file and convert contents to a data frame

    Parameters
    ----------
    input_filename: str or Path
        Name of the tex tabular file
    multi_index: bool
        Converteer de index in een multi index op basis van de eerste 2 kolommen
    search_and_replace:
        dict met search and replace strings

    Returns
    -------
    tabular_df: pd.DataFrame
        Dataframe of the tabular
    """

    _logger.debug(f"Reading file {input_filename}")
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
    if multi_index:
        if header_row[0] == "":
            header_row[0] = "l1"
        if header_row[1] == "":
            header_row[1] = "l2"
        table_df = pd.DataFrame.from_records(rows, columns=header_row)
        table_df.set_index(["l1", "l2"], drop=True, inplace=True)
        table_df.index = table_df.index.rename(["", ""])
    else:
        table_df = pd.DataFrame.from_records(rows, columns=header_row)
        table_df.set_index(first_col, drop=True, inplace=True)

    for alias, pattern in aliases.items():
        for col_name in table_df.columns:
            try:
                alias_exact = "^" + alias + "$"
                table_df[col_name] = table_df[col_name].str.replace(alias_exact, pattern,
                                                                    regex=True)
            except AttributeError:
                pass

    if search_and_replace is not None:
        for search, replace in search_and_replace.items():
            table_df.replace(search, replace, regex=True, inplace=True)

    return table_df


class WorkBook:
    def __init__(self, workbook):
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
        self.left_align_helvetica = self.workbook.add_format({
            'font': "helvetica",
            'align': 'left',
            'font_size': 8,
            'border': 0
        })
        self.left_align_helvetica_bold = self.workbook.add_format({
            'font': "helvetica",
            'bold': True,
            'align': 'left',
            'font_size': 8,
            'border': 0
        })
        self.left_align_italic = self.workbook.add_format({
            'font': "arial",
            'italic': True,
            'align': 'left',
            'font_size': 8,
            'border': 0
        })
        self.left_align_italic_large = self.workbook.add_format({
            'font': "arial",
            'italic': True,
            'align': 'left',
            'font_size': 10,
            'border': 0
        })
        self.left_align_italic_large_ul = self.workbook.add_format({
            'font': "arial",
            'italic': True,
            'align': 'left',
            'underline': True,
            'font_size': 10,
            'border': 0
        })
        self.left_align_bold = self.workbook.add_format({
            'font': "arial",
            'bold': True,
            'align': 'left',
            'font_size': 8,
            'border': 0
        })
        self.left_align_bold_large = self.workbook.add_format({
            'font': "arial",
            'bold': True,
            'align': 'left',
            'font_size': 10,
            'border': 0
        })
        self.left_align_bold_larger = self.workbook.add_format({
            'font': "arial",
            'bold': True,
            'align': 'left',
            'font_size': 12,
            'border': 0
        })
        self.left_align = self.workbook.add_format({
            'font': "arial",
            'align': 'left',
            'font_size': 8,
            'border': 0
        })
        self.left_align_large_wrap = self.workbook.add_format({
            'font': "arial",
            'align': 'left',
            'text_wrap': True,
            'font_size': 10,
            'border': 0
        })
        self.left_align_large_wrap_top = self.workbook.add_format({
            'font': "arial",
            'align': 'left',
            'valign': 'top',
            'text_wrap': True,
            'font_size': 10,
            'border': 0
        })
        self.left_align_large = self.workbook.add_format({
            'font': "arial",
            'align': 'left',
            'font_size': 10,
            'border': 0
        })
        self.right_align = self.workbook.add_format({
            'font': "arial",
            'align': 'right',
            'font_size': 8,
            'border': 0
        })
        self.header_format = self.workbook.add_format({
            'font': "arial",
            'bold': True,
            'italic': True,
            'text_wrap': True,
            'align': 'left',
            'font_size': 8,
        })
        self.header_format.set_bottom()
        self.header_format.set_top()

        self.title_format = self.workbook.add_format({
            'font': "arial",
            'bold': True,
            'italic': False,
            'text_wrap': True,
            'align': 'centre',
            'font_size': 12,
        })
        self.section_heading = self.workbook.add_format({
            'font': "arial",
            'bold': True,
            'italic': True,
            'text_wrap': True,
            'align': 'left',
            'font_size': 11,
        })

        self.footer_format = self.workbook.add_format({
            'font': "arial",
            'align': 'left',
            'font_size': 8,
        })
        self.footer_format.set_top()

    def set_format(self, color_name):

        color_code = None
        try:
            color_code = cbc.CBS_COLORS_HEX[color_name]
        except KeyError:
            try:
                color_code = cbc.CBS_COLORS_HEX["cbs:" + color_name]
            except KeyError:
                try:
                    color_code = mlc.get_named_colors_mapping()[color_name]
                except KeyError:
                    _logger.warning(f"kleur {color_name} niet gevonden")

        if color_code is not None:
            cell_format = self.workbook.add_format({'font_size': 8})
            cell_format.set_font_color(color_code)

        else:
            cell_format = None

        return cell_format


def update_width(label, max_width):
    width = len(label)
    if width > max_width:
        max_width = width
    return max_width


def get_max_width(data_frame, name, index=False):
    """ bepaal de maximale string in een index of column """
    max_col_width = len(name)
    if index:
        values = data_frame.index.get_level_values(name)
    else:
        values = data_frame[name]
    for value in values:
        col_width = len(str(value))
        if col_width > max_col_width:
            max_col_width = col_width

    return max_col_width


def find_color_name(value: str):
    found_color = None
    for color_name in ALL_COLORS:
        if value.startswith(color_name):
            found_color = color_name
            break
    return found_color


def write_data_to_sheet_multiindex(data_df, file_name, sheet_name="Sheet"):
    """
    Schrijf de data naar excel file met format

    Parameters
    ----------
    data_df: pd.DataFrame
        De data die we naar excel scrhijven
    file_name: str
    sheet_name: str
        De sheet name

    """

    writer = pd.ExcelWriter(file_name, engine="xlsxwriter")

    data_df.to_excel(excel_writer=writer, sheet_name=sheet_name)

    ExcelFormatter.header_style = None

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]

    wb = WorkBook(workbook=workbook)

    n_index = 0
    max_width = 0
    character_width = 1
    start_row = 0

    for col_idx, index_name in enumerate(data_df.index.names):
        col_width = get_max_width(data_frame=data_df, name=index_name, index=True)
        _logger.info(f"Adjusting {index_name}/{col_idx} with width {col_width}")
        align = wb.left_align
        worksheet.set_column(col_idx, col_idx, col_width * character_width, cell_format=align)
        worksheet.write(start_row, col_idx, index_name, wb.header_format)

        for value in data_df.index.get_level_values(index_name):
            found_color_name = find_color_name(value)
            if found_color_name is not None:
                _logger.info(f"Going to set {value} {found_color_name}")

        n_index += 1

    for col_idx, column_name in enumerate(data_df.columns):
        col_width = get_max_width(data_frame=data_df, name=column_name, index=False)
        _logger.info(f"Adjusting {column_name}/{col_idx} with width {col_width}")
        align = wb.left_align
        col_idx2 = col_idx + n_index
        worksheet.set_column(col_idx2, col_idx2, col_width * character_width, cell_format=align)
        worksheet.write(start_row, col_idx2, column_name, wb.header_format)

        for idx, value in enumerate(data_df[column_name]):
            found_color_name = find_color_name(value)
            if found_color_name is not None:
                _logger.info(f"Going to set {value} {found_color_name}")
                cell_format = wb.set_format(found_color_name)
                new_value = value.replace(found_color_name, "")
                if cell_format is not None:
                    worksheet.write(idx + 1, col_idx2, new_value, cell_format)
                else:
                    _logger
                    worksheet.write(idx + 1, col_idx2, new_value)

    writer.save()
    _logger.info("Done")
